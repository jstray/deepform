import util
import numpy as np


def token_features(row, vocab_size):
    tokstr = row['token'].upper()
    return [hash(tokstr) % vocab_size,
            float(row['page']),
            float(row['x0']),
            float(row['y0']),
            float(len(tokstr)),
            float(np.mean([c.isdigit() for c in tokstr])),
            float(util.is_dollar_amount(tokstr))]
