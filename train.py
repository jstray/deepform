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
import re
import pdfplumber
from decimal import Decimal

import wandb
from wandb.keras import WandbCallback

run = wandb.init()
config = run.config
config.epochs = 25

# Thanks, StackOverflow. This "undoes" a 1D convolution, by combining upsampling plus convolution.
def Conv1DTranspose(input_tensor, filters, kernel_size, strides=2, padding='same'):
		x = Lambda(lambda x: expand_dims(x, axis=2))(input_tensor)
		x = Conv2DTranspose(filters=filters, kernel_size=(kernel_size, 1), strides=(strides, 1), padding=padding)(x)
		x = Lambda(lambda x: squeeze(x, axis=2))(x)
		return x

# Configuration
max_doc_length = 4096
vocab_size = 5000
target_thresh = 0.9
augment_dims = 4 # number of features per token, other then token type

wandb.log({'algorithm':'U-net with position'})

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


# --- additional features ----
def is_dollar_amount(s):
	return re.search(r'\$?\d[\d,]+(\.\d\d)?',s) != None

def augment_row(row):
	return [ row['page'], row['x0'], row['y0'], is_dollar_amount(row['token'])]
	

# --- Create training data ---
print('Loading training data...')
docs = []
labels = []
augment = []
for docrows in input_docs():	
	# reconstruct document text (will be tokenized again below, huh)
	docs.append(' '.join([row['token'] for row in docrows]))
	
	# threshold fuzzy matching score with our target field, to get binary labels 
	labels.append([(0 if float(row['gross_amount']) < target_thresh else 1) for row in docrows])
	
	augment.append([augment_row(r) for row in docrows])

print(f'Loaded {len(docs)}')
max_length = max([len(x) for x in labels])
print(f'Max document size {max_length}')
avg_length = sum([len(x) for x in labels])/len(labels)
print(f'Average document size {avg_length}')

# integer encode the documents, truncate to max_doc_length
encoded_docs = [one_hot(d, vocab_size) for d in docs]
x = pad_sequences(encoded_docs, maxlen=max_doc_length, padding='post', truncating='post')
print(f'x.shape: {x.shape}')

# Truncate to max_doc_length
y = pad_sequences(labels, maxlen=max_doc_length, padding='post', truncating='post')

# additional features
#a = pad_sequences(augment, maxlen=max_doc_length, padding='post', truncating='post'))

# --- Specify network ---

# We use a U-net to handle long range dependencies between tokens 
indata = Input((max_doc_length, augment_dims+1))
tok_word = Lambda( lambda x: slice(x, 0, 1))(indata)
tok_feature = Lambda( lambda x: slice(x, 1, -1))(indata)
embed = Embedding(vocab_size, 32)(tok_word)

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
#print(model.summary())


# --- Go! ----

model.fit(
		x=x,
		y=y,
		epochs=10,
		validation_split=0.2,
		callbacks=[WandbCallback()])

# --- Log output PDF images ---

# convert a single row of document data (one token) to bbox format needed for drawing
def docrow_to_bbox(t):
	return [Decimal(t['x0']), Decimal(t['y0']), Decimal(t['x1']), Decimal(t['y1'])] 
	
cnt=0
for doc_idx,doc_rows in enumerate(input_docs()):
	slug = doc_rows[0]['slug']
	doc_rows = doc_rows[:max_doc_length]
	fname = 'pdfs/' + slug + '.pdf'
	try:
		pdf = pdfplumber.open(fname)
	except Exception as e:
		# If the file's not there, that's fine -- we use available PDFs to define what to see
		continue

	print('Rendering output for ' +  fname)

	# Get the correct answers: find the indices of the token(s) labelled 1
	target_idx = [idx for (idx,val) in enumerate(y[doc_idx]) if val==1]
			
	# Draw the machine output: get a score for each token
	z = np.array([x[doc_idx]])
	predict = model.predict(z)
	
	if cnt==0:
		print('--- predict ---')
		print(predict)
		cnt+=1
		
	predict = predict.squeeze(axis=0)
	
	page_images=[]
	for pagenum,page in enumerate(pdf.pages):
		im = page.to_image(resolution=300)
		current_page = str(pagenum/float(len(pdf.pages)-1)) # training data has 0..1 for page range
		
		# Draw target tokens
		target_toks = [doc_rows[i] for i in target_idx if doc_rows[i]['page']==current_page]
		rects = [ docrow_to_bbox(t) for t in target_toks]
		im.draw_rects(rects, stroke='blue', stroke_width=3, fill=None)
		
		# Draw guesses
		for idx,tok in enumerate(doc_rows):
			if predict[idx]>0.1 and tok['page']==current_page:
				c = int(255*predict[idx])
				im.draw_rect(docrow_to_bbox(tok), 
							 stroke=(255, 255-c, 255-c),
							 fill=None)
				
		page_images.append(wandb.Image(im.annotated, caption='page ' +  str(pagenum)))
		
	wandb.log({slug: page_images})
		
