"""
Process a parquet of all training data to add labels and computed features.

Final data is stored individually (per-document) to enable random access of
small samples, with an index over all the documents.
"""

import argparse
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from fuzzywuzzy import fuzz
import numpy as np
import pandas as pd
from tqdm import tqdm

from deepform.data.csv_to_parquet import OUTPUT_PQ as INPUT_PQ
from deepform.util import is_dollar_amount, log_dollar_amount

# Defaults
DOC_INDEX = INPUT_PQ.parent / "doc_index.parquet"


def extend_and_write_docs(df, pq_index=DOC_INDEX, pq_path=None):
    """Split data into individual documents, add features, and write to parquet."""
    # Set defaults and create whatever directories we need.
    pq_index, pq_path = pq_index_and_dir(pq_index, pq_path)

    # Spin up a bunch of jobs to do the conversion
    with ThreadPoolExecutor() as executor:
        doc_jobs = []
        logging.debug("Starting document conversion jobs")
        for slug, doc in df.groupby("slug"):
            kwargs = {"slug": slug, "doc": doc, "base_path": pq_path}
            doc_jobs.append(executor.submit(process_document_tokens, **kwargs))

        logging.debug("Waiting for jobs to complete")
        progress = tqdm(as_completed(doc_jobs), total=len(doc_jobs))
        doc_results = [j.result() for j in progress]

    logging.debug(f"Writing document index to {pq_index}...")
    doc_index = pd.DataFrame(doc_results).set_index("slug", drop=True)
    doc_index.to_parquet(pq_index, compression="lz4")


def pq_index_and_dir(pq_index, pq_path=None):
    """Get directory for sharded training data, creating if necessary."""
    pq_index = Path(pq_index).resolve()
    if pq_path is None:
        pq_path = pq_index.parent / "tokenized_docs"
    else:
        pq_path = Path(pq_path)
    pq_index.parent.mkdir(parents=True, exist_ok=True)
    pq_path.mkdir(parents=True, exist_ok=True)
    return pq_index, pq_path


def process_document_tokens(slug, doc, base_path):
    """Filter out short tokens, add computed features, and return index info."""

    # Remove tokens shorter than three characters.
    doc = doc[doc["token"].str.len() >= 3]

    # Extend with the straightforward features.
    doc = add_base_features(doc)

    # Handle the features that need the whole document.
    max_score = doc["gross_amount"].max()
    doc["label"] = np.isclose(doc["gross_amount"], max_score)

    # Write to its final location.
    file_path = base_path / f"{slug}.parquet"
    doc.drop("slug", axis=1).to_parquet(file_path, compression="lz4", index=False)

    # Return the summary information about the document.
    return {"slug": slug, "length": len(doc), "best_match": max_score}


def fraction_digits(s):
    """Return the fraction of a string that is composed of digits."""
    return np.mean([c.isdigit() for c in s]) if isinstance(s, str) else 0.0

def match_string(a,b):
    m = fuzz.ratio(a.lower(), b.lower()) / 100.0 
    return m if m>=0.9 else 0

def add_base_features(token_df):
    """Extend a DataFrame with features that can be pre-computed."""
    df = token_df.copy()
    df["hash"] = df["token"].apply(hash).astype("i8")
    df["length"] = df["token"].str.len().astype("i2")
    df["digitness"] = df["token"].apply(fraction_digits).astype("f4")
    df["is_dollar"] = df["token"].apply(is_dollar_amount).astype("f4")
    df["log_amount"] = df["token"].apply(log_dollar_amount).fillna(0).astype("f4")

    for s in ['amount','totals','gross','net','contract']:
        df['str_'+s] = df['token'].apply(lambda x: match_string(s,x)).astype("f4")

    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "infile", nargs="?", default=INPUT_PQ, help="training data to extend",
    )
    parser.add_argument(
        "indexfile",
        nargs="?",
        default=DOC_INDEX,
        help="path to index of resulting parquet files",
    )
    parser.add_argument(
        "outdir", nargs="?", help="directory of parquet files",
    )
    parser.add_argument("--log-level", dest="log_level", default="INFO")
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level.upper())

    logging.info(f"Reading {Path(args.infile).resolve()}")
    df = pd.read_parquet(args.infile)

    extend_and_write_docs(df, args.indexfile, args.outdir)
