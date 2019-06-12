# Manual extraction by looking for h/v aligned tokens after a template match
# Baseline accuracy for this problem

import numpy as np
import csv
import re
from fuzzywuzzy import fuzz

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



def tok_geo(tok):
	return float(tok['x0']), float(tok['y0']), float(tok['page'])

def is_dollar_amount(s):
	return re.search(r'\$?\d[\d,]+(\.\d\d)?',s) != None

# Is this a word that appears next to the total we are looking for?
def is_total_marker(tokstr):
	markers = [
		'TOTAL',
		'AMOUNT',
		'AMT',
		'GROSS',
		'TOTALS',
		'CHARGES'
	]

	ustr = tokstr.upper()
	ratios = [fuzz.ratio(ustr, m) for m in markers]

	return max(ratios) > 90


align_thresh = 0.5 # how far can x or y be from marker to count as aligned?
def guess_doc_answer(doc_tokens):
	numtoks = len(doc_tokens)
	# loop over tokens
	for idx,tok in enumerate(doc_tokens):
		tokstr = tok['token']
		if is_total_marker(tokstr):

			h_marker, v_marker, p_marker = tok_geo(tok) 

			# loop over all following tokens
			for i in range(idx, numtoks):
				tok2 = doc_tokens[i]
				tok2str = tok2['token']

				if not is_dollar_amount(tok2str):
					continue # must be a dollar amount

				h,v,p = tok_geo(tok2)

				if p != p_marker:
					continue # must be on the same page 

#				print(f'Comparing marker {tokstr} at {h_marker},{v_marker} to {tok2str} at {h},{v}')
				# if it's more-or-less aligned horizontally (below) or vertically (to the right), guess it
				if (abs(h-h_marker) < align_thresh) or (abs(v-v_marker) < align_thresh):
					return tok2str


# Correct answer is the token with the highest "gross_amount" score
def correct_answer(doc_tokens):
	i = np.argmax([float(t['gross_amount']) for t in doc_tokens])
	return doc_tokens[i]['token']


# loop over docs
num_docs = 0.0
correct_guesses = 0.0

for doc_tokens in input_docs(max_docs=1000):	
	guess = guess_doc_answer(doc_tokens)
	correct = correct_answer(doc_tokens)
	print(f"{doc_tokens[0]['slug']}: guessed {guess} correct {correct}")
	if guess == correct:
		correct_guesses += 1
	num_docs +=1

print(f'{correct_guesses} correct out of {num_docs}')
print(f'Accuracy: {correct_guesses/num_docs}')


