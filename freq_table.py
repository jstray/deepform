import pandas as pd
import csv

incsv = csv.DictReader(open('../dfold/filings-tokens-2.csv', mode='r'))


tokens = [] 
try:
	for row in incsv:
		if len(row['token']) > 2:
			tokens.append(row['token'])
except Exception:
	pass

s = pd.Series(tokens)
print(s.value_counts())

print(f'There are {len(s.unique())} unique types')