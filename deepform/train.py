# Data extraction by deep learning, using a fully connected architecture over
# token windows. Engineered to extract total amounts, using a few custom
# features.
# Achieves up to 90% accuracy.
#
# jstray 2019-6-12

import argparse
import logging
import os

import keras as K
import wandb
from wandb.keras import WandbCallback

from deepform.data.add_features import DOC_INDEX
from deepform.document_store import DocumentStore
from deepform.model import create_model, predict_answer, save_model, windowed_generator
from deepform.pdfs import log_pdf
from deepform.util import config_desc, dollar_match


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

        match = dollar_match(predict_text, answer_text)

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

    if config.save_model:
        save_model(model, config)


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
