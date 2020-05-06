import util
import numpy as np



def token_features(row, config):
    if row:
        tokstr = row['token'].upper()
        return [ hash(tokstr) % config.vocab_size,
                 float(row['page']), 
                 float(row['x0']),
                 float(row['y0']), 
                 float(len(tokstr)),
                 float(np.mean([c.isdigit() for c in tokstr])),
                 float(util.is_dollar_amount(tokstr)),
                 util.dollar_amount(tokstr) if config.amount_feature else 0 ]
    else:
        return [0 for i in range(config.token_dims)]