# This takes the token file and does a number of things:
# - rejects documents with too few tokens (need OCR) or no ground truth
# - normalizes page numbers in 0..1
# - provides fuzzy matching scores for each token vs ground truth tokens

import pandas as pd
from fuzzywuzzy import fuzz
import csv
import re


# data in filings that we want to find
targets = ['committee','agency','callsign','gross_amount']


filings = pd.read_csv('ftf-all-filings.tsv', sep='\t')

incsv = csv.DictReader(open('filings-tokens-2.csv', mode='r'))

outcols = ['slug','page','x','y','token'] + targets
outcsv = csv.DictWriter(open('training.csv', mode='w'), fieldnames=outcols)
outcsv.writeheader()


# computes fuzzy distance from each token in the series to the target answer for the document
# answer may be multiple tokens, in which case we take the max of matches

def is_dollar_amount(s):
	return re.search(r'\$?\d[\d,]+(\.\d\d)?',s) != None

def target_match_token(anstoks, token):
	if len(anstoks)==1 and is_dollar_amount(anstoks[0]) and is_dollar_amount(token):
		try:
			ans_num = float(anstoks[0].replace('$','').replace(',',''))
			tok_num = float(token.replace('$','').replace(',',''))
			return fuzz.ratio(str(ans_num), str(tok_num))
		except ValueError:
			return fuzz.ratio(anstoks[0], token)  # not a number, maybe a date?

	else:
		return max([fuzz.ratio(x,token) for x in anstoks])/100.0

def target_match(answer, tokens):
	anstoks = str(answer).lower().split(' ')
	return tokens.map(lambda x: target_match_token(anstoks, x.lower()))
	

def process_doc(slug, rows):
	if len(rows) < 10:
		print(f'Skipping {slug} because it has only {len(rows)} tokens') # probably needs OCR
		return

	answers = filings.loc[filings['dc_slug'] == slug]
	if len(answers) != 1:
		print(f'Skipping {slug} because it matches {len(answers)} rows')
		return
	answers = answers.iloc[0]


	df = pd.DataFrame(rows)

	page = pd.to_numeric(df['page'])
	df['page'] = page / page.max()  # last page = 1.0

	for t in targets:
		df[t] = target_match(answers[t], df['token'])

	for index, row in df.iterrows():
		outcsv.writerow(row.to_dict())

	print(f'Processed {slug} with {len(df)} tokens')

# --- Main ---
# Accumulate all rows with the same slug
active_rows = []
active_slug = None

for row in incsv:
	if row['slug'] != active_slug:
		if active_slug:
			process_doc(active_slug, active_rows)
		active_slug = row['slug']
		active_rows = [row]
	else:
		active_rows.append(row)
