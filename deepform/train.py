# Data extraction by deep learning, using a fully connected architecture over
# token windows. Engineered to extract total amounts, using a few custom
# features.
# Achieves up to 90% accuracy.
#
# jstray 2019-6-12

import argparse
import os
import re
from collections import defaultdict
from datetime import datetime

import pandas as pd
import wandb
from tensorflow import keras as K
from wandb.keras import WandbCallback

from deepform.common import LOG_DIR, TRAINING_INDEX, WANDB_ENTITY, WANDB_PROJECT
from deepform.data.add_features import LABEL_COLS
from deepform.document_store import DocumentStore
from deepform.logger import logger
from deepform.model import create_model, save_model, windowed_generator
from deepform.pdfs import log_pdf
from deepform.util import config_desc, date_match, dollar_match, loose_match


# Calculate accuracy of answer extraction over num_to_test docs, print
# diagnostics while we do so
def compute_accuracy(model, config, dataset, num_to_test, print_results, log_path):
    n_print = config.render_results_size

    n_docs = min(num_to_test, len(dataset))

    accuracies = defaultdict(int)

    for doc in sorted(dataset.sample(n_docs), key=lambda d: d.slug):
        slug = doc.slug
        answer_texts = doc.label_values

        predict_texts, predict_scores, all_scores = doc.predict_answer(
            model, config.predict_thresh
        )
        answer_texts = [answer_texts[c] for c in LABEL_COLS.keys()]

        doc_output = doc.show_predictions(predict_texts, predict_scores, all_scores)
        # path = log_path / ("right" if match else "wrong")
        log_path.mkdir(parents=True, exist_ok=True)
        with open(log_path / f"{slug}.txt", "w") as predict_file:
            predict_file.write(doc_output)

        if print_results:
            print(f"file_id:{slug}")
        for i, (field, answer_text) in enumerate(doc.label_values.items()):
            predict_text = predict_texts[i]
            predict_score = predict_scores[i]
            match = (
                (predict_score < config.predict_thresh and not answer_text)
                or loose_match(predict_text, answer_text)
                or (field == "gross_amount" and dollar_match(predict_text, answer_text))
                or (
                    field in ("flight_from", "flight_to")
                    and date_match(predict_text, answer_text)
                )
            )

            accuracies[field] += match

            prefix = "✔️" if match else "❌"
            guessed = f'guessed "{predict_text}" with score {predict_score:.3f}'
            correction = "" if match else f', was actually "{answer_text}"'

            if print_results:
                print(f"\t{prefix} {field}: {guessed}{correction}")
                if not match and n_print > 0:
                    log_pdf(
                        doc, predict_score, all_scores[:, i], predict_text, answer_text
                    )
                    n_print -= 1

    return pd.Series(accuracies) / n_docs


# ---- Custom callback to log document-level accuracy ----
class DocAccCallback(K.callbacks.Callback):
    def __init__(self, config, run_timestamp, dataset, logname):
        self.config = config
        self.dataset = dataset
        self.logname = logname
        self.log_path = LOG_DIR / "predictions" / run_timestamp

    def on_epoch_end(self, epoch, logs):
        if epoch >= self.config.epochs - 1:
            # last epoch, sample from all docs and print inference results
            print_results = self.logname == "doc_val_acc"
            test_size = len(self.dataset)
        else:
            # intermediate epoch, small sample and no logger
            print_results = False
            test_size = self.config.doc_acc_sample_size + epoch

        # Avoid sampling tens of thousands of documents on large training sets.
        test_size = min(test_size, self.config.doc_acc_max_sample_size)

        kind = "test" if self.logname == "doc_val_acc" else "train"

        acc = compute_accuracy(
            self.model,
            self.config,
            self.dataset,
            test_size,
            print_results,
            self.log_path / kind / f"{epoch:02d}",
        )
        acc_str = re.sub(r"\s+", " ", acc.to_string())

        print(f"This epoch {self.logname}: {acc_str}")
        wandb.log({self.logname: acc_str})


def main(config):
    config.name = config_desc(config)
    if config.use_wandb:
        run.save()

    print("Configuration:")
    print(config)

    run_ts = datetime.now().isoformat(timespec="seconds").replace(":", "")

    # all_data = load_training_data(config)
    all_documents = DocumentStore.open(index_file=TRAINING_INDEX, config=config)

    # split into validation and training sets
    validation_set, training_set = all_documents.split(percent=config.val_split)
    print(f"Training on {len(training_set)}, validating on {len(validation_set)}")

    model = create_model(config)
    print(model.summary())

    callbacks = [WandbCallback()] if config.use_wandb else []
    callbacks.append(K.callbacks.LambdaCallback(on_epoch_end=lambda *args: print()))
    callbacks.append(DocAccCallback(config, run_ts, training_set, "doc_train_acc"))
    callbacks.append(DocAccCallback(config, run_ts, validation_set, "doc_val_acc"))

    model.fit(
        windowed_generator(training_set, config),
        steps_per_epoch=config.steps_per_epoch,
        epochs=config.epochs,
        callbacks=callbacks,
    )

    if config.save_model:
        model_filepath = save_model(model, config)
        alias = model_filepath.name
        artifact = wandb.Artifact(
            "deepform-model", type="model", metadata={"name": alias}
        )
        artifact.add_dir(
            str(model_filepath)
        )  # TODO: check that this is necessary? What does wandb api expect here?
        run.log_artifact(artifact, aliases=["latest", alias])


if __name__ == "__main__":
    # First read in the initial configuration.
    run = wandb.init(
        project=WANDB_PROJECT,
        entity=WANDB_ENTITY,
        job_type="train",
        allow_val_change=True,
    )
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

    logger.setLevel(config.log_level)

    main(config)
