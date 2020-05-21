import numpy as np

import util


def token_features(row, config):
    if row:
        c = config
        tokstr = row["token"].upper()
        return [
            (hash(tokstr) % config.vocab_size) if c.use_string else 0,
            float(row["page"]) if c.use_page else 0,
            float(row["x0"]) if c.use_geom else 0,
            float(row["y0"]) if c.use_geom else 0,
            float(len(tokstr)),
            np.mean([c.isdigit() for c in tokstr]),
            util.is_dollar_amount(tokstr) or 0,
            util.log_dollar_amount(tokstr) or 0 if c.use_amount else 0,
        ]
    else:
        return [0 for i in range(config.token_dims)]
