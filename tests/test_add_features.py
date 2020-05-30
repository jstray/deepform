import pandas as pd

from deepform.add_features import extend_and_write_docs
from deepform.csv_to_parquet import CSV_COL_TYPES
from deepform.features import fraction_digits
from deepform.util import is_dollar_amount, log_dollar_amount
from test_csv_to_parquet import training_docs_data

DOCS = ["doc.1", "doc-2", "doc_3"]


def random_training_data_row(faker):
    x0 = faker.pyfloat(min_value=-1, max_value=600)
    y0 = faker.pyfloat(min_value=-1, max_value=750)
    return {
        "slug": faker.random_element(DOCS),
        "page": faker.pyfloat(min_value=0, max_value=1),
        "x0": x0,
        "y0": y0,
        "x1": x0 + faker.pyfloat(min_value=-1, max_value=20),
        "y1": y0 + faker.pyfloat(min_value=-1, max_value=50),
        "token": faker.pystr(min_chars=1, max_chars=50),
        "gross_amount": faker.pyfloat(min_value=0, max_value=1),
    }


def random_data_parquet(faker, path):

    cols = "slug,page,x0,y0,x1,y1,token,gross_amount".split(",")
    data = [random_training_data_row(faker) for _ in range(100)]
    df = pd.DataFrame(data, columns=cols)
    df = df.sort_values(by="slug page y0 x0".split()).reset_index(drop=True)
    df.to_csv(path, index=False)


def test_convert_csv_to_parquet(faker, tmp_path):
    num_docs = 5

    idx_path = tmp_path / "doc_index.parquet"
    pd_path = tmp_path / "tokenized_docs"

    # Create the source data to start with.
    df = training_docs_data(faker, num_docs, repeat=False)
    df = df.astype(CSV_COL_TYPES)

    # Run the conversion code.
    extend_and_write_docs(df, idx_path)

    # Check out the index.
    index = pd.read_parquet(idx_path)

    assert len(index) == num_docs
    assert set(df.slug) == set(index.index)

    # Check out each individual document that was produced.
    for slug, length, best_match in index.itertuples():
        doc = pd.read_parquet(pd_path / f"{slug}.parquet")
        # Doc features
        assert doc.token.str.len().min() >= 3
        assert length == len(doc)
        assert best_match == doc.gross_amount.max()
        # Row features
        assert (doc.hash == doc.token.apply(hash)).all()
        assert (doc.length == doc.token.str.len()).all()
        assert (doc.digitness == doc.token.apply(fraction_digits)).all()
        assert (doc.is_dollar == doc.token.apply(is_dollar_amount)).all()
        assert (doc.log_amount == doc.token.apply(log_dollar_amount).fillna(0)).all()
