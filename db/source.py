import pandas as pd
from sqlalchemy import create_engine
import tensorflow as tf
import string


charset = string.printable + '\t\n\x00'


def connection(user, password, host="127.0.0.1", port=3306, dbname="deepform"):
    engine = create_engine(
        f"mysql+mysqldb://{user}:{password}@{host}:{port}/{dbname}",
        pool_recycle=3600)
    return engine.connect()


def clean_text(text):
    def clean_char(c):
        if c in charset:
            return c
        else:
            return '\x00'
    return [clean_char(x) for x in text]


def input_generator(conn, num_samples=10, truncate_length=3000):
    # TODO: pass in seed value to rand for deterministic shuffles?
    documents = pd.read_sql(
        f"select * from document where committee != '' order by rand() limit {num_samples};",
        conn
    )
    for document in documents.itertuples():
        doc_id = document.dc_slug
        # TODO: read all tokens for a given batch of docs at a time
        tokens = pd.read_sql(
            f"select * from token where dc_slug = '{doc_id}';",
            conn
        )
        for token in tokens.itertuples():
            yield document.dc_slug, token.token, token.x0, token.y0, token.page, document.committee, document.gross_amount_usd


def dataset(conn, buffer_size=100):
    gen = lambda: input_generator(conn)
    ds = tf.data.Dataset.from_generator(
        gen,
        args=[],
        output_types=(tf.string, tf.string, tf.double, tf.double, tf.double, tf.string, tf.double),
    )
    return ds.prefetch(buffer_size)


if __name__ == '__main__':
    conn = connection("root", "changeme")
    ds = dataset(conn)
    for d in ds:
        print(d)
        print("*****")
