#!/bin/usr/python3
# ----------------------------------------------------------
# Token-level LSTM model;
# Cleaned up by: Stacey Svetlichnaya 
#
# ----------------------------------------------------------

import argparse
import numpy as np
import os
import pandas as pd
import tensorflow as tf
import warnings

from tensorflow.keras import layers, activations, models, preprocessing, utils
import wandb
from wandb.keras import WandbCallback


DATASET = "train.csv"
TRAIN_DATA = "./training_data/" + DATASET + ".csv"

def load_files(filenames):
    yield pd.read_csv(filenames)

def process_data():
    # slugs and processed tokens
    df = pd.concat(load_files(TRAIN_DATA))
    df['processed'] = df['processed'].astype(str) # Make sure we are dealing with strings

    # Grab our input and target training data
    input_texts = df['processed'].to_list()
    target_texts = df['committee'].to_list()

    # Set '<START> ' as the "start sequence" character
    # for the targets, and ' <END>' as "end sequence" character.
    target_texts = ['<START> ' + s + ' <END>' for s in target_texts]
    print("num input texts: ", len(input_texts))
    print("num output labels: ", len(target_texts))

    # Tokenization 
    tokenizer = preprocessing.text.Tokenizer()
    tokenizer.fit_on_texts( input_texts + target_texts )
    VOCAB_SIZE = len( tokenizer.word_index )+1
    print( 'VOCAB SIZE : {}'.format( VOCAB_SIZE ))

    vocab = []
    for word in tokenizer.word_index:
    vocab.append( word )

    # format input text training data for encoder, padding to max len
    tokenized_inputs = tokenizer.texts_to_sequences( input_texts )
    maxlen_inputs = max( [ len(x) for x in tokenized_inputs ] )
    padded_inputs = preprocessing.sequence.pad_sequences(tokenized_inputs,
                                                    maxlen=maxlen_inputs,
                                                    padding='post' )
    encoder_input_data = np.array( padded_inputs )
    # one row for each input text, as long as the maximum length input text
    print("Encoder input shape: {}".format(encoder_input_data.shape , maxlen_inputs ))

    # format output labels training data for decoder, padding to max len
    tokenized_targets = tokenizer.texts_to_sequences( target_texts )
    maxlen_targets = max( [ len(x) for x in tokenized_targets ] )
    padded_targets = preprocessing.sequence.pad_sequences(tokenized_targets,
                                                      maxlen=maxlen_targets, padding='post' )
    decoder_input_data = np.array( padded_targets )
    # one row for each output label, as long as the max len output label
    print("Decoder input shape: {}".format(decoder_input_data.shape , maxlen_targets ))

    # decoder_output_data
    tokenized_answers = tokenizer.texts_to_sequences( target_texts )
    # drops the start token?
    for i in range(len(tokenized_answers)) :
    tokenized_answers[i] = tokenized_answers[i][1:]
    padded_targets = preprocessing.sequence.pad_sequences( tokenized_answers,
                                                      maxlen=maxlen_targets , padding='post' )
    onehot_answers = utils.to_categorical( padded_targets , VOCAB_SIZE )
    decoder_output_data = np.array( onehot_answers )
    # one row for each output label encoded into vocab, as long as the longest output label in tokens
    print("Decoder output data shape: {}".format(decoder_output_data.shape ))
    return encoder_input_data, decoder_input_data, decoder_output_data, VOCAB_SIZE

def seq2seq_model(cfg):
    encoder_inputs = tf.keras.layers.Input(shape=( None , ))
    encoder_embedding = tf.keras.layers.Embedding( cfg.vocab_size, cfg.num_units , mask_zero=True ) (encoder_inputs)
    encoder_outputs , state_h , state_c = tf.keras.layers.LSTM( cfg.num_units, return_state=True )( encoder_embedding )
    encoder_states = [ state_h , state_c ]

    decoder_inputs = tf.keras.layers.Input(shape=( None ,  ))
    decoder_embedding = tf.keras.layers.Embedding(cfg.vocab_size, cfg.num_units, mask_zero=True) (decoder_inputs)
    decoder_lstm = tf.keras.layers.LSTM(cfg.num_units, return_state=True , return_sequences=True )
    decoder_outputs , _ , _ = decoder_lstm ( decoder_embedding , initial_state=encoder_states )
    decoder_dense = tf.keras.layers.Dense(cfg.vocab_size, activation=tf.keras.activations.softmax ) 
    output = decoder_dense ( decoder_outputs )

    model = tf.keras.models.Model([encoder_inputs, decoder_inputs], output )
    model.compile(optimizer=cfg.optimizer, loss='categorical_crossentropy', metrics=['acc'])

    return model

def train(args):
    encoder_input, decoder_input, decoder_output, VOCAB_SIZE = process_data()
    wb_config = {
        "model_type" : "word seq2seq",
        "batch_size" : args.batch_size,
        "num_units" : args.num_units,
        "num_epochs" : args.epochs,
        "optimizer"  : args.optimizer,
        "vocab_size" : VOCAB_SIZE,
        "num_train" : encoder_input.shape[0],
        "max_len_input" : encoder_input.shape[1],
        "max_len_output" : decoder_input.shape[1],
        "dataset" : DATASET
    }

    wandb.init(project="seq2seq_lstm_test", entity="deepform", name=args.model_name, config=wb_config) 
    cfg = wandb.config
    model = seq2seq_model(cfg)
    model.fit([encoder_input, decoder_input], decoder_output,
          batch_size=cfg.batch_size, epochs=cfg.num_epochs,
          validation_split=0.2,
          callbacks=[WandbCallback()]) 
    model.save("long_test_e_75.h5")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "-m",
        "--model_name",
        type=str,
        default="",
        help="Name of this model/run (model will be saved to this file)")

    parser.add_argument(
        "-b",
        "--batch_size",
        type=int,
        default=64,
        help="Batch size") 

    parser.add_argument(
        "-n",
        "--num_units",
        type=int,
        default=200,
        help="Number of units in LSTM")

    parser.add_argument(
        "-e",
        "--epochs",
        type=int,
        default=5,
        help="Number of training epochs")

    parser.add_argument(
        "-o",
        "--optimizer",
        type=str,
        default="rmsprop",
        help="Learning optimizer")

    parser.add_argument(
        "-q",
        "--dry_run",
        action="store_true",
        help="Dry run (do not log to wandb)")

    args = parser.parse_args()

    # easier testing--don't log to wandb if dry run is set
    if args.dry_run:
        os.environ['WANDB_MODE'] = 'dryrun'

    train(args)
