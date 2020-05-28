import string

import pandas as pd
from sqlalchemy import create_engine

charset = string.printable + "\t\n\x00"


def connection(user, password, host="127.0.0.1", port=3306, dbname="deepform"):
    engine = create_engine(
        f"mysql+mysqldb://{user}:{password}@{host}:{port}/{dbname}", pool_recycle=3600
    )
    return engine.connect()


def clean_text(text):
    def clean_char(c):
        if c in charset:
            return c
        else:
            return "\x00"

    return [clean_char(x) for x in text]


def input_generator(conn, max_docs=10, truncate_length=3000):
    documents = pd.read_sql(
        f"select * from document "
        f"where committee != '' order by rand() limit {max_docs};",
        conn,
    )
    for document in documents.itertuples():
        doc_id = document.dc_slug
        tokens = pd.read_sql(f"select * from token where dc_slug = '{doc_id}';", conn)
        text = " ".join([str(token) for token in tokens["token"]])
        # yield clean_text(text), clean_text(document.committee)
        yield text, document.committee


def input_docs(conn, max_docs=10, minimum_doc_length=30):
    try:
        emitted_docs = 0
        raw_conn = conn.engine.raw_connection()
        cursor = raw_conn.cursor()
        cursor.execute(
            "select dc_slug, committee, gross_amount_usd from document where committee \
            != '' order by rand()"
        )
        while emitted_docs < max_docs:
            doc = cursor.fetchone()
            if doc:
                dc_slug, committee, gross_amount_usd = (doc[0], doc[1], doc[2])
                rows = pd.read_sql(
                    f"select * from token where dc_slug = '{dc_slug}';", conn
                )
                if len(rows) < minimum_doc_length:
                    continue
                else:
                    yield dc_slug, committee, gross_amount_usd, rows
                    emitted_docs += 1
            else:
                break
    finally:
        conn.close()


if __name__ == "__main__":
    conn = connection("root", "changeme")
    docs = input_docs(conn)
    for doc in docs:
        print(doc)
        print("*****")
