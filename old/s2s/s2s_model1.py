from __future__ import print_function

import math
import string

import numpy as np
import pandas as pd
from tensorflow.python.keras.layers import LSTM, Dense, Input
from tensorflow.python.keras.models import Model
from wandb.keras import WandbCallback

batch_size = 100  # Batch size for training.
epochs = 50  # Number of epochs to train for.
latent_dim = 256  # Latent dimensionality of the encoding space.
num_samples = 4000  # Number of samples to train on.
test_outputs = 20

saved_model = "s2s_politics1_4_2_20_first_model_outputting_committees.h5"
trainmode = False
beamsearch = True

# Fixed character set for 1-hot encoding of inputs and outputs
# \t=start, \n=stop, \x00=unknown character
charset = string.printable + "\t\n\x00"

num_encoder_tokens = len(charset)
num_decoder_tokens = num_encoder_tokens

input_token_index = dict([(char, i) for i, char in enumerate(charset)])
target_token_index = dict([(char, i) for i, char in enumerate(charset)])


# Reverse-lookup token index to decode sequences back to
# something readable.
reverse_input_char_index = dict((i, char) for char, i in input_token_index.items())
reverse_target_char_index = dict((i, char) for char, i in target_token_index.items())
reverse_target_char_index[95] = "\t"
reverse_target_char_index[96] = "\n"


def clean_text(text):
    def clean_char(c):
        if c in charset:
            return c
        else:
            return "\x00"

    return [clean_char(x) for x in text]


# Load training data and encode into 1-hot tensors
def BuildInputTensor():

    train = "../source/training.csv"
    filings = "../source/ftf-all-filings.tsv"

    # docs = 200000
    truncate_length = 3000

    dft = pd.read_csv(train)  # , nrows = docs)
    dff = pd.read_csv(filings, sep="\t")

    df_all = pd.merge(
        left=dft, right=dff, how="left", left_on="slug", right_on="dc_slug"
    )
    # df_all = df_all[['slug', 'page', 'x0', 'y0', 'x1', 'y1', 'token', 'gross_amount_x', 'committee']]
    df_all = df_all[["slug", "token", "committee"]]

    df_group = (
        df_all.groupby(["slug", "committee"])["token"]
        .apply(lambda a: " ".join([str(x) for x in a]))
        .reset_index()
    )
    print(df_group.shape)
    print("number of documents")

    df_group["text"] = df_group["token"].str.slice(0, truncate_length)
    df_group["committee"] = "\t" + df_group["committee"] + "\n"

    df_group.drop(["token"], axis=1)

    print(df_group["committee"][:3])

    target_texts = df_group["committee"][:num_samples]
    input_texts = df_group["text"][:num_samples]

    # ---------------------------------

    max_encoder_seq_length = max([len(txt) for txt in input_texts])
    max_decoder_seq_length = max([len(txt) for txt in target_texts])

    print("Number of unique input chars:", num_encoder_tokens)
    print("Number of unique output cahrs:", num_decoder_tokens)
    print("Max sequence length for inputs:", max_encoder_seq_length)
    print("Max sequence length for outputs:", max_decoder_seq_length)

    encoder_input_data = np.zeros(
        (len(input_texts), max_encoder_seq_length, num_encoder_tokens), dtype="float32"
    )
    decoder_input_data = np.zeros(
        (len(input_texts), max_decoder_seq_length, num_decoder_tokens), dtype="float32"
    )
    decoder_target_data = np.zeros(
        (len(input_texts), max_decoder_seq_length, num_decoder_tokens), dtype="float32"
    )

    for i, (input_text, target_text) in enumerate(zip(input_texts, target_texts)):
        input_text = clean_text(input_text)
        for t, char in enumerate(input_text):
            encoder_input_data[i, t, input_token_index[char]] = 1.0
        encoder_input_data[i, t + 1 :, input_token_index[" "]] = 1.0
        target_text = clean_text(target_text)
        for t, char in enumerate(target_text):
            # decoder_target_data is ahead of decoder_input_data by one
            # timestep
            decoder_input_data[i, t, target_token_index[char]] = 1.0
            if t > 0:
                # decoder_target_data will be ahead by one timestep
                # and will not include the start character.
                decoder_target_data[i, t - 1, target_token_index[char]] = 1.0
    #       decoder_input_data[i, t + 1:, target_token_index[' ']] = 1.
    #       decoder_target_data[i, t:, target_token_index[' ']] = 1.

    return (
        encoder_input_data,
        max_decoder_seq_length,
        max_encoder_seq_length,
        decoder_input_data,
        decoder_target_data,
        input_texts,
        target_texts,
    )


