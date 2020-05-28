from uuid import uuid1 as uuid

import pandas as pd

from deepform.convert_to_parquet import convert_csv_to_parquet, doc_count, line_count

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


def random_data_csv(faker, path):
    cols = "slug,page,x0,y0,x1,y1,token,gross_amount".split(",")
    data = [random_training_data_row(faker) for _ in range(100)]
    df = pd.DataFrame(data, columns=cols)
    df = df.sort_values(by="slug page y0 x0".split()).reset_index(drop=True)
    df.to_csv(path, index=False)


def test_line_count(tmp_path):
    test_file = tmp_path / "lines.txt"
    test_file.write_text("\n".join(str(i) for i in range(21)))
    assert line_count(test_file) == 20


def test_doc_count():
    df = pd.DataFrame({"slug": [uuid() for i in range(15)]})
    assert doc_count(df) == 15


def test_convert_csv_to_parquet(faker, tmp_path):
    # Put a random CSV into a temporary directory.
    csv_path = tmp_path / "training.csv"
    pq_path = tmp_path / "parquet"
    random_data_csv(faker, csv_path)

    # Run the conversion code.
    convert_csv_to_parquet(csv_path, pq_path)

    # Check out the index.
    index = pd.read_parquet(pq_path.parent / "doc_index.parquet")
    assert len(index) == 3
    assert set(DOCS) == set(index["slug"])

    # Check out each individual document that was produced.
    for slug in DOCS:
        doc = pd.read_parquet(pq_path / f"{slug}.parquet")
        assert doc["token"].str.len().min() >= 3
        reference = index[index["slug"] == slug].iloc[0]
        assert reference["length"] == len(doc)
        assert reference["best_match"] == doc["gross_amount"].max()
