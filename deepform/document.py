from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from deepform.data.add_features import TokenType
from deepform.features import fix_dtypes

FEATURE_COLS = [
    "tok_id",
    "page",
    "x0",
    "y0",
    "length",
    "digitness",
    "is_dollar",
    "log_amount",
]
NUM_FEATURES = len(FEATURE_COLS)

TOKEN_COLS = [
    "token",
    "x0",
    "y0",
    "x1",
    "y1",
    "page",
    # The following are "match %" for the known fields
    "contract_num",
    "advertiser",
    "flight_from",
    "flight_to",
    "gross_amount",
]


# This sets which field the model is looking for.
SINGLE_CLASS_PREDICTION = "gross_amount"


@dataclass
class Window:
    """A Window just holds views to the arrays held by a Document."""

    tokens: pd.DataFrame
    features: np.ndarray
    labels: np.ndarray

    def __len__(self):
        return len(self.labels)


@dataclass(frozen=True)
class Document:
    slug: str
    # tokens, features, and labels are all aligned with the same indices.
    tokens: pd.DataFrame
    features: np.ndarray
    labels: np.ndarray
    # positive_windows is a list of which (starting) indices have a match.
    positive_windows: np.ndarray
    window_len: int
    label_values: dict[str, str]

    def random_window(self, require_positive=False):
        if require_positive:
            index = np.random.choice(self.positive_windows)
        else:
            index = np.random.randint(len(self))
        return self[index]

    def __getitem__(self, n):
        """Return the `n`th window in the document."""
        k = n + self.window_len
        return Window(self.tokens.iloc[n:k], self.features[n:k], self.labels[n:k])

    def __len__(self):
        """Return the number of windows in the document.

        Note that unless window_len=1, this is less than the number of tokens.
        """
        return len(self.labels) - self.window_len + 1

    def __iter__(self):
        """Iterate over all windows in the document in order."""
        for i in range(len(self)):
            yield self[i]

    def predict_scores(self, model):
        """Use a model to predict labels for each of the document tokens."""
        windowed_features = np.stack([window.features for window in self])
        window_scores = model.predict(windowed_features)

        num_windows = len(self.labels)
        scores = np.zeros(num_windows)
        for i, window_score in enumerate(window_scores):
            scores[i : i + self.window_len] += window_score / self.window_len

        return scores

    def predict_answer(self, model):
        """Score each token and return the text and score of the best match."""
        scores = self.predict_scores(model)
        best_score_idx = np.argmax(scores)
        best_score_text = self.tokens.iloc[best_score_idx]["token"]
        return best_score_text, scores[best_score_idx], scores

    def show_predictions(self, pred_text, pred_score, scores):
        """Predict token scores and print them alongside the tokens and true labels."""
        # pred_text, pred_score, scores = self.predict_answer(model)
        title = f"======={self.slug}======="
        predicted = "predictions (actual / predicted <score>):"
        for name, value in self.label_values.items():
            predicted += f"\t{name}: {pred_text} / {value} <{pred_score}>"
        body = pd.DataFrame(
            {
                "token": self.tokens.token,
                "label": [TokenType(x).name if x else "" for x in self.labels],
                "score": scores,
            }
        )
        body = body.iloc[self.window_len - 1 : 1 - self.window_len]
        return "\n".join([title, predicted, body.to_string()])

    @staticmethod
    def from_parquet(slug, pq_path, config):
        """Load precomputed features from a parquet file and apply a config."""
        df = pd.read_parquet(pq_path)

        df["tok_id"] = (
            np.minimum(df["tok_id"], config.vocab_size - 1) * config.use_string
        )
        df["page"] *= config.use_page
        df["x0"] *= config.use_geom
        df["y0"] *= config.use_geom
        df["log_amount"] *= config.use_amount

        label_values = {}
        for token_type in TokenType:
            if token_type is TokenType.NONE:
                continue
            name = token_type.name.lower()
            label_values[name] = actual_value(df, value_col="token", match_col=name)

        if config.pad_windows:
            df = pad_df(df, config.window_len - 1)
        fix_dtypes(df)

        labels = df["label"] == TokenType[SINGLE_CLASS_PREDICTION.upper()].value

        # Pre-compute which windows have the desired token.
        positive_windows = []
        for i in range(len(df) - config.window_len):
            if labels.iloc[i : i + config.window_len].any():
                positive_windows.append(i)
        assert len(positive_windows) > 0

        return Document(
            slug=slug,
            tokens=df[TOKEN_COLS],
            features=df[FEATURE_COLS].to_numpy(dtype=float),
            labels=labels.to_numpy(dtype=int),
            positive_windows=np.array(positive_windows),
            window_len=config.window_len,
            label_values=label_values,
        )


def pad_df(df, num_rows):
    """Add `num_rows` NaNs to the start and end of a DataFrame."""
    zeros = pd.DataFrame(index=pd.RangeIndex(num_rows))
    return pd.concat([zeros, df, zeros]).reset_index(drop=True)


def actual_value(df, value_col, match_col):
    """Return the best value from `value_col`, as evaluated by `match_col`."""
    index = df[match_col].argmax()
    return df.iloc[index][value_col]
