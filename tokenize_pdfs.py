# This version outputs a CSV in normal form:
# slug, page, x, y, token
import pandas as pd
import pdfplumber
import csv
import json

d = pd.read_csv('data/ftf-all-filings.tsv', sep='\t')

f = open('data/filings-tokens.csv', mode='w')
csv = csv.writer(f)
csv.writerow(['slug','page','x','y','token'])

for index, row in d.iterrows():
	slug = row['dc_slug']
	fname = 'pdfs/' + slug + '.pdf'
	print('Extracting ' +  fname)

	try:
		pdf = pdfplumber.open(fname)
		for p in range(len(pdf.pages)):
			for w in pdf.pages[p].extract_words():
				csv.writerow([slug, p, float(w['x0']), float(w['top']), w['text']])		

	except Exception as e:
		print(e)
