"""
Use a manifest to add labels to the tokenized documents.
"""

import argparse
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd
from fuzzywuzzy import fuzz
from tqdm import tqdm

from deepform.common import LABELED_DIR, TOKEN_DIR
from deepform.util import normalize_date, normalize_dollars, simple_string


def default_similarity(lhs, rhs):
    return fuzz.ratio(simple_string(lhs), simple_string(rhs)) / 100


def dollar_similarity(lhs, rhs):
    lh_dollar, rh_dollar = normalize_dollars(lhs), normalize_dollars(rhs)
    if lh_dollar and rh_dollar:
        return fuzz.ratio(lh_dollar, rh_dollar) / 100
    return default_similarity(lhs, rhs)


def date_similarity(lhs, rhs):
    lh_date, rh_date = normalize_date(lhs), normalize_date(rhs)
    if lh_date and rh_date and lh_date == rh_date:
        return 1
    return default_similarity(lhs, rhs)


LABEL_COLS = {
    # Each label column, and the match function that it uses.
    "contract_num": default_similarity,
    "advertiser": default_similarity,
    "flight_from": date_similarity,
    "flight_to": date_similarity,
    "gross_amount": dollar_similarity,
}


def label_tokens(tokens, labels):
    for col_name, label_value in labels.items():
        match_fn = LABEL_COLS[col_name]
        tokens[col_name] = tokens.token.apply(match_fn, args=(label_value,))
    return tokens


def label_doc(token_file, dest_file, labels):
    tokens = pd.read_parquet(token_file)
    tokens = label_tokens(tokens, labels)
    tokens.to_parquet(dest_file, compression="lz4", index=False)


def label_docs(manifest, source_dir, dest_dir):
    token_files = {p.stem: p for p in source_dir.glob("*.parquet")}

    jobqueue = []
    for row in manifest.itertuples():
        slug = row.file_id
        if slug not in token_files:
            logging.error(f"No token file for {slug}")
            continue
        labels = {}
        for label_col in LABEL_COLS:
            labels[label_col] = getattr(row, label_col)
            if not labels[label_col]:
                logging.warning(f"'{label_col}' for {slug} is empty")
        jobqueue.append(
            {
                "token_file": token_files[slug],
                "dest_file": dest_dir / f"{slug}.parquet",
                "labels": labels,
            }
        )

    label_jobs = []
    with ThreadPoolExecutor() as executor:
        for kwargs in jobqueue:
            label_jobs.append(executor.submit(label_doc, **kwargs))

        _ = [j.result() for j in tqdm(as_completed(label_jobs), total=len(label_jobs))]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", help="CSV with labels for each document")
    parser.add_argument(
        "indir", nargs="?", default=TOKEN_DIR, help="training data to extend",
    )
    parser.add_argument(
        "outdir", nargs="?", default=LABELED_DIR, help="directory of output files",
    )
    parser.add_argument("--log-level", dest="log_level", default="INFO")
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level.upper())

    logging.info(f"Reading {Path(args.manifest).resolve()}")
    manifest = pd.read_csv(args.manifest)

    indir, outdir = Path(args.indir).resolve(), Path(args.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    label_docs(manifest, indir, outdir)
