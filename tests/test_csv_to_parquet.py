import random

import pandas as pd

from deepform.data.csv_to_parquet import CSV_COL_TYPES, csv_to_parquet


def random_training_data_row(faker):
    x0 = faker.pyfloat(min_value=-1, max_value=600)
    y0 = faker.pyfloat(min_value=-1, max_value=750)
    return {
        "slug": None,
        "page": faker.pyfloat(min_value=0, max_value=1),
        "x0": x0,
        "y0": y0,
        "x1": x0 + faker.pyfloat(min_value=-1, max_value=20),
        "y1": y0 + faker.pyfloat(min_value=-1, max_value=50),
        "token": faker.pystr(min_chars=1, max_chars=50),
        "gross_amount": faker.pyfloat(min_value=0, max_value=1),
    }


def random_doc_data(faker):
    num_tokens = faker.pyint(min_value=1, max_value=200)
    df = pd.DataFrame([random_training_data_row(faker) for _ in range(num_tokens)])
    df.slug = faker.slug()
    return df


def training_docs_data(faker, doc_count, repeat=True):
    docs = [random_doc_data(faker) for _ in range(doc_count)]
    if repeat:
        docs = random.choices(docs, k=2 * doc_count)
    return pd.concat(docs)


def test_convert_csv_to_parquet(faker, tmp_path):
    # Put a random CSV into a temporary directory.
    csv_path = tmp_path / "training.csv"
    pq_path = tmp_path / "training.parquet"

    # Produce some random data.
    docs = training_docs_data(faker, doc_count=5, repeat=True)

    # Write to our temporary csv.
    docs.to_csv(csv_path, index=False)

    # Run the conversion code.
    csv_to_parquet(csv_path, pq_path)

    # Read the results.
    result = pd.read_parquet(pq_path)

    # All the slugs were maintained.
    assert set(docs.slug) == set(result.slug)

    # But all the duplicates were dropped.
    assert len(docs.drop_duplicates()) == len(result)

    # And all the types are what we expect.
    assert (docs.astype(CSV_COL_TYPES).dtypes == result.dtypes).all()
