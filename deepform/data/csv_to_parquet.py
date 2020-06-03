"""
Convert a CSV of training data into typed, deduped parquet file.

Except for type coercion and deduplication, this script leaves all tokens intact and
in order; it doesn't perform any filtering or feature engineering.
"""

import argparse
import logging
from pathlib import Path

import dask.dataframe as dd
from dask.diagnostics import ProgressBar
from deepform.common import DATA_DIR
from humanize import naturalsize

# Defaults
INPUT_CSV = DATA_DIR / "training.csv"
OUTPUT_PQ = DATA_DIR / "training.parquet"


CSV_COL_TYPES = {
    "slug": "category",
    "page": "f4",  # 32-bit float.
    "x0": "f4",
    "y0": "f4",
    "x1": "f4",
    "y1": "f4",
    "token": "string",  # Pandas 1.x string type.
    "gross_amount": "f4",
}


def csv_to_parquet(csv_file, pq_file):
    csv_file, pq_file = Path(csv_file).resolve(), Path(pq_file).resolve()

    logging.debug(f"Reading {csv_file}")
    df = dd.read_csv(csv_file, dtype=CSV_COL_TYPES)

    logging.debug("Dropping duplicates")
    with ProgressBar():
        df = df.drop_duplicates().compute()

    logging.info(f"Left with {len(df):,} rows and {len(df.slug.unique())} documents")
    logging.info(f"DataFrame uses {naturalsize(df.memory_usage().sum())} of memory")

    pq_file.parent.mkdir(parents=True, exist_ok=True)  # Ensure output path exists.
    logging.debug(f"Writing to {pq_file}")
    df.to_parquet(pq_file, compression="lz4", index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "infile", nargs="?", default=INPUT_CSV, help="csv of training data to convert",
    )
    parser.add_argument(
        "outfile", nargs="?", default=OUTPUT_PQ, help="destination parquet",
    )
    parser.add_argument("--log-level", dest="log_level", default="INFO")
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level.upper())

    csv_to_parquet(args.infile, args.outfile)
