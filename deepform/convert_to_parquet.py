"""
Process a CSV of training data to compute features and store them as parquet files.
"""

import argparse
import math
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
from tqdm import tqdm

from deepform.features import add_base_features, fix_dtypes

# Defaults
ROOT_DIR = Path(__file__).absolute().parents[1]
INPUT_CSV = ROOT_DIR / "data" / "training.csv"
PARQUET_PATH = ROOT_DIR / "data" / "parquet"
DOCUMENT_INDEX = PARQUET_PATH.parent / "doc_index.parquet"


def convert_csv_to_parquet(csv_path=INPUT_CSV, pq_path=PARQUET_PATH):

    # Make sure the path to the parquet files actually exists.
    pq_path.mkdir(parents=True, exist_ok=True)

    # Get a list of DataFrames (chunks from the CSV).
    chunks = read_with_progess_bar(csv_path)
    print(f"Got {doc_count(*chunks):,} unique documents")

    print("Removing tokens less than 3 characters long...")
    chunks = [
        df[df["token"].str.len() >= 3].reset_index(drop=True) for df in tqdm(chunks)
    ]
    n_rows = sum(len(df) for df in chunks)
    n_docs = doc_count(*chunks)
    print(f"left with {n_rows:,} rows from {n_docs:,} documents")

    print("Fixing dtypes...")
    for df in tqdm(chunks):
        fix_dtypes(df)

    print("Combining chunks...", end=" ")
    tokens = pd.concat(chunks)
    print("done")

    documents = []
    print(f"Computing features and writing to {pq_path.absolute()}...")
    for slug, group in tqdm(tokens.groupby("slug"), total=n_docs):
        file_path = pq_path / f"{slug}.parquet"
        df = add_base_features(group.drop("slug", axis=1))
        max_score = df["gross_amount"].max()
        df["label"] = np.isclose(df["gross_amount"], max_score)
        df.to_parquet(file_path, compression="lz4", index=False)
        documents.append({"slug": slug, "length": len(df), "best_match": max_score})

    index_path = pq_path.parent / "doc_index.parquet"
    print(f"Writing document index to {index_path.absolute()}...")
    pd.DataFrame(documents).to_parquet(index_path)


def read_with_progess_bar(csv_path, chunksize=4000):
    """Read from a csv while displaying a progress bar, return the chunks."""
    csv_path = Path(csv_path)
    n_chunks = math.ceil(line_count(csv_path) / chunksize)
    df_list = []
    print(f"Reading {csv_path.absolute()}...")
    for df_chunk in tqdm(pd.read_csv(csv_path, chunksize=chunksize), total=n_chunks):
        df_list.append(df_chunk)
    return df_list


def doc_count(*dfs):
    return len(pd.concat(df["slug"] for df in dfs).unique())


def line_count(filepath):
    """Count the number of lines in a file as quickly as possible.
    
    This uses the shell built-in which runs much faster than opening a file in Python.
    The main use of this is to see if a file is too large before opening it, but can
    also be used with tqdm to provide decent progress bars.
    """
    print(f"Checking file size of {filepath}...", end=" ")
    ret = subprocess.run(["wc", "-l", filepath], capture_output=True)
    n = int(ret.stdout.split()[0])
    print(f"counted {n:,} lines")
    return n


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "infile", nargs="?", default=INPUT_CSV, help="csv of training data to convert",
    )
    parser.add_argument(
        "outdir",
        nargs="?",
        default=PARQUET_PATH,
        help="path to destination parquet directory",
    )
    args = parser.parse_args()
    convert_csv_to_parquet(Path(args.infile), Path(args.outdir))
