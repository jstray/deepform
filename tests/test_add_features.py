from datetime import date, timedelta

import pandas as pd
from babel.numbers import format_currency

from deepform.data.add_features import (
    extend_and_write_docs,
    fraction_digits,
    pq_index_and_dir,
)
from deepform.data.create_vocabulary import get_token_id
from deepform.util import is_dollar_amount, log_dollar_amount

COL_TYPES = {
    "page": "f4",  # 32-bit float.
    "x0": "f4",
    "y0": "f4",
    "x1": "f4",
    "y1": "f4",
    "token": "string",  # Pandas 1.x string type.
}


def random_dollar_amount(faker):
    amount = round(faker.pyfloat(min_value=0, max_value=100000), 2)
    return format_currency(amount, "USD", locale="en_US")


def random_date(faker, start_date=date(2020, 1, 1), end_date=date(2020, 12, 31)):
    days = (end_date - start_date).days
    day = faker.pyint(min_value=0, max_value=days)
    return start_date + timedelta(days=day)


def random_training_data_row(faker):
    x0 = faker.pyfloat(min_value=-1, max_value=600)
    y0 = faker.pyfloat(min_value=-1, max_value=750)
    return {
        "page": faker.pyfloat(min_value=0, max_value=1),
        "x0": x0,
        "y0": y0,
        "x1": x0 + faker.pyfloat(min_value=-1, max_value=20),
        "y1": y0 + faker.pyfloat(min_value=-1, max_value=50),
        "token": faker.pystr(min_chars=1, max_chars=50),
    }


def random_doc_data(faker):
    num_tokens = faker.pyint(min_value=1, max_value=500)
    df = pd.DataFrame([random_training_data_row(faker) for _ in range(num_tokens)])
    return df.astype(COL_TYPES)


def create_tokens_and_manifest(faker, src_path, manifest_path, num_docs=5):
    src_path.mkdir(parents=True, exist_ok=True)

    docs = {faker.slug(): random_doc_data(faker) for _ in range(num_docs)}
    manifest = []

    for slug, doc in docs.items():
        doc.to_parquet(src_path / f"{slug}.parquet", compression="lz4", index=False)
        manifest.append(
            {
                "file_id": slug,
                "contract_num": faker.isbn10(),
                "advertiser": faker.company(),
                "flight_from": random_date(faker),
                "flight_to": random_date(faker),
                "gross_amount": random_dollar_amount(faker),
            }
        )

    return pd.DataFrame(manifest)


def test_add_features_to_labeled_parquet(faker, tmp_path):
    num_docs = 5
    src_path = tmp_path / "tokenized"
    manifest = create_tokens_and_manifest(faker, src_path, num_docs)

    idx_path = tmp_path / "doc_index.parquet"
    idx_path, pq_path = pq_index_and_dir(idx_path)

    # Run the conversion code.
    extend_and_write_docs(src_path, manifest, idx_path, pq_path, 1)

    # Check out the index.
    index = pd.read_parquet(idx_path)

    assert len(index) == num_docs
    assert set(manifest.file_id) == set(index.index)

    # Check out each individual document that was produced.
    for row in index.itertuples():
        doc = pd.read_parquet(pq_path / f"{row.Index}.parquet")
        # Doc features
        assert doc.token.str.len().min() >= 3
        assert row.length == len(doc)
        assert row.best_match_gross_amount == doc.gross_amount.max()
        assert row.best_match_contract_num == doc.contract_num.max()

        # Row features
        assert (doc.tok_id == doc.token.apply(get_token_id)).all()
        assert (doc.length == doc.token.str.len()).all()
        assert (doc.digitness == doc.token.apply(fraction_digits)).all()
        assert (doc.is_dollar == doc.token.apply(is_dollar_amount)).all()
        assert (doc.log_amount == doc.token.apply(log_dollar_amount).fillna(0)).all()
