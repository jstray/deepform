# This takes the token file and does a number of things:
# - rejects documents with too few tokens (need OCR) or no ground truth
# - normalizes page numbers in 0..1
# - provides fuzzy matching scores for each token vs ground truth tokens

import csv
import decimal
import numpy as np

import pandas as pd
from fuzzywuzzy import fuzz

from util import is_dollar_amount, normalize_dollars

output_docs = 0

# Data in filings that we want to find.
# We output a column for each one of these, indicating how close the token is to the correct answer
# For our first experiment, just extract gross_amount
# Other possible targets include 'committee','agency','callsign'
targets = ["gross_amount", "contract_number"] ###Add additional targets

filings = pd.read_csv("../source/ftf-all-filings.tsv", sep="\t")

incsv = csv.DictReader(open("filings-tokens.csv", mode="r"))

outcols = ["slug", "page", "x0", "y0", "x1", "y1", "token"] + targets
outcsv = csv.DictWriter(open("training.csv", mode="w"), fieldnames=outcols)
outcsv.writeheader()


# computes fuzzy distance from each token in the series to the target answer for the document
# answer may be multiple tokens, in which case we take the max of matches

def target_match(answer, tokens, target, max_n): 
    anstok = str(answer).lower().replace(" ", "") # Remove spaces and make the answer lower case
    tokens = [token.lower() for token in tokens] # lowercase all the tokens also
    
    if target == "gross_amount":
        max_n = 1
        for token in tokens:
            if is_dollar_amount(anstok) and is_dollar_amount(token): 
                try: 
                    ratioslist.append(
                        fuzz.ratio(normalize_dollars(anstok), normalize_dollars(token))
                        / 100.0
                    )
                except decimal.InvalidOperation:
                    # not a number, maybe a date?
                    ratioslist.append(fuzz.ratio(anstok, token) / 100.0)
            else: 
                ratioslist.append([fuzz.ratio(x, token) anstok] / 100.0)

    elif target == "contract_number":

        best_match = np.zeroes(max_n)
        #best_idx = np.zeroes(max_n)
        ratioslist = np.zeroes(max_n, len(tokens))          # two dimensional because we will have one array for each possible n-gram length
        for i in range (1, max_n):                          # For each possible number of tokens in answertoken
           for idx in range (0, len(tokens) - i):           #for each n-gram of that length in the doc
               token_string = tokens[idx:idx+i].join('')    # make it one token so we can compare
               match = fuzz.ratio(anstok, token_string) / 100.0 # compare and store the float in match
               ratiolist[i-1, idx] = match                  # update the ratiolist matrix with this match value for the n-gram length and index
               if match > best_match[i]:                    # update our vector of best matches for each n-gram
                   best_match[i-1] = match 
                   #best_idx[i-1] = idx
        ratioslist = ratioslist[np.argmax(best_match),:]    #Ratiolist is all the values in the column which corresponds to the 
    
    return ratioslist 

def process_doc(slug, rows, max_n):
    global output_docs
    if len(rows) < 10:
        # probably needs OCR
        print(f"Skipping {slug} because it has only {len(rows)} tokens")
        return

    answers = filings.loc[filings["dc_slug"] == slug]
    if len(answers) != 1:
        print(f"Skipping {slug} because it matches {len(answers)} rows")
        return
    answers = answers.iloc[0]

    if answers[targets].isnull().any():
        print(
            f"Skipping {slug} because it is missing answers for {[t for t in targets if pd.isnull(answers[t])]}"
        )
        return

    df = pd.DataFrame(rows)

    page = pd.to_numeric(df["page"])
    maxpage = page.max()
    if maxpage:  # avoid div/0 for one page docs
        df["page"] = page / maxpage  # last page = 1.0

    for t in targets:
        df[t] = target_match(answers[t], df["token"], t, max_n) # The value of the answer and an array of the tokens for that slug

    for _, row in df.iterrows():
        outcsv.writerow(row.to_dict())

    print(f"Processed {slug} with {len(df)} tokens")
    output_docs += 1


# --- Main ---
# Accumulate all rows with the same slug
active_rows = []
active_slug = None
input_docs = 0
max_n = 5
   for row in incsv:
    if row["slug"] != active_slug:
        if active_slug:
            process_doc(active_slug, active_rows, max_n)
            input_docs += 1
        active_slug = row["slug"]
        active_rows = [row]
    else:
        active_rows.append(row)

print(f"Input documents {input_docs}")
print(f"Output documents {output_docs}")
