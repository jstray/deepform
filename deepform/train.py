# Data extraction by deep learning, using a fully connected architecture over token windows.
# Engineered to extract total amounts, using a few custom features.
# Achieves up to 90% accuracy.
#
# jstray 2019-6-12

import random

import keras as K
import numpy as np
import pdfplumber
import tensorflow as tf
import wandb
from keras.backend import squeeze
from keras.engine.input_layer import Input
from keras.layers import Dense, Dropout, Flatten, Lambda, concatenate
from keras.layers.embeddings import Embedding
from keras.models import Model
from wandb.keras import WandbCallback

from load_data import load_training_data
from util import docrow_to_bbox, is_dollar_amount, normalize_dollars

run = wandb.init(project="extract_total", entity="deepform", name="hypersweep")
config = run.config

c_ = config
run.name = f"len:{c_.len_train} win:{c_.window_len} str:{c_.use_string} page:{c_.use_page} geom:{c_.use_geom} amt:{c_.use_amount} voc:{c_.vocab_size} emb:{c_.vocab_embed_size} steps:{c_.steps_per_epoch}"
run.save()


# Generator that reads raw training data
# For each document, yields an array of dictionaries, each of which is a token
# ---- Resample features,labels as windows ----


# returns a window of tokens, labels at a random position in a random document
def one_window_unbalanced(features, labels, window_len):
    doc_idx = random.randint(0, len(features) - 1)
    doc_len = len(features[doc_idx])
    tok_idx = random.randint(0, doc_len - window_len)
    return (
        features[doc_idx][tok_idx : tok_idx + window_len],
        labels[doc_idx][tok_idx : tok_idx + window_len],
    )


# control the fraction of windows that include a positive label. not efficient.
def one_window(features, labels, window_len, positive_fraction):
    f, label_set = one_window_unbalanced(features, labels, window_len)
    if random.random() > positive_fraction:  # mostly positive examples
        while not (1 in label_set):
            f, label_set = one_window_unbalanced(features, labels, window_len)
    return f, label_set


def windowed_generator(features, labels, config):
    # Create empty arrays to contain batch of features and labels#
    batch_features = np.zeros((config.batch_size, config.window_len, config.token_dims))
    batch_labels = np.zeros((config.batch_size, config.window_len))

    while True:
        for i in range(config.batch_size):
            features1, labels1 = one_window(
                features, labels, config.window_len, config.positive_fraction
            )
            batch_features[i, :, :] = features1
            batch_labels[i, :] = labels1
        yield batch_features, batch_labels


# ---- Custom loss function is basically MSE but high penalty for missing a 1 label ---
def missed_token_loss(one_penalty):
    def _missed_token_loss(y_true, y_pred):
        expected_zero = tf.cast(tf.math.equal(y_true, 0), tf.float32)
        s = y_pred * expected_zero
        zero_loss = K.backend.mean(K.backend.square(s))
        expected_one = tf.cast(tf.math.equal(y_true, 1), tf.float32)
        t = one_penalty * (1 - y_pred) * expected_one
        one_loss = K.backend.mean(K.backend.square(t))
        return zero_loss + one_loss

    return _missed_token_loss  # closes over one_penalty


# --- Specify network ---


def create_model(config):
    indata = Input((config.window_len, config.token_dims))

    # split into the hash and the rest of the token features, embed hash as
    # one-hot, then merge
    tok_hash = Lambda(
        lambda x: squeeze(K.backend.slice(x, (0, 0, 0), (-1, -1, 1)), axis=2)
    )(indata)
    tok_features = Lambda(lambda x: K.backend.slice(x, (0, 0, 1), (-1, -1, -1)))(indata)
    embed = Embedding(config.vocab_size, config.vocab_embed_size)(tok_hash)
    merged = concatenate([embed, tok_features], axis=2)

    f = Flatten()(merged)
    d1 = Dense(
        int(config.window_len * config.token_dims * config.layer_1_size_factor),
        activation="sigmoid",
    )(f)
    d2 = Dropout(config.dropout)(d1)
    d3 = Dense(
        int(config.window_len * config.token_dims * config.layer_2_size_factor),
        activation="sigmoid",
    )(d2)
    d4 = Dropout(config.dropout)(d3)
    d5 = Dense(config.window_len, activation="elu")(d4)

    model = Model(inputs=[indata], outputs=[d5])
    model.compile(
        optimizer=K.optimizers.Adam(learning_rate=config.learning_rate),
        loss=missed_token_loss(config.penalize_missed),
        metrics=["acc"],
    )

    return model


