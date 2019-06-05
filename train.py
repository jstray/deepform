from numpy import array
from keras.preprocessing.text import one_hot
from keras.preprocessing.sequence import pad_sequences
from keras.engine.input_layer import Input
from keras.layers import Dense, Flatten, Conv1D, MaxPooling1D, Lambda, Conv2DTranspose, concatenate
from keras.layers.embeddings import Embedding
from keras.models import Model
from keras.backend import expand_dims, squeeze
import pandas as pd
import numpy as np
import csv


# Thanks, StackOverflow
def Conv1DTranspose(input_tensor, filters, kernel_size, strides=2, padding='same'):
    x = Lambda(lambda x: expand_dims(x, axis=2))(input_tensor)
    x = Conv2DTranspose(filters=filters, kernel_size=(kernel_size, 1), strides=(strides, 1), padding=padding)(x)
    x = Lambda(lambda x: squeeze(x, axis=2))(x)
    return x

# Configuration
max_doc_length = 4096
vocab_size = 5000

incsv = csv.DictReader(open('data/training.csv', mode='r'))


# input and labels
docs = []
targets = []

# Reconstruct documents by concatenating all rows with the same slug
active_slug = None
tokens = [] 
target = []
for row in incsv:
	if len(targets) == 1000:
		break

	token = row['token']
	if len(token) < 3:
		continue 

	if row['slug'] != active_slug:
		if active_slug:
			docs.append(' '.join(tokens))
			targets.append(target)
		active_slug = row['slug']
		tokens = [row['token']]
		target = [0 if float(row['gross_amount']) < 0.9 else 1]
	else:
		tokens.append(row['token'])
		target.append(0 if float(row['gross_amount']) < 0.9 else 1)

max_length = max([len(x) for x in targets])
print(f'Max document size {max_length}')

# Truncate to max_doc_length and turn into np array
#y = np.array([row + [0]*(max_length-len(row)) for row in targets])
y = pad_sequences(targets, maxlen=max_doc_length, padding='post', truncating='post')
print(y[1:10,])

# integer encode the documents
encoded_docs = [one_hot(d, vocab_size) for d in docs]

# pad documents to longest length
padded_docs = pad_sequences(encoded_docs, maxlen=max_doc_length, padding='post', truncating='post')


# We use a U-net to handle long range dependencies between tokens 
indata = Input((max_doc_length,))
embed = Embedding(vocab_size, 32)(indata)
c1 = Conv1D(filters=8, kernel_size=5, padding='same')(embed)  # 4096
p1 = MaxPooling1D()(c1)
c2 = Conv1D(filters=16, kernel_size=5, padding='same')(p1) # 2048
p2 = MaxPooling1D()(c2)
c3 = Conv1D(filters=32, kernel_size=5, padding='same')(p2) # 1024
p3 = MaxPooling1D()(c3)
c4 = Conv1D(filters=64, kernel_size=5, padding='same')(p3) # 512
p4 = MaxPooling1D()(c4) # 256

c5 = Conv1D(filters=64, kernel_size=5, padding='same')(p4) # 256

c6 = Conv1DTranspose(c5, filters=64, kernel_size=5, padding='same') # 512
u6 = concatenate([c4,c6], axis=2) # 512 x 128

c7 = Conv1DTranspose(u6, filters=32, kernel_size=5, padding='same') # 1024
u7 = concatenate([c3,c7], axis=2) # 1024 x 64

c8 = Conv1DTranspose(u7, filters=16, kernel_size=5, padding='same') # 2048
u8 = concatenate([c2,c8], axis=2) # 2048 x 32

c9 = Conv1DTranspose(u8, filters=8, kernel_size=5, padding='same') # 4096
u9 = concatenate([c1,c9], axis=2) # 4096 x 16

# This last convolution produces the target token scores
c10 = Conv1D(filters=1, kernel_size=10, padding='same', activation='relu')(c9)  # 4096 x 1
f = Flatten()(c10)

model = Model(inputs=[indata], outputs=[f])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['acc'])
print(model.summary())

# # fit the model
model.fit(padded_docs, y, epochs=50, verbose=0)
# # evaluate the model
loss, accuracy = model.evaluate(padded_docs, y, verbose=0)
print('Accuracy: %f' % (accuracy*100))
