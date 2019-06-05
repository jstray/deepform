import pandas as pd
import os

d = pd.read_csv('ftf-all-filings.tsv', sep='\t')

for slug in d['dc_slug']:
	fname = slug + '.pdf'
	if not os.path.isfile('pdfs/'+fname):
			print('downloading ' + fname)
			url = 'https://documentcloud.org/documents/' + fname
			# L = follow redirects, f = fail with no output if not 200 (e.g. 404)
			os.system('curl -L -f ' + url + ' > pdfs/' + fname)
	else:
		print('skipping' + fname)
