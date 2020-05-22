"""
Process a CSV of training data to compute features and store them as parquet files.
"""

import argparse
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from features import add_base_features

# Defaults
ROOT_DIR = Path(__file__).absolute().parent
INPUT_CSV = ROOT_DIR / "source" / "training.csv"
PARQUET_PATH = ROOT_DIR / "source" / "parquet"


def convert_csv_to_parquet(csv_path=INPUT_CSV, pq_path=PARQUET_PATH):
    print(f"Reading {csv_path}...", end=" ")
    tokens = pd.read_csv(csv_path)
    num_docs = len(tokens["slug"].unique())
    print(f"got {len(tokens):n} rows from {num_docs:n} documents")

    print("Removing tokens less than 3 characters long...", end=" ")
    tokens = tokens[tokens["token"].str.len() >= 3].reset_index(drop=True)
    num_docs = len(tokens["slug"].unique())
    print(f"left with {len(tokens):n} rows from {num_docs:n} documents")

    print("Fixing dtypes...", end=" ")
    fix_dtypes(tokens)
    print("done")

    # Make sure the path to the parquet files actually exists.
    PARQUET_PATH.mkdir(parents=True, exist_ok=True)

    print(f"Computing features and writing to {pq_path}...")
    for slug, group in tqdm(tokens.groupby("slug"), total=num_docs):
        file_path = PARQUET_PATH / f"{slug}.parquet"
        add_base_features(group).to_parquet(file_path, compression="lz4", index=False)


def fix_dtypes(df):
    # Use new-style Pandas string types.
    df[["slug", "token"]] = df[["slug", "token"]].astype("string")

    # Downcast 64-bit floats to 32 bits to save space.
    for col in ["page", "x0", "y0", "x1", "y1", "gross_amount"]:
        df[col] = pd.to_numeric(df[col], downcast="float")


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
    convert_csv_to_parquet(args.infile, args.outdir)
