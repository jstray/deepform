from numpy import array
import keras as K
from keras.engine.input_layer import Input
from keras.models import Model
from keras.layers import Dense, Flatten, Dropout, Lambda, concatenate
from keras.layers.embeddings import Embedding
from keras.backend import expand_dims, squeeze
import tensorflow as tf
import pandas as pd
import numpy as np
import csv
import re
import random
import pdfplumber
import os
import pickle
from decimal import Decimal

import wandb
from wandb.keras import WandbCallback

# Configuration
run = wandb.init()
config = run.config
config.read_docs = 10000 # how many docs to load, at most
config.window_len = 30 # size of token sequences to train on (and network size!)
config.vocab_size = 500
config.token_dims = 5 # number of features per token, including token hash
config.positive_fraction = 0.5
config.target_thresh = 0.9 # target match scores larger than this will becomes positive labels
config.epochs = 50
config.batch_size=10000
config.steps_per_epoch = 10


# Generator that reads raw training data
# For each document, yields an array of dictionaries, each of which is a token
def input_docs(max_docs=None):
	incsv = csv.DictReader(open('data/training.csv', mode='r'))
		
	# Reconstruct documents by concatenating all rows with the same slug
	active_slug = None
	doc_rows = [] 
	num_docs = 0

	for row in incsv:	
		# throw out tokens that are too short, they won't help us
		token = row['token']
		if len(token) < 3:
			continue 

		if row['slug'] != active_slug:
			if active_slug:
				yield doc_rows
				num_docs += 1
				if max_docs and num_docs >= max_docs:
					return
			doc_rows = [row]
			active_slug = row['slug']
		else:
			doc_rows.append(row)
		
	yield doc_rows


def is_dollar_amount(s):
	return re.search(r'\$?\d[\d,]+(\.\d\d)?',s) != None

def token_features(row, vocab_size):
	return [ hash(row['token']) % vocab_size,
					 float(row['page']), 
					 float(row['x0']),
					 float(row['y0']), 
					 float(is_dollar_amount(row['token'])) ]
	
# Load raw training data, create our per-token features and binary labels	
def load_training_data_nocache(config):
	features = []
	labels = []
	for doc_tokens in input_docs(max_docs=config.read_docs):	
		if len(doc_tokens) < config.window_len:
			continue # TODO pad shorter docs
			
		features.append([token_features(row, config.vocab_size) for row in doc_tokens])
		
		# threshold fuzzy matching score with our target field, to get binary labels 
		labels.append([(0 if float(row['gross_amount']) < config.target_thresh else 1) for row in doc_tokens])

	return features, labels
	
# Because generating the list of features is so expensive, we cache it on disk
def load_training_data(config):
	if os.path.isfile('data/cached_features.p'):
		print('Loading training data from cache...')
		features,labels = pickle.load(open('data/cached_features.p', 'rb'))
	else:
		print('Loading training data...')
		features, labels = load_training_data_nocache(config)
		print('Saving training data to cache...')
		pickle.dump((features, labels), open('data/cached_features.p', 'wb'))

	return features,labels


	
# ---- Resample doc_features,labels as windows ----

# returns a window of tokens, labels at a random position in a random document
def one_window_unbalanced(features, labels, window_len):
	doc_idx = random.randint(0,len(features)-1)
	doc_len = len(features[doc_idx])
	tok_idx = random.randint(0, doc_len-window_len)
	return features[doc_idx][tok_idx : tok_idx+window_len], labels[doc_idx][tok_idx : tok_idx+window_len]

# control the fraction of windows that include a positive label. not efficient.
def one_window(features, labels, window_len, positive_fraction):
	f,l = one_window_unbalanced(features, labels, window_len)
	if random.random() > positive_fraction: # mostly positive examples
		while not 1 in l:
			f,l = one_window_unbalanced(features, labels, window_len)
	return f,l

def windowed_generator(features, labels, config):
	# Create empty arrays to contain batch of features and labels#
	batch_features = np.zeros((config.batch_size, config.window_len, config.token_dims))
	batch_labels = np.zeros((config.batch_size, config.window_len))

	while True:
		for i in range(config.batch_size):
			features1,labels1 = one_window(features, labels, config.window_len, config.positive_fraction)
			batch_features[i,:,:] = features1
			batch_labels[i,:] = labels1
		yield batch_features, batch_labels


# --- Specify network ---

def create_model(config):
	indata = Input((config.window_len, config.token_dims))

	# split into the hash and the rest of the token features, embed hash as one-hot, then merge
	tok_hash = Lambda( lambda x: squeeze(K.backend.slice(x, (0,0,0), (-1,-1,1)),axis=2))(indata)
	tok_features = Lambda( lambda x: K.backend.slice(x, (0,0,1), (-1,-1,-1)))(indata)
	embed = Embedding(config.vocab_size, 32)(tok_hash)
	merged = concatenate([embed, tok_features], axis=2)

	f = Flatten()(merged)
	d1 = Dense(config.window_len*config.token_dims*5, activation='sigmoid')(f)
	d2 = Dropout(0.3)(d1)
	d3 = Dense(config.window_len*config.token_dims, activation='sigmoid')(d2)
	d4 = Dropout(0.3)(d3)
	d5 = Dense(config.window_len, activation='elu')(d4)

	model = Model(inputs=[indata], outputs=[d5])
	model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['acc'])

	return model

# --- MAIN ----

print('Configuration:')
print(config)

features, labels = load_training_data(config)
print(f'Loaded {len(features)}')
max_length = max([len(x) for x in labels])
print(f'Max document size {max_length}')
avg_length = sum([len(x) for x in labels])/len(labels)
print(f'Average document size {avg_length}')

model = create_model(config)
print(model.summary())

# validation on same data for now, not so good
x_val, y_val = next(windowed_generator(features, labels, config)) 

model.fit_generator(
	windowed_generator(features, labels, config),
	validation_data=(x_val, y_val), 
	steps_per_epoch=config.steps_per_epoch,
	epochs=config.epochs,
	callbacks=[WandbCallback()])