# --- Predict ---
# Our network is windowed, so we have to aggregate windows to get a final score

# Returns vector of token scores
def predict_scores(model, features, window_len):
    doc_len = len(features)
    num_windows = doc_len - window_len + 1

    windowed_features = np.array(
        [features[i : i + window_len] for i in range(num_windows)]
    )
    window_scores = model.predict(windowed_features)

    scores = np.zeros(doc_len)
    for i in range(num_windows):
        # would max work better than sum?
        scores[i : i + window_len] += window_scores[i]
    return scores


# returns text, score of best answer, plus all scores
def predict_answer(model, features, tokens, window_len):
    scores = predict_scores(model, features, window_len)
    best_score_idx = np.argmax(scores)
    best_score_text = tokens[best_score_idx]["token"]
    return best_score_text, scores[best_score_idx], scores


# returns text of correct answer,
def correct_answer(features, labels, tokens):
    answer_idx = np.argmax(labels)
    answer_text = tokens[answer_idx]["token"]
    return answer_text


# Match e.g. "$14,123.02" to "14123.02"
def answer_match(predicted, actual):
    return (
        is_dollar_amount(predicted)
        and is_dollar_amount(actual)
        and (normalize_dollars(predicted) == normalize_dollars(actual))
    )


# -- Render visualization of output on PDF pages --

# make page number matches robust to floating point dirt
def same_page(pagetok, current_page):
    return abs(float(pagetok) - current_page) < 0.01


def log_pdf(slug, tokens, labels, score, scores, predict_text, answer_text):
    fname = "../pdfs/" + slug + ".pdf"
    try:
        pdf = pdfplumber.open(fname)
    except Exception:
        # If the file's not there, that's fine -- we use available PDFs to
        # define what to see
        print("Cannot open pdf " + fname)
        return

    print("Rendering output for " + fname)

    # Get the correct answers: find the indices of the token(s) labelled 1
    target_idx = [idx for (idx, val) in enumerate(labels) if val == 1]

    # Draw the machine output: get a score for each token
    page_images = []
    for pagenum, page in enumerate(pdf.pages):
        im = page.to_image(resolution=300)

        # training data has 0..1 for page range (see create-training-data.py)
        num_pages = len(pdf.pages)
        if num_pages > 1:
            current_page = pagenum / float(num_pages - 1)
        else:
            current_page = 0.0

        # Draw guesses
        for idx, tok in enumerate(tokens):
            rel_score = scores[idx] / score
            if rel_score >= 0.5 and same_page(tok["page"], current_page):
                if rel_score == 1:
                    w = 5
                    s = "magenta"
                elif rel_score >= 0.75:
                    w = 3
                    s = "red"
                else:
                    w = 1
                    s = "red"
                im.draw_rect(docrow_to_bbox(tok), stroke=s, stroke_width=w, fill=None)

        # Draw target tokens
        target_toks = [
            tokens[i] for i in target_idx if same_page(tokens[i]["page"], current_page)
        ]
        rects = [docrow_to_bbox(t) for t in target_toks]
        im.draw_rects(rects, stroke="blue", stroke_width=3, fill=None)

        page_images.append(wandb.Image(im.annotated, caption="page " + str(pagenum)))

    # get best matching score of any token in the training data
    match = max([tok["match"] for tok in tokens])
    caption = f"{slug} guessed:{predict_text} answer:{answer_text} match:{match:.2f}"
    if answer_match(predict_text, answer_text):
        caption = "CORRECT " + caption
    else:
        caption = "INCORRECT " + caption
    wandb.log({caption: page_images})


