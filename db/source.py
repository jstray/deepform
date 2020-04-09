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
    documents = pd.read_sql(
        f"select * from document where committee != '' order by rand() limit {num_samples};",
        conn
    )
    for document in documents.itertuples():
        doc_id = document.dc_slug
        tokens = pd.read_sql(
            f"select * from token where dc_slug = '{doc_id}';",
            conn
        )
        text = ' '.join([str(token) for token in tokens['token']])
        # yield clean_text(text), clean_text(document.committee)
        yield text, document.committee


def dataset(conn, buffer_size=100):
    gen = lambda: input_generator(conn)
    ds = tf.data.Dataset.from_generator(
        gen,
        args=[],
        output_types=(tf.string, tf.string),
    )
    return ds.prefetch(buffer_size)


if __name__ == '__main__':
    conn = connection("root", "changeme")
    ds = dataset(conn)
    for d in ds.take(10):
        print(d)
        print("*****")
