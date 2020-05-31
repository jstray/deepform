# Data extraction by deep learning, using a fully connected architecture over
# token windows. Engineered to extract total amounts, using a few custom
# features.
# Achieves up to 90% accuracy.
#
# jstray 2019-6-12

import argparse
import logging
import os
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
from numpy import isclose as same_page
from wandb.keras import WandbCallback

from deepform.add_features import DOC_INDEX
from deepform.document_store import DocumentStore
from deepform.pdfs import get_pdf_path
from deepform.util import (
    config_desc,
    docrow_to_bbox,
    is_dollar_amount,
    normalize_dollars,
)

# Generator that reads raw training data
# For each document, yields an array of dictionaries, each of which is a token
# ---- Resample features,labels as windows ----


# control the fraction of windows that include a positive label. not efficient.
def one_window(dataset, config):
    require_positive = random.random() > config.positive_fraction
    return dataset.random_document().random_window(require_positive)


def windowed_generator(dataset, config):
    # Create empty arrays to contain batch of features and labels#
    batch_features = np.zeros((config.batch_size, config.window_len, config.token_dims))
    batch_labels = np.zeros((config.batch_size, config.window_len))

    while True:
        for i in range(config.batch_size):
            window = one_window(dataset, config)
            batch_features[i, :, :] = window.features
            batch_labels[i, :] = window.labels
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
def predict_scores(model, document):
    windowed_features = np.stack([window.features for window in document])
    window_scores = model.predict(windowed_features)

    scores = np.zeros(len(document) + document.window_len)
    for i in range(len(document)):
        # would max work better than sum?
        scores[i : i + document.window_len] += window_scores[i]
    return scores


# returns text, score of best answer, plus all scores
def predict_answer(model, document):
    scores = predict_scores(model, document)
    best_score_idx = np.argmax(scores)
    best_score_text = document.tokens.iloc[best_score_idx]["token"]
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


def log_pdf(doc, score, scores, predict_text, answer_text):
    fname = get_pdf_path(doc.slug)
    try:
        pdf = pdfplumber.open(fname)
    except Exception:
        # If the file's not there, that's fine -- we use available PDFs to
        # define what to see
        print("Cannot open pdf " + fname)
        return

    print(f"Rendering output for {fname}")

    # Get the correct answers: find the indices of the token(s) labelled 1
    target_idx = [idx for (idx, val) in enumerate(doc.labels) if val == 1]

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
        for idx, tok in enumerate(doc.tokens):
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
            doc.tokens.iloc[i]
            for i in target_idx
            if same_page(doc.tokens.iloc[i]["page"], current_page)
        ]
        rects = [docrow_to_bbox(t) for t in target_toks]
        im.draw_rects(rects, stroke="blue", stroke_width=3, fill=None)

        page_images.append(wandb.Image(im.annotated, caption="page " + str(pagenum)))

    # get best matching score of any token in the training data
    match = doc.tokens["match"].max()
    caption = (
        f"{doc.slug} guessed:{predict_text} answer:{answer_text} match:{match:.2f}"
    )
    if answer_match(predict_text, answer_text):
        caption = "CORRECT " + caption
    else:
        caption = "INCORRECT " + caption
    wandb.log({caption: page_images})


# Calculate accuracy of answer extraction over num_to_test docs, print
# diagnostics while we do so
def compute_accuracy(model, config, dataset, num_to_test, print_results):
    n_print = config.render_results_size

    n_docs = min(num_to_test, len(dataset))
    acc = 0
    for doc in dataset.sample(n_docs):
        slug = doc.slug
        answer_text = doc.gross_amount

        predict_text, predict_score, token_scores = predict_answer(model, doc)

        match = answer_match(predict_text, answer_text)

        acc += match
        prefix = f"Correct: {slug}" if match else f"**Incorrect: {slug}"
        guessed = f'guessed "{predict_text}" with score {predict_score:.2f}, '
        correct = f'correct "{answer_text}"'

        if print_results:
            print(f"{prefix}: {guessed}, {correct}")
            if not match and n_print > 0:
                log_pdf(doc, predict_score, token_scores, predict_text, answer_text)
                n_print -= 1

    return acc / n_docs


# ---- Custom callback to log document-level accuracy ----


class DocAccCallback(K.callbacks.Callback):
    def __init__(self, config, dataset, logname):
        self.config = config
        self.dataset = dataset
        self.logname = logname

    def on_epoch_end(self, epoch, logs):
        if epoch >= self.config.epochs - 1:
            # last epoch, sample from all docs and print inference results
            print_results = self.logname == "doc_val_acc"
            test_size = len(self.dataset)
        else:
            # intermediate epoch, small sample and no logging
            print_results = False
            test_size = self.config.doc_acc_sample_size + epoch

        # Avoid sampling tens of thousands of documents on large training sets.
        test_size = min(test_size, self.config.doc_acc_max_sample_size)

        acc = compute_accuracy(
            self.model, self.config, self.dataset, test_size, print_results,
        )

        print(f"This epoch {self.logname}: {acc}")
        wandb.log({self.logname: acc})


def main(config):
    config.name = config_desc(config)
    if config.use_wandb:
        run.save()

    print("Configuration:")
    print(config)

    # all_data = load_training_data(config)
    all_documents = DocumentStore.open(index_file=DOC_INDEX, config=config)

    # split into validation and training sets
    validation_set, training_set = all_documents.split(percent=config.val_split)
    print(f"Training on {len(training_set)}, validating on {len(validation_set)}")

    model = create_model(config)
    print(model.summary())

    callbacks = [WandbCallback()] if config.use_wandb else []
    callbacks.append(DocAccCallback(config, training_set, "doc_train_acc"))
    callbacks.append(DocAccCallback(config, validation_set, "doc_val_acc"))

    model.fit_generator(
        windowed_generator(training_set, config),
        steps_per_epoch=config.steps_per_epoch,
        epochs=config.epochs,
        callbacks=callbacks,
    )


if __name__ == "__main__":
    # First read in the initial configuration.
    run = wandb.init(project="extract_total", entity="deepform", allow_val_change=True)
    config = run.config

    # Then override it with any parameters passed along the command line.
    parser = argparse.ArgumentParser()

    # Anything in the config is fair game to be overridden by a command line flag.
    for key, info in config.as_dict().items():
        if key.startswith("_"):
            continue
        value = info["value"]
        cli_flag = "--" + key.replace("_", "-")
        parser.add_argument(
            cli_flag, dest=key, help=info["desc"], type=type(value), default=value
        )

    args = parser.parse_args()
    config.update(args, allow_val_change=True)

    if not config.use_wandb:
        os.environ["WANDB_SILENT"] = "true"
        os.environ["WANDB_MODE"] = "dryrun"
        wandb.log = lambda *args, **kwargs: None

    logging.basicConfig(level=config.log_level)

    main(config)