# Calculate accuracy of answer extraction over num_to_test docs, print
# diagnostics while we do so
def compute_accuracy(
    model, window_len, slugs, tokens, features, labels, num_to_test, print_results
):
    n_print = config.render_results_size

    n_docs = min(num_to_test, len(slugs))
    doc_idxs = random.sample(range(n_docs), n_docs)
    acc = 0.0
    for doc_idx in doc_idxs:
        slug = slugs[doc_idx]
        predict_text, predict_score, token_scores = predict_answer(
            model, features[doc_idx], tokens[doc_idx], window_len
        )
        answer_text = correct_answer(
            features[doc_idx], labels[doc_idx], tokens[doc_idx]
        )

        if answer_match(predict_text, answer_text):
            if print_results:
                print(
                    f'Correct: {slug}: guessed "{predict_text}" with score {predict_score:.2f}, correct "{answer_text}"'
                )
            acc += 1
        else:
            if print_results:
                print(
                    f'***Incorrect: {slug}: guessed "{predict_text}" with score {predict_score:.2f}, correct "{answer_text}"'
                )

                if n_print > 0:
                    log_pdf(
                        slug,
                        tokens[doc_idx],
                        labels[doc_idx],
                        predict_score,
                        token_scores,
                        predict_text,
                        answer_text,
                    )
                    n_print -= 1

    return acc / n_docs


# ---- Custom callback to log document-level accuracy ----


class DocAccCallback(K.callbacks.Callback):
    def __init__(
        self, window_len, slugs, tokens, features, labels, num_to_test, logname
    ):
        self.window_len = window_len
        self.slugs = slugs
        self.tokens = tokens
        self.features = features
        self.labels = labels
        self.num_to_test = num_to_test
        self.logname = logname

    def on_epoch_end(self, epoch, logs):
        if epoch >= config.epochs - 1:
            # last epoch, sample from all docs and print inference results (for validation set)
            print_results = self.logname == "doc_val_acc"
            test_size = len(self.slugs)
        else:
            # intermediate epoch, small sample (getting gradually more accurate) and no logging
            print_results = False
            test_size = self.num_to_test + epoch

        acc = compute_accuracy(
            self.model,
            self.window_len,
            self.slugs,
            self.tokens,
            self.features,
            self.labels,
            test_size,
            print_results,
        )

        print(f"This epoch {self.logname}: {acc}")
        wandb.log({self.logname: acc})


# --- Main ---

print("Configuration:")
print(config)

slugs, token_text, features, labels = load_training_data(config)

# DF: commenting out because these are just diagnostic and rely on in-mem data
# print(f'Loaded {len(features)}')
# max_length = max([len(x) for x in labels])
# print(f'Max document size {max_length}')
# avg_length = sum([len(x) for x in labels]) / len(labels)
# print(f'Average document size {avg_length}')

# split into train and test
slugs_train = []
token_text_train = []
features_train = []
labels_train = []
slugs_val = []
token_text_val = []
features_val = []
labels_val = []
for i in range(len(features)):
    if random.random() < config.val_split:
        slugs_val.append(slugs[i])
        token_text_val.append(token_text[i])
        features_val.append(features[i])
        labels_val.append(labels[i])
    else:
        slugs_train.append(slugs[i])
        token_text_train.append(token_text[i])
        features_train.append(features[i])
        labels_train.append(labels[i])

print(f"Training on {len(features_train)}, validating on {len(features_val)}")

model = create_model(config)
print(model.summary())

model.fit_generator(
    windowed_generator(features_train, labels_train, config),
    steps_per_epoch=config.steps_per_epoch,
    epochs=config.epochs,
    callbacks=[
        WandbCallback(),
        DocAccCallback(
            config.window_len,
            slugs_train,
            token_text_train,
            features_train,
            labels_train,
            config.doc_acc_sample_size,
            "doc_train_acc",
        ),
        DocAccCallback(
            config.window_len,
            slugs_val,
            token_text_val,
            features_val,
            labels_val,
            config.doc_acc_sample_size,
            "doc_val_acc",
        ),
    ],
)
