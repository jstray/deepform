#!/bin/usr/python3
# ----------------------------------------------------------
# Reads instances and labels, splits into training and
# test set.
# ToDo:
# arparse; command-line option split ratio
#
# ----------------------------------------------------------

import os

import pandas as pd


def load_files(filenames):
    yield pd.read_csv(filenames)


def main():
    # Read in data
    data_file = "./processed_data/processed_data_instances.csv"
    committee_file = "./processed_data/slug_committee_labels.csv"

    # Training and test set split ratio
    split_ratio = 0.80

    # slugs and processed tokens
    data_df = pd.concat(load_files(data_file))
    data_df = data_df.drop(
        columns="token"
    )  # Remove unwanted column (token is redundant)
    data_df["processed"] = data_df["processed"].astype(
        str
    )  # Make sure we are dealing with strings

    # committee info
    committee_df = pd.read_csv(committee_file)
    committee_df.drop(columns="Unnamed: 0", inplace=True)  # Remove unwanted column
    committee_df["committee"] = committee_df[
        "committee"
    ].str.lower()  # Lower case committee names

    # Merge both .csv (now DataFrames) into one
    df = pd.merge(data_df, committee_df, on="slug")

    # Group together based on slug and committee
    df = (
        df.groupby(["slug", "committee"])["processed"]
        .apply(lambda a: " ".join([str(x) for x in a]))
        .reset_index()
    )

    # # Define size of train set
    train_size = int(split_ratio * len(df))

    # Split dataset
    train_set = df[:train_size]
    test_set = df[train_size:]

    # Check path directory exists
    if not os.path.isdir("./test_data"):
        os.mkdir("./test_data")

    if not os.path.isdir("./training_data"):
        os.mkdir("./training_data")

    # Save .csv files
    train_set.to_csv("./training_data/train.csv")
    test_set.to_csv("./test_data/test.csv")


if __name__ == "__main__":
    main()
