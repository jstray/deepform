# This takes the token file and does a number of things:
# - rejects documents with too few tokens (need OCR) or no ground truth
# - normalizes page numbers in 0..1
# - provides fuzzy matching scores for each token vs ground truth tokens

import csv
import decimal
import re
from decimal import Decimal

import pandas as pd
from fuzzywuzzy import fuzz

output_docs = 0

# Data in filings that we want to find.
# We output a column for each one of these, indicating how close the token is to the correct answer
# For our first experiment, just extract gross_amount
# Other possible targets include 'committee','agency','callsign'
targets = ["gross_amount"]

filings = pd.read_csv("source/ftf-all-filings.tsv", sep="\t")

incsv = csv.DictReader(open("data/filings-tokens.csv", mode="r"))

outcols = ["slug", "page", "x0", "y0", "x1", "y1", "token"] + targets
outcsv = csv.DictWriter(open("data/training.csv", mode="w"), fieldnames=outcols)
outcsv.writeheader()


# computes fuzzy distance from each token in the series to the target answer for the document
# answer may be multiple tokens, in which case we take the max of matches


def is_dollar_amount(s):
    return re.search(r"\$?\d[\d,]+(\.\d\d)?", s) is not None


# take a string like "$56,333.1" and remove punct, round to two decimals,
# return string


def normalize_dollars(s):
    return str(round(Decimal(s.replace("$", "").replace(",", "")), 2))


def target_match_token(anstoks, token):
    if len(anstoks) == 1 and is_dollar_amount(anstoks[0]) and is_dollar_amount(token):
        try:
            return (
                fuzz.ratio(normalize_dollars(anstoks[0]), normalize_dollars(token))
                / 100.0
            )
        except decimal.InvalidOperation:
            # not a number, maybe a date?
            return fuzz.ratio(anstoks[0], token) / 100.0

    else:
        return max([fuzz.ratio(x, token) for x in anstoks]) / 100.0


def target_match(answer, tokens):
    anstoks = str(answer).lower().split(" ")
    return tokens.map(lambda x: target_match_token(anstoks, x.lower()))


def process_doc(slug, rows):
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
        df[t] = target_match(answers[t], df["token"])

    for index, row in df.iterrows():
        outcsv.writerow(row.to_dict())

    print(f"Processed {slug} with {len(df)} tokens")
    output_docs += 1


# --- Main ---
# Accumulate all rows with the same slug
active_rows = []
active_slug = None
input_docs = 0
for row in incsv:
    if row["slug"] != active_slug:
        if active_slug:
            process_doc(active_slug, active_rows)
            input_docs += 1
        active_slug = row["slug"]
        active_rows = [row]
    else:
        active_rows.append(row)

print(f"Input documents {input_docs}")
print(f"Output documents {output_docs}")
