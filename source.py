from features import token_features
import csv
import os
import pickle


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


def load_training_data_nocache(config):
    slugs = []
    token_text = []
    features = []
    labels = []
    for doc_tokens in input_docs(max_docs=config.read_docs):
        if len(doc_tokens) < config.window_len:
            continue  # TODO pad shorter docs

        # Not training data, but used for evaluating results later
        # unique document ID, also PDF filename
        slugs.append(doc_tokens[0]['slug'])
        token_text.append([row['token'] for row in doc_tokens])

        features.append([token_features(row, config.vocab_size)
                         for row in doc_tokens])

        # threshold fuzzy matching score with our target field, to get binary
        # labels
		max_score = math.max([float(row['gross_amount']) for row in doc_tokens])
		row_labels = [1 if float(row['gross_amount'])==max_score else 0 for row in doc_tokens]
		labels.append(row_labels)
    print("Length of slugs in load_training_data_nocache = ", len(slugs))
    return slugs, token_text, features, labels


# Because generating the list of features is so expensive, we cache it on disk
def load_training_data(config, pickle_destination="source/cached_features.p"):
    if os.path.isfile(pickle_destination):
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

	# Trim the training data so we can sweep across various training data sizes
	print("Length of slugs in load_training_data before modification = ", len(slugs))
	slugs = random.sample(slugs, config.len_train)
	print("Length of slugs in load_training_data after modification = ", len(slugs))
	token_text = random.sample(token_text, config.len_train)
	features = random.sample(features, config.len_train)
	labels = random.sample(labels, config.len_train)

    return slugs, token_text, features, labels


if __name__ == "__main__":
    docs = [doc for doc in input_docs(max_docs=1)]
    print(docs)