(
    encoder_input_data,
    max_decoder_seq_length,
    max_encoder_seq_length,
    decoder_input_data,
    decoder_target_data,
    input_texts,
    target_texts,
) = BuildInputTensor()

# wandb.init(project="seq2seq_lstm_char_test", entity="deepform", name="test1", config = {"model_type" : "lstm_seq2seq_char_test", "batch_size" : 50, "vocab_size": num_encoder_tokens})


# Define an input sequence and process it.
encoder_inputs = Input(shape=(None, num_encoder_tokens))

encoder = LSTM(latent_dim, return_state=True)
encoder_outputs, state_h, state_c = encoder(encoder_inputs)

# We discard `encoder_outputs` and only keep the states.
encoder_states = [state_h, state_c]

# Set up the decoder, using `encoder_states` as initial state.
decoder_inputs = Input(shape=(None, num_decoder_tokens))

# We set up our decoder to return full output sequences,
# and to return internal states as well. We don't use the
# return states in the training model, but we will use them in inference.
decoder_lstm = LSTM(latent_dim, return_sequences=True, return_state=True)
decoder_outputs, _, _ = decoder_lstm(decoder_inputs, initial_state=encoder_states)
decoder_dense = Dense(num_decoder_tokens, activation="softmax")
decoder_outputs = decoder_dense(decoder_outputs)

# Define the model that will turn
# `encoder_input_data` & `decoder_input_data` into `decoder_target_data`
model = Model([encoder_inputs, decoder_inputs], decoder_outputs,)


if trainmode:
    # Run training
    model.compile(
        optimizer="rmsprop", loss="categorical_crossentropy", metrics=["accuracy"]
    )

    model.fit(
        [encoder_input_data, decoder_input_data],
        decoder_target_data,
        batch_size=batch_size,
        epochs=epochs,
        validation_split=0.2,
        callbacks=[WandbCallback()],
    )

    # Save model
    model.save("s2s_politics1.h5")

else:
    model.load_weights(saved_model, by_name=True)

# Next: inference mode (sampling).
# Here's the drill:
# 1) encode input and retrieve initial decoder state
# 2) run one step of decoder with this initial state
# and a "start of sequence" token as target.
# Output will be the next target token
# 3) Repeat with the current target token and current states

# Define sampling models
encoder_model = Model(encoder_inputs, encoder_states)
print("Encoder Model:")
encoder_model.summary()

decoder_state_input_h = Input(shape=(latent_dim,))
decoder_state_input_c = Input(shape=(latent_dim,))
decoder_states_inputs = [decoder_state_input_h, decoder_state_input_c]

decoder_outputs, state_h, state_c = decoder_lstm(
    decoder_inputs, initial_state=decoder_states_inputs
)
decoder_states = [state_h, state_c]
decoder_outputs = decoder_dense(decoder_outputs)
decoder_model = Model(
    [decoder_inputs] + decoder_states_inputs, [decoder_outputs] + decoder_states
)
print("Decoder Model:")
decoder_model.summary()


