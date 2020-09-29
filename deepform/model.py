import random
from datetime import datetime
from pathlib import Path

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.layers import (
    Dense,
    Dropout,
    Embedding,
    Flatten,
    Lambda,
    Reshape,
    Softmax,
    concatenate,
)
from tensorflow.keras.models import Model

from deepform.common import MODEL_DIR
from deepform.data.add_features import TokenType
from deepform.document import NUM_FEATURES
from deepform.util import git_short_hash


# control the fraction of windows that include a positive label. not efficient.
def one_window(dataset, config):
    require_positive = random.random() > config.positive_fraction
    window = dataset.random_document().random_window(require_positive)
    if config.permute_tokens:
        shuffle = np.random.permutation(config.window_len)
        window.features = window.features[shuffle]
        window.labels = window.labels[shuffle]
    return window


def windowed_generator(dataset, config):
    # Create empty arrays to contain batch of features and labels#
    batch_features = np.zeros((config.batch_size, config.window_len, NUM_FEATURES))
    batch_labels = np.zeros((config.batch_size, config.window_len))

    while True:
        for i in range(config.batch_size):
            window = one_window(dataset, config)
            batch_features[i, :, :] = window.features
            batch_labels[i, :] = window.labels  # tf.one_hot(window.labels, 2)
        yield batch_features, batch_labels


# ---- Custom loss function is basically MSE but high penalty for missing a 1 label ---
def missed_token_loss(one_penalty):
    def _missed_token_loss(y_true, y_pred):
        expected_zero = tf.cast(tf.math.equal(y_true, 0), tf.float32)
        s = y_pred * expected_zero
        zero_loss = tf.keras.backend.mean(tf.keras.backend.square(s))
        expected_one = tf.cast(tf.math.equal(y_true, 1), tf.float32)
        t = one_penalty * (1 - y_pred) * expected_one
        one_loss = tf.keras.backend.mean(tf.keras.backend.square(t))
        return zero_loss + one_loss

    return _missed_token_loss  # closes over one_penalty


# --- Specify network ---
def create_model(config):
    indata = tf.keras.Input((config.window_len, NUM_FEATURES))

    # split into the hash and the rest of the token features, embed hash as
    # one-hot, then merge
    def create_tok_hash(x):
        import tensorflow as tf

        return tf.squeeze(tf.slice(x, (0, 0, 0), (-1, -1, 1)), axis=2)

    def create_tok_features(x):
        import tensorflow as tf

        return tf.slice(x, (0, 0, 1), (-1, -1, -1))

    tok_hash = Lambda(create_tok_hash)(indata)
    tok_features = Lambda(create_tok_features)(indata)
    embed = Embedding(config.vocab_size, config.vocab_embed_size)(tok_hash)
    merged = concatenate([embed, tok_features], axis=2)

    f = Flatten()(merged)
    d1 = Dense(
        int(config.window_len * NUM_FEATURES * config.layer_1_size_factor),
        activation="sigmoid",
    )(f)
    d2 = Dropout(config.dropout)(d1)
    d3 = Dense(
        int(config.window_len * NUM_FEATURES * config.layer_2_size_factor),
        activation="sigmoid",
    )(d2)
    d4 = Dropout(config.dropout)(d3)

    if config.num_layers == 3:
        d5 = Dense(
            int(config.window_len * NUM_FEATURES * config.layer_3_size_factor),
            activation="sigmoid",
        )(d4)
        last_layer = Dropout(config.dropout)(d5)
    else:
        last_layer = d4

    preout = Dense(config.window_len * len(TokenType), activation="linear")(last_layer)
    shaped = Reshape((config.window_len, len(TokenType)))(preout)
    outdata = Softmax(axis=-1)(shaped)
    model = Model(inputs=[indata], outputs=[outdata])

    # _missed_token_loss = missed_token_loss(config.penalize_missed)

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=config.learning_rate),
        loss=tf.keras.losses.SparseCategoricalCrossentropy(),
        metrics=["acc"],
    )

    return model


def default_model_name(window_len):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return MODEL_DIR / f"{timestamp}_{git_short_hash()}_{window_len}.model"


def latest_model():
    models = MODEL_DIR.glob("*.model")
    return max(models, key=lambda p: p.stat().st_ctime)


def load_model(model_file=None):
    filepath = Path(model_file) if model_file else latest_model()
    window_len = int(filepath.stem.split("_")[-1])
    model = keras.models.load_model(
        filepath, custom_objects={"_missed_token_loss": missed_token_loss(5)}
    )
    return model, window_len


def save_model(model, config):
    basename = Path(config.model_path) or default_model_name(config.window_len)
    basename.parent.mkdir(parents=True, exist_ok=True)
    model.save(basename)
