#!/bin/usr/python3
# ----------------------------------------------------------
# reads in .ftf file and grabes slug identifier and
# committee names.
#
# ----------------------------------------------------------

import argparse
import os

import pandas as pd


def load_files(filenames):
    """
    Loads data from csv in chunks.
    """
    yield pd.read_csv(filenames)


# Create the parser
argparser = argparse.ArgumentParser(
    description="Combines ftf and training data. Extracts labels for training."
)

# Add arguments
argparser.add_argument("-c", "--csv", type=str, help="path to csv")

argparser.add_argument("-f", "--ftf", type=str, help="path to ftf")


def main(args):
    # Read filenames
    # ftf = pd.read_csv('./ftf-all-filings.tsv', delimiter='\t', encoding='utf-8')
    ftf_file = args.ftf
    ftf = pd.read_csv(ftf_file, delimiter="\t", encoding="utf-8")

    # data_files = './training.csv'
    data_files = args.csv
    data = pd.concat(load_files(data_files))

    # Let's drop NaN if there are any
    data["token"].dropna(inplace=True)

    # Rename column so we can merge
    ftf.rename(columns={"dc_slug": "slug"}, inplace=True)

    # Combine both data sets.
    # Pandas merge will remove those that are not included in both
    # Let's combine this so that we can figure out what our labels are
    merged_data = pd.merge(data, ftf, on="slug")

    # Drop rows with same slug name
    merged_data_unique = merged_data.drop_duplicates(subset="slug")

    # Grab only the slug and committee name columns
    output_dataset = merged_data_unique[["slug", "committee"]]

    # Check we have file directory
    if not os.path.isdir("./processed_data"):
        os.mkdir("./processed_data")

    # Save the slug-committee names as inputid_outputlabel.csv
    output_dataset.to_csv("./processed_data/slug_committee_labels.csv")


if __name__ == "__main__":
    # Exectute parse_args()
    args = argparser.parse_args()
    main(args)
