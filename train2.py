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
from decimal import Decimal

import wandb
from wandb.keras import WandbCallback

run = wandb.init()


# Configuration
read_docs = 10000 # how many docs to load, at most
target_thresh = 0.9 # target match scores larger than this will becomes positive labels
window_len = 20 # size of token sequences to train on (and network size!)
vocab_size = 500
token_dims = 5 # number of features per token, including token hash


# Generator that reads all our training data
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

def token_features(row):
	return [ hash(row['token']) % vocab_size,
					 float(row['page']), 
					 float(row['x0']),
					 float(row['y0']), 
					 float(is_dollar_amount(row['token'])) ]
	


# --- Load documents ---
print('Loading training data...')
features = []
labels = []
for doc_tokens in input_docs(max_docs=read_docs):	
	if len(doc_tokens) < window_len:
		continue # TODO pad shorter docs
		
	features.append([token_features(row) for row in doc_tokens])
	
	# threshold fuzzy matching score with our target field, to get binary labels 
	labels.append([(0 if float(row['gross_amount']) < target_thresh else 1) for row in doc_tokens])
	

num_docs = len(features)

print(f'Loaded {num_docs} docs')
max_length = max([len(x) for x in labels])
print(f'Max document size {max_length}')
avg_length = sum([len(x) for x in labels])/len(labels)
print(f'Average document size {avg_length}')

	
# ---- Resample doc_features,labels as windows ----

# returns a window of tokens, labels at a random position in a random document
def one_window_unbalanced():
	global num_docs, features, labels
	doc_idx = random.randint(0,num_docs-1)
	doc_len = len(features[doc_idx])
	tok_idx = random.randint(0, doc_len-window_len)
	return features[doc_idx][tok_idx : tok_idx+window_len], labels[doc_idx][tok_idx : tok_idx+window_len]

# control the fraction of windows that include a positive label. not efficient.
def one_window():
	f,l = one_window_unbalanced()
	if random.randint(0,1):
		while not 1 in l:
			f,l = one_window_unbalanced()
	return f,l

def windowed_generator(batch_size):
	global window_len
	# Create empty arrays to contain batch of features and labels#
	batch_features = np.zeros((batch_size, window_len, token_dims))
	batch_labels = np.zeros((batch_size,window_len))

	while True:
		for i in range(batch_size):
			features,labels = one_window()
			batch_features[i,:,:] = features
			batch_labels[i,:] = labels
		yield batch_features, batch_labels


x_val, y_val = next(windowed_generator(100))

# --- Specify network ---

indata = Input((window_len, token_dims))

# split into the hash and the rest of the token features, embed hash as one-hot, then merge
tok_hash = Lambda( lambda x: squeeze(K.backend.slice(x, (0,0,0), (-1,-1,1)),axis=2))(indata)
tok_features = Lambda( lambda x: K.backend.slice(x, (0,0,1), (-1,-1,-1)))(indata)
embed = Embedding(vocab_size, 32)(tok_hash)
merged = concatenate([embed, tok_features], axis=2)

f = Flatten()(merged)
d1 = Dense(window_len*token_dims*5, activation='sigmoid')(f)
d2 = Dropout(0.3)(d1)
d3 = Dense(window_len*token_dims, activation='sigmoid')(d2)
d4 = Dropout(0.3)(d3)
d5 = Dense(window_len, activation='elu')(d4)

model = Model(inputs=[indata], outputs=[d5])
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['acc'])
print(model.summary())

# --- fit ----

# train the network
model.fit_generator(
	windowed_generator(batch_size=10000),
	validation_data=(x_val, y_val), 
	steps_per_epoch=10,
	epochs=25,
	callbacks=[WandbCallback()])



