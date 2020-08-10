import pandas as pd

from deepform.data.add_features import (
    extend_and_write_docs,
    fraction_digits,
    pq_index_and_dir,
)
from deepform.data.create_vocabulary import get_token_id
from deepform.util import is_dollar_amount, log_dollar_amount
from test_csv_to_parquet import random_doc_data


def test_add_features_to_labeled_parquet(faker, tmp_path):
    num_docs = 5

    src_path = tmp_path / "labeled"
    src_path.mkdir(parents=True, exist_ok=True)
    idx_path = tmp_path / "doc_index.parquet"
    idx_path, pq_path = pq_index_and_dir(idx_path)

    # Create the source data to start with.
    docs = {}
    for _ in range(num_docs):
        doc = random_doc_data(faker)
        docs[doc.slug[0]] = doc.drop("slug", axis=1)

    # Write the data to the temp files `extend_and_write_docs` expects.
    for slug, doc in docs.items():
        doc.to_parquet(src_path / f"{slug}.parquet", compression="lz4", index=False)

    # Run the conversion code.
    extend_and_write_docs(src_path, idx_path, pq_path)

    # Check out the index.
    index = pd.read_parquet(idx_path)

    assert len(index) == num_docs
    assert set(docs.keys()) == set(index.index)

    # Check out each individual document that was produced.
    for slug, length, best_match in index.itertuples():
        doc = pd.read_parquet(pq_path / f"{slug}.parquet")
        # Doc features
        assert doc.token.str.len().min() >= 3
        assert length == len(doc)
        assert best_match == doc.gross_amount.max()
        # Row features
        assert (doc.tok_id == doc.token.apply(get_token_id)).all()
        assert (doc.length == doc.token.str.len()).all()
        assert (doc.digitness == doc.token.apply(fraction_digits)).all()
        assert (doc.is_dollar == doc.token.apply(is_dollar_amount)).all()
        assert (doc.log_amount == doc.token.apply(log_dollar_amount).fillna(0)).all()
