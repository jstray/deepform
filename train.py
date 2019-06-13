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
config.token_dims = 7 # number of features per token, including token hash
config.positive_fraction = 0.5
config.target_thresh = 0.9 # target match scores larger than this will becomes positive labels
config.epochs = 50
config.batch_size=10000
config.steps_per_epoch = 10
config.doc_acc_sample_size = 25 # how many documents to check extraction on after each epoch
config.penalize_missed = 10 # much more more a missed 1 counts than a missed 0 in output
config.val_split = 0.2

# ---- Load data and generate features ----

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
	tokstr = row['token'].upper()
	return [ hash(tokstr) % vocab_size,
					 float(row['page']), 
					 float(row['x0']),
					 float(row['y0']), 
					 float(len(tokstr)),
					 float(np.mean([c.isdigit() for c in tokstr])),
					 float(is_dollar_amount(tokstr)) ]
	
# Load raw training data, create our per-token features and binary labels	
def load_training_data_nocache(config):
	slugs = []
	token_text = []
	features = []
	labels = []
	for doc_tokens in input_docs(max_docs=config.read_docs):	
		if len(doc_tokens) < config.window_len:
			continue # TODO pad shorter docs
			
		# Not training data, but used for evaluating results later
		slugs.append(doc_tokens[0]['slug']) # unique document ID, also PDF filename
		token_text.append([row['token'] for row in doc_tokens])

		features.append([token_features(row, config.vocab_size) for row in doc_tokens])
		
		# threshold fuzzy matching score with our target field, to get binary labels 
		labels.append([(0 if float(row['gross_amount']) < config.target_thresh else 1) for row in doc_tokens])

	return slugs, token_text, features, labels
	
# Because generating the list of features is so expensive, we cache it on disk
def load_training_data(config):
	if os.path.isfile('data/cached_features.p'):
		print('Loading training data from cache...')
		slugs, token_text, features,labels = pickle.load(open('data/cached_features.p', 'rb'))
	else:
		print('Loading training data...')
		slugs, token_text, features, labels = load_training_data_nocache(config)
		print('Saving training data to cache...')
		pickle.dump((slugs, token_text, features, labels), open('data/cached_features.p', 'wb'))

	return slugs, token_text, features,labels

	
# ---- Resample features,labels as windows ----

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

# ---- Custom loss function is basically MSE but high penalty for missing a 1 label ---

def missed_token_loss(one_penalty):
   
	def _missed_token_loss(y_true, y_pred):
	  expected_zero = tf.to_float(tf.math.equal(y_true,0))
	  s = y_pred*expected_zero
	  zero_loss = K.backend.mean(K.backend.square(s))
	  expected_one = tf.to_float(tf.math.equal(y_true,1))
	  t = one_penalty*(1-y_pred)*expected_one
	  one_loss = K.backend.mean(K.backend.square(t))
	  return zero_loss + one_loss

	return _missed_token_loss # closes over one_penalty

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
	model.compile(
		optimizer='adam', 
		loss=missed_token_loss(config.penalize_missed), 
		metrics=['acc'])

	return model

# --- Predict ---
# Our network is windowed, so we have to aggregate windows to get a final score

# Returns vector of token scores
def predict_scores(model, features, window_len):
	doc_len = len(features)
	num_windows = doc_len-window_len

	windowed_features = np.array([features[i:i+window_len] for i in range(num_windows)])
	window_scores = model.predict(windowed_features)

	scores = np.zeros(doc_len)
	for i in range(num_windows):
		scores[i:i+window_len] += window_scores[i] # would max work better than sum?
	return scores

# returns text, score of best answer
def predict_answer(model, features, token_text, window_len):
	scores = predict_scores(model, features, window_len)
	best_score_idx = np.argmax(scores)
	best_score_text = token_text[best_score_idx]
	return best_score_text, scores[best_score_idx]

# returns text of correct answer,
def correct_answer(features, labels, token_text):
	answer_idx = np.argmax(labels)
	answer_text = token_text[answer_idx]
	return answer_text

# Calculate accuracy of answer extraction over num_to_test docs, print diagnostics while we do so
def compute_accuracy(model, window_len, slugs, token_text, features, labels, num_to_test):
	acc = 0.0
	for i in range(num_to_test):
		doc_idx = random.randint(0, len(slugs)-1)
		predict_text, predict_score = predict_answer(model, features[doc_idx], token_text[doc_idx], window_len)
		answer_text = correct_answer(features[doc_idx], labels[doc_idx], token_text[doc_idx])
		print(f'{slugs[doc_idx]}: guessed "{predict_text}" with score {predict_score}, correct "{answer_text}"')
		if predict_text==answer_text:
			acc+=1
	return acc/num_to_test


# ---- Custom callback to log document-level accuracy ----

class DocAccCallback(K.callbacks.Callback):
	def __init__(self, window_len, slugs, token_text, features, labels, num_to_test, logname):
		self.window_len = window_len
		self.slugs = slugs
		self.token_text = token_text
		self.features = features
		self.labels = labels
		self.num_to_test = num_to_test
		self.logname = logname

	def on_epoch_end(self, epoch, logs):
		acc = compute_accuracy(self.model,
			self.window_len,
			self.slugs,
			self.token_text,
			self.features,
			self.labels,
			self.num_to_test+epoch)  # test more docs later in training, for more precise acc
		print(f'This epoch {self.logname}: {acc}')
		wandb.log({self.logname:acc})


# --- MAIN ----

print('Configuration:')
print(config)

slugs, token_text, features, labels = load_training_data(config)
print(f'Loaded {len(features)}')
max_length = max([len(x) for x in labels])
print(f'Max document size {max_length}')
avg_length = sum([len(x) for x in labels])/len(labels)
print(f'Average document size {avg_length}')

# split into train and test
slugs_train = []
token_text_train = []
features_train = []
labels_train = []
slugs_val = []
token_text_val = []
features_val = []
labels_val = []
for i in range(len(features)):
	if random.random() < config.val_split:
		slugs_val.append(slugs[i])
		token_text_val.append(token_text[i])
		features_val.append(features[i])
		labels_val.append(labels[i])
	else:
		slugs_train.append(slugs[i])
		token_text_train.append(token_text[i])		
		features_train.append(features[i])
		labels_train.append(labels[i])

print(f'Training on {len(features_train)}, validating on {len(features_val)}')

model = create_model(config)
print(model.summary())


model.fit_generator(
	windowed_generator(features_train, labels_train, config),
	steps_per_epoch=config.steps_per_epoch,
	epochs=config.epochs,
	callbacks=[ 
		WandbCallback(),
		DocAccCallback(	config.window_len, 
										slugs_train, 
										token_text_train, 
										features_train, 
										labels_train, 
										config.doc_acc_sample_size,
										'doc_train_acc'),
		DocAccCallback(	config.window_len, 
										slugs_val, 
										token_text_val, 
										features_val, 
										labels_val, 
										config.doc_acc_sample_size,
										'doc_val_acc')
	])

