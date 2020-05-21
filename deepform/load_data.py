import logging
import os
import pickle
import random
from pathlib import Path

import pandas as pd

import db.source as db
from features import token_features

seed = 42

SOURCE_DIR = Path().absolute() / "source"
SOURCE_DATA = SOURCE_DIR / "training.csv"
CACHE_FILE = SOURCE_DIR / "cached_features.p"


def clean_slug(slug):
    return slug[:-4] if slug.endswith(".pdf") else slug


def input_docs(source_data=SOURCE_DATA):
    docs_df = pd.read_csv(source_data)

    # Filter out tokens that are too short.
    docs_df = docs_df[docs_df["token"].str.len() >= 3].reset_index(drop=True)

    # Get rid of '.pdf' at the end of slugs (make the new data consistent with the old).
    docs_df["slug"] = docs_df["slug"].apply(clean_slug)

    for _, group in docs_df.groupby("slug"):
        yield group.to_dict("records")


# Load raw training data, create our per-token features and binary labels
def load_training_data_nocache(config):
    slugs = []
    tokens = []
    features = []
    labels = []

    blank_token = {
        "token": "",  # for window padding
        "x0": 0,
        "y0": 0,
        "x1": 0,
        "y1": 0,
        "page": 0,
        "match": 0,
    }

    n_docs = 0
    for doc_tokens in input_docs():

        if not config.pad_windows and len(doc_tokens) < config.window_len:
            continue  # this doc is too short

        n_docs += 1
        if n_docs > config.read_docs:
            logging.debug(f"Collected {n_docs} docs, stopping here")
            break

        token_row = [
            {
                "token": row["token"],
                "x0": row["x0"],
                "y0": row["y0"],
                "x1": row["x1"],
                "y1": row["y1"],
                "page": row["page"],
                "match": float(row["gross_amount"]),
            }
            for row in doc_tokens
        ]

        feature_row = [token_features(row, config) for row in doc_tokens]

        # takes the token with the highest fuzzy string matching score as the correct answer
        max_score = max([float(row["gross_amount"]) for row in doc_tokens])
        if max_score < config.target_thresh:
            continue  # The document's best score isn't good enough
        label_row = [
            1 if float(row["gross_amount"]) == max_score else 0 for row in doc_tokens
        ]

        # Optionally pad document with a window of blanks at start and end, to avoid edge effects
        if config.pad_windows:
            n = config.window_len - 1

            token_padding = [blank_token for i in range(n)]
            token_row = token_padding + token_row + token_padding

            feature_padding = [token_features(None, config) for i in range(n)]
            feature_row = feature_padding + feature_row + feature_padding

            label_padding = [0 for i in range(n)]
            label_row = label_padding + label_row + label_padding

        # Slugs and token text are not training data, but used for evaluating results later
        slugs.append(doc_tokens[0]["slug"])  # unique document ID, also PDF filename
        tokens.append(token_row)

        features.append(feature_row)
        labels.append(label_row)

    logging.info(f"Length of slugs in load_training_data_nocache = {len(slugs)}")
    return slugs, tokens, features, labels


# Because generating the list of features is so expensive, we cache it on disk
def load_training_data_from_files(config, pickle_destination=CACHE_FILE):
    if config.use_data_cache and os.path.isfile(pickle_destination):
        logging.info("Loading training data from cache...")
        slugs, tokens, features, labels = pickle.load(open(pickle_destination, "rb"))
    else:
        logging.info("Loading training data...")
        slugs, tokens, features, labels = load_training_data_nocache(config)
        if config.use_data_cache:
            logging.info("Saving training data to cache...")
            pickle.dump(
                (slugs, tokens, features, labels), open(pickle_destination, "wb")
            )

        # Trim the training data so we can sweep across various training data sizes
        # we may have less data than asked for, just return all
        if len(slugs) <= config.len_train:
            return slugs, tokens, features, labels

        random.seed(seed)
        slugs = random.sample(slugs, config.len_train)
        random.seed(seed)
        tokens = random.sample(tokens, config.len_train)
        random.seed(seed)
        features = random.sample(features, config.len_train)
        random.seed(seed)
        labels = random.sample(labels, config.len_train)

    return slugs, tokens, features, labels


def load_training_data_from_db(config):
    conn = db.connection(config.db_user, config.db_password)
    slugs = []
    token_text = []
    features = []
    labels = []

    for doc in db.input_docs(conn):
        dc_slug, _committee, _gross_amount_usd, rows = doc
        slugs.append(dc_slug)
        token_text.append([token for token in rows.token])
        features.append([token_features(row, config) for idx, row in rows.iterrows()])
        # threshold fuzzy matching score with our target field, to get binary
        # labels
        labels.append(
            [
                (0 if float(row["gross_amount"]) < config.target_thresh else 1)
                for idx, row in rows.iterrows()
            ]
        )

    return slugs, token_text, features, labels


def load_training_data(config):
    if config.data_from_db:
        return load_training_data_from_db(config)
    else:
        return load_training_data_from_files(config)
