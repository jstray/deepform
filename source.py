from features import token_features
import csv
import os
import pickle
import db.source as db
from features import token_features
import random

seed = 42

def input_docs(max_docs=None, source_data="source/training.csv"):
    incsv = csv.DictReader(open(source_data, mode='r'))

    # Reconstruct documents by concatenating all rows with the same slug
    active_slug = None
    doc_rows = []
    num_docs = 0

    for row in incsv:
        # throw out tokens that are too short, they won't help us
        token = row['token']
        if len(token) < 3:
            continue

        if row['slug'] != active_slug:
            if active_slug:
                yield doc_rows
                num_docs += 1
                if max_docs and num_docs >= max_docs:
                    return
            doc_rows = [row]
            active_slug = row['slug']
        else:
            doc_rows.append(row)

    yield doc_rows

# Load raw training data, create our per-token features and binary labels   
def load_training_data_nocache(config):
    slugs = []
    token_text = []
    features = []
    labels = []
    for doc_tokens in input_docs(max_docs=config.read_docs):    
        if not config.pad_windows and len(doc_tokens) < config.window_len:
            continue # this doc is too short
        
        token_row = [row['token'] for row in doc_tokens]
        feature_row = [token_features(row, config) for row in doc_tokens]

        # takes the token with the highest fuzzy string matching score as the correct answer
        max_score = max([float(row['gross_amount']) for row in doc_tokens])
        label_row = [1 if float(row['gross_amount'])==max_score else 0 for row in doc_tokens]

        # Optionally pad document with a window of blanks at start and end, to avoid edge effects
        if config.pad_windows:
            n = config.window_len - 1
            
            token_padding = ['' for i in range(n)]
            token_row = token_padding + token_row
            token_row.extend(token_padding)

            feature_padding = [token_features(None, config) for i in range(n)]
            feature_row = feature_padding + feature_row
            feature_row.extend(feature_padding)

            label_padding = [0 for i in range(n)]
            label_row = label_padding + label_row
            label_row.extend(label_padding)

        # Slugs and token text are not training data, but used for evaluating results later
        slugs.append(doc_tokens[0]['slug']) # unique document ID, also PDF filename
        token_text.append(token_row)

        features.append(feature_row)
        labels.append(label_row)

    print("Length of slugs in load_training_data_nocache = ", len(slugs))
    return slugs, token_text, features, labels


# Because generating the list of features is so expensive, we cache it on disk
def load_training_data_from_files(
        config, pickle_destination="source/cached_features.p"):
    if config.use_data_cache and os.path.isfile(pickle_destination):
        print('Loading training data from cache...')
        slugs, token_text, features, labels = pickle.load(
            open(pickle_destination, 'rb'))
    else:
        print('Loading training data...')
        slugs, token_text, features, labels = load_training_data_nocache(
            config)
        print('Saving training data to cache...')
        pickle.dump(
            (slugs, token_text, features, labels), open(
                pickle_destination, 'wb'))

        # Trim the training data so we can sweep across various training data
        # sizes
        print(
            "Length of slugs in load_training_data before modification = ",
            len(slugs))
        random.seed(seed)
        slugs = random.sample(slugs, config.len_train)
        print(
            "Length of slugs in load_training_data after modification = ",
            len(slugs))
        random.seed(seed)
        token_text = random.sample(token_text, config.len_train)
        random.seed(seed)
        features = random.sample(features, config.len_train)
        random.seed(seed)
        labels = random.sample(labels, config.len_train)

    return slugs, token_text, features, labels


def load_training_data_from_db(config):
    conn = db.connection(config.db_user, config.db_password)
    slugs = []
    token_text = []
    features = []
    labels = []

    for doc in db.input_docs(conn):
        dc_slug, committee, gross_amount_usd, rows = doc
        slugs.append(dc_slug)
        token_text.append([token for token in rows.token])
        features.append([token_features(row, config)
                         for idx, row in rows.iterrows()])
        # threshold fuzzy matching score with our target field, to get binary
        # labels
        labels.append([(0 if float(row['gross_amount']) <
                        config.target_thresh else 1) for idx, row in rows.iterrows()])

    return slugs, token_text, features, labels


def load_training_data(config):
    if config.data_from_db:
        return load_training_data_from_db(config)
    else:
        return load_training_data_from_files(config)


if __name__ == "__main__":
    docs = [doc for doc in input_docs(max_docs=1)]
    print(docs)
