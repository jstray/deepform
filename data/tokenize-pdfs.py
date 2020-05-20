# This version outputs a CSV in normal form:
# slug, page, x, y, token
import csv

import pandas as pd
import pdfplumber

nopened = 0
nparsed = 0
nopenerror = 0
nparseerror = 0


def print_stats():
    global nopened, nparsed, nopenerror, nparseerror
    print("-----")
    print(f"Found {nopened} files, could not open {nopenerror}")
    print(f"Parsed {nparsed}, could not parse {nparseerror}")
    print("-----")


d = pd.read_csv("../source/ftf-all-filings.tsv", sep="\t")

f = open("filings-tokens.csv", mode="w")
csv = csv.writer(f)
csv.writerow(["slug", "page", "x0", "y0", "x1", "y1", "token"])

for index, row in d.iterrows():
    slug = row["dc_slug"]
    fname = "pdfs/" + slug + ".pdf"
    print("Extracting " + fname)

    try:
        pdf = pdfplumber.open(fname)
        nopened += 1
    except Exception as e:
        print(e)
        nopenerror += 1
        continue

    try:
        for p in range(len(pdf.pages)):
            for w in pdf.pages[p].extract_words():
                # some tokens have nulls in them, which are not valid in a csv
                if "\0" not in w["text"]:
                    csv.writerow(
                        [
                            slug,
                            p,
                            float(w["x0"]),
                            float(w["top"]),
                            float(w["x1"]),
                            float(w["bottom"]),
                            w["text"],
                        ]
                    )
        nparsed += 1
    except Exception as e:
        print(e)
        nparseerror += 1

    if (index % 100) == 0:
        print_stats()


print("-----")
print("Done!")
print(f"{len(d)} rows total")
print_stats()
