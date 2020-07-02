from collections import Counter
from string import ascii_lowercase

import pandas as pd

from deepform.common import DATA_DIR, TOKEN_DIR

VOCAB_FILE = DATA_DIR / "token_frequency.csv"


def clean(token):
    """Convert to lowercase and strip out anything other than ascii letters."""
    return "".join(c for c in token.casefold() if c in ascii_lowercase)


def per_document_tokens():
    """Generator that produces the unique set of tokens for each document."""
    for doc in TOKEN_DIR.glob("*.parquet"):
        yield pd.read_parquet(doc, columns=["token"]).token.apply(clean).unique()


def per_document_token_count():
    counts = Counter()
    for tokens in per_document_tokens():
        counts.update(tokens)
    return counts


def create_frequency_file():
    counts = per_document_token_count()
    counts_df = pd.DataFrame(counts.most_common(), columns=["token", "count"])
    counts_df.to_csv(VOCAB_FILE)


def token_frequencies():
    if not VOCAB_FILE.is_file():
        create_frequency_file()
    return pd.read_csv(VOCAB_FILE)


class Vocabulary:
    def __init__(self):
        vocab = token_frequencies().token
        self.token_ids = {t: i + 1 for i, t in enumerate(vocab)}

    def __getitem__(self, token):
        # Unrecognized words are assigned to 0.
        return self.token_ids.get(clean(token), 0)


def get_token_id(token):
    global _vocabulary_singleton
    try:
        return _vocabulary_singleton[token]
    except NameError:
        _vocabulary_singleton = Vocabulary()
        return _vocabulary_singleton[token]


if __name__ == "__main__":
    create_frequency_file()
