import csv


def input_docs(max_docs=None, source_data="source/training.csv"):
    incsv = csv.DictReader(open(source_data, mode='r'))

    # Reconstruct documents by concatenating all rows with the same slug
    active_slug = None
    doc_rows = []
    num_docs = 0

    for row in incsv:
        # throw out tokens that are too short, they won't help us
        token = row['token']
        if len(token) < 3:
            continue

        if row['slug'] != active_slug:
            if active_slug:
                yield doc_rows
                num_docs += 1
                if max_docs and num_docs >= max_docs:
                    return
            doc_rows = [row]
            active_slug = row['slug']
        else:
            doc_rows.append(row)

    yield doc_rows


if __name__ == "__main__":
    docs = [doc for doc in input_docs(max_docs=1)]
    print(docs)
