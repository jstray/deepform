"""
Process a parquet of all training data to add labels and computed features.

Final data is stored individually (per-document) to enable random access of
small samples, with an index over all the documents.
"""

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import Enum, auto
from pathlib import Path

import numpy as np
import pandas as pd
from fuzzywuzzy import fuzz
from tqdm import tqdm

from deepform.common import DATA_DIR, TOKEN_DIR, TRAINING_DIR, TRAINING_INDEX
from deepform.data.create_vocabulary import get_token_id
from deepform.logger import logger
from deepform.util import (
    date_similarity,
    default_similarity,
    dollar_similarity,
    is_dollar_amount,
    log_dollar_amount,
)


class TokenType(Enum):
    NONE = 0
    CONTRACT_NUM = auto()
    ADVERTISER = auto()
    FLIGHT_FROM = auto()
    FLIGHT_TO = auto()
    GROSS_AMOUNT = auto()


LABEL_COLS = {
    # Each label column, and the match function that it uses.
    "contract_num": default_similarity,
    "advertiser": default_similarity,
    "flight_from": date_similarity,
    "flight_to": date_similarity,
    "gross_amount": dollar_similarity,
}

MAX_TOKENS_BY_TARGET = {
    # Each label column, and the maximum expected tokens that it uses.
    "contract_num": 3,
    "advertiser": 11,
    "flight_from": 3,
    "flight_to": 3,
    "gross_amount": 3,
}


def extend_and_write_docs(source_dir, manifest, pq_index, out_path, max_token_count):
    """Split data into individual documents, add features, and write to parquet."""

    token_files = {p.stem: p for p in source_dir.glob("*.parquet")}

    jobqueue = []
    for row in manifest.itertuples():
        slug = row.file_id
        if slug not in token_files:
            logger.error(f"No token file for {slug}")
            continue
        labels = {}
        for label_col in LABEL_COLS:
            labels[label_col] = getattr(row, label_col)
            if not labels[label_col]:
                logger.warning(f"'{label_col}' for {slug} is empty")
        jobqueue.append(
            {
                "token_file": token_files[slug],
                "dest_file": out_path / f"{slug}.parquet",
                "labels": labels,
                "max_token_count": max_token_count,
            }
        )

    # Spin up a bunch of jobs to do the conversion
    with ThreadPoolExecutor() as executor:
        doc_jobs = []
        for kwargs in jobqueue:
            doc_jobs.append(executor.submit(process_document_tokens, **kwargs))

        logger.debug("Waiting for jobs to complete")
        progress = tqdm(as_completed(doc_jobs), total=len(doc_jobs))
        doc_results = [j.result() for j in progress]

    logger.debug(f"Writing document index to {pq_index}...")
    doc_index = pd.DataFrame(doc_results).set_index("slug", drop=True)
    doc_index.to_parquet(pq_index)


def pq_index_and_dir(pq_index, pq_path=None):
    """Get directory for sharded training data, creating if necessary."""
    pq_index = Path(pq_index).resolve()
    if pq_path is None:
        pq_path = TRAINING_DIR
    else:
        pq_path = Path(pq_path)
    pq_index.parent.mkdir(parents=True, exist_ok=True)
    pq_path.mkdir(parents=True, exist_ok=True)
    return pq_index, pq_path


def process_document_tokens(token_file, dest_file, labels, max_token_count):
    """Filter out short tokens, add computed features, and return index info."""
    slug = token_file.stem
    doc = pd.read_parquet(token_file).reset_index(drop=True)

    doc = label_tokens(doc, labels, max_token_count)

    # Strip whitespace off all tokens.
    doc["token"] = doc.token.str.strip()

    # Remove tokens shorter than three characters.
    doc = doc[doc.token.str.len() >= 3]

    # Extend with the straightforward features.
    doc = add_base_features(doc)

    # Handle the features that need the whole document.
    doc["label"] = np.zeros(len(doc), dtype="u1")
    # The "label" column stores the TokenType that correctly labels this token.
    # By default this is 0, or "NONE".
    best_matches = {}
    for feature in LABEL_COLS:
        token_value = TokenType[feature.upper()].value
        max_score = doc[feature].max()
        best_matches[f"best_match_{feature}"] = max_score
        matches = token_value * np.isclose(doc[feature], max_score)
        doc["label"] = np.maximum(doc["label"], matches)

    # Write to its final location.
    doc.to_parquet(dest_file, index=False)

    # Return the summary information about the document.
    return {"slug": slug, "length": len(doc), **labels, **best_matches}


def label_tokens(tokens, labels, max_token_count):
    for col_name, label_value in labels.items():
        tokens[col_name] = 0.0
        match_fn = LABEL_COLS[col_name]
        max_token_count = MAX_TOKENS_BY_TARGET[col_name]
        if col_name == "advertiser":
            tokens[col_name] = label_multitoken(
                tokens.token.to_numpy(), label_value, max_token_count, match_fn
            )
        else:
            tokens[col_name] = tokens.token.apply(match_fn, args=(label_value,))

    return tokens


def label_multitoken(tokens, value, token_count, match_fn=default_similarity):
    best_match_values = np.array([match_fn(value, x) for x in tokens])
    for c in range(1, token_count):
        texts = [" ".join(tokens[i - c : i]) for i in range(c, tokens.size)]
        match_values = np.array([match_fn(value, x) for x in texts] + [0] * c)
        for p in range(c):
            best_match_values = np.maximum(best_match_values, np.roll(match_values, p))
    return best_match_values


def fraction_digits(s):
    """Return the fraction of a string that is composed of digits."""
    return np.mean([c.isdigit() for c in s]) if isinstance(s, str) else 0.0


def match_string(a, b):
    m = fuzz.ratio(a.lower(), b.lower()) / 100.0
    return m if m >= 0.9 else 0


def add_base_features(token_df):
    """Extend a DataFrame with features that can be pre-computed."""
    df = token_df.copy()
    df["tok_id"] = df["token"].apply(get_token_id).astype("u2")
    df["length"] = df["token"].str.len().astype("i2")
    df["digitness"] = df["token"].apply(fraction_digits).astype("f4")
    df["is_dollar"] = df["token"].apply(is_dollar_amount).astype("f4")
    df["log_amount"] = df["token"].apply(log_dollar_amount).fillna(0).astype("f4")

    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "manifest",
        help="CSV with labels for each document",
        default=DATA_DIR / "3_year_manifest.csv",
    )
    parser.add_argument(
        "indir",
        nargs="?",
        default=TOKEN_DIR,
        help="directory of document tokens",
    )
    parser.add_argument(
        "indexfile",
        nargs="?",
        default=TRAINING_INDEX,
        help="path to index of resulting parquet files",
    )
    parser.add_argument(
        "outdir",
        nargs="?",
        default=TRAINING_DIR,
        help="directory of parquet files",
    )
    parser.add_argument(
        "--max-token-count",
        type=int,
        default=5,
        help="maximum number of contiguous tokens to match against each label",
    )
    parser.add_argument("--log-level", dest="log_level", default="INFO")
    args = parser.parse_args()
    logger.setLevel(args.log_level.upper())

    logger.info(f"Reading {Path(args.manifest).resolve()}")
    manifest = pd.read_csv(args.manifest)

    indir, index, outdir = Path(args.indir), Path(args.indexfile), Path(args.outdir)
    index.parent.mkdir(parents=True, exist_ok=True)
    outdir.mkdir(parents=True, exist_ok=True)
    extend_and_write_docs(indir, manifest, index, outdir, args.max_token_count)