def decode_sequence(input_seq):
    # Encode the input as state vectors.
    states_value = encoder_model.predict(input_seq)

    # Generate empty target sequence of length 1.
    target_seq = np.zeros((1, 1, num_decoder_tokens))
    # Populate the first character of target sequence with the start character.
    target_seq[0, 0, target_token_index["\t"]] = 1.0

    # Sampling loop for a batch of sequences
    # (to simplify, here we assume a batch of size 1).
    stop_condition = False
    decoded_sentence = ""
    while not stop_condition:
        output_tokens, h, c = decoder_model.predict([target_seq] + states_value)

        # Sample a token
        sampled_token_index = np.argmax(output_tokens[0, -1, :])
        sampled_char = reverse_target_char_index[sampled_token_index]
        decoded_sentence += sampled_char

        # Exit condition: either hit max length
        # or find stop character.

        # old version, no print statement
        # if (sampled_char == '\n' or
        #    len(decoded_sentence) > max_decoder_seq_length):
        #    stop_condition = True

        if sampled_char == "\n":
            print("Stop character reached.")
            stop_condition = True

        if len(decoded_sentence) > max_decoder_seq_length:
            print("Max sentence length reached.")
            stop_condition = True

        # Update the target sequence (of length 1).
        target_seq = np.zeros((1, 1, num_decoder_tokens))
        target_seq[0, 0, sampled_token_index] = 1.0

        # Update states
        states_value = [h, c]

    return decoded_sentence


def decode_sequence_beam(input_seq):

    beamwidth = 5
    live_strings = [("", 0, 0)]
    dead_strings = []

    # Encode the input as state vectors.
    states_value = encoder_model.predict(input_seq)

    # Generate empty target sequence of length 1.
    target_seq = np.zeros((len(live_strings), 1, num_decoder_tokens))
    # Populate the first character of target sequence with the start character.
    target_seq[0, 0, target_token_index["\t"]] = 1.0

    # Sampling loop for a batch of sequences
    # (to simplify, here we assume a batch of size beamwidth).

    step_counter = 0

    while len(live_strings) > 0 and step_counter < max_decoder_seq_length:
        # print(f'step {step_counter}')
        # print(f'{len(live_strings)} live strings')
        # print('Current Sentences:')
        # for sentence, prob, idx in live_strings:
        #    print(sentence + ' ' + str(math.exp(prob)))

        output_tokens, h, c = decoder_model.predict([target_seq] + states_value)

        new_live_strings = []

        # Loop over live strings
        for i in range(len(live_strings)):
            prefix, logprob, old_index = live_strings[i]

            # Loop over output chars
            for j in range(num_decoder_tokens):
                new_live_strings.append(
                    (
                        prefix + reverse_target_char_index[j],
                        logprob + math.log(1e-100 + output_tokens[i, -1, j]),
                        i,
                    )
                )

        dead_strings.extend([l for l in new_live_strings if l[0][-1] == "\n"])

        new_live_strings = [k for k in new_live_strings if k[0][-1] != "\n"]
        new_live_strings = sorted(new_live_strings, key=lambda x: x[1], reverse=True)[
            :beamwidth
        ]

        # Update the target sequence (of length 1).
        target_seq = np.zeros((len(new_live_strings), 1, num_decoder_tokens))
        states_h = np.zeros((len(new_live_strings), latent_dim))
        states_c = np.zeros((len(new_live_strings), latent_dim))

        for i in range(len(new_live_strings)):
            string, prob, index = new_live_strings[i]
            target_seq[i, 0, target_token_index[string[-1]]] = 1.0
            states_h[i] = h[index]
            states_c[i] = c[index]
        states_value = [states_h, states_c]

        # Update states
        live_strings = new_live_strings
        step_counter += 1

    # length normalization, and drop state index
    dead_strings = [(s, p / len(s)) for (s, p, i) in dead_strings]
    return sorted(dead_strings, key=lambda x: x[1], reverse=True)[:beamwidth]


for seq_index in range(test_outputs):
    # Take one sequence (part of the training set)
    # for trying out decoding.
    input_seq = encoder_input_data[seq_index : seq_index + 1]

    print("-----")
    print("Input sentence:", input_texts[seq_index])
    print("Target Sentence:", target_texts[seq_index])
    if beamsearch:
        decoded_sentences = decode_sequence_beam(input_seq)

        print("Decoded Sentences:")
        for sentence, prob in decoded_sentences:
            print(sentence + " " + str(math.exp(prob)))

    else:
        decoded_sentence = decode_sequence(input_seq)
        print("Decoded Sentence:", decoded_sentence)
