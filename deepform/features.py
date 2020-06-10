import numpy as np
import pandas as pd

from deepform.util import is_dollar_amount, log_dollar_amount

STRING_COLS = ["slug", "token"]
INT_COLS = ["hash", "length"]
FLOAT_COLS = [
    "page",
    "x0",
    "y0",
    "x1",
    "y1",
    "gross_amount",
    "match",
    "digitness",
    "log_amount",
    "str_totals",
    "str_amount",
    "str_gross",
    "str_net",
    "str_contract"
]
BOOL_COLS = ["is_dollar", "label"]


# def fraction_digits(s):
#     """Return the fraction of a string that is composed of digits."""
#     return np.mean([c.isdigit() for c in s]) if isinstance(s, str) else 0.0

# def match_string(a,b):
#     m = fuzz.ratio(a.lower(), b.lower()) / 100.0 
#     return m if m>=0.9 else 0

# def add_base_features(token_df):
#     """Extend a DataFrame with features that can be pre-computed."""
#     df = token_df.copy()
#     df["hash"] = df["token"].apply(hash)
#     df["length"] = df["token"].str.len()
#     df["digitness"] = df["token"].apply(fraction_digits)
#     df["is_dollar"] = df["token"].apply(is_dollar_amount)
#     df["log_amount"] = df["token"].apply(log_dollar_amount)

#     for s in ['amount','totals','gross','net','contract']:
#         df['str_'+s] = df['str_'+s].apply(lambda x: match_string(s,x))

#     return df.fillna(0)


def fix_type(df, col, na_value, dtype, downcast=False):
    if col not in df.columns:
        return
    df[col] = df[col].fillna(na_value).astype(dtype)
    if downcast:
        try:
            df[col] = pd.to_numeric(df[col], downcast=dtype)
        except ValueError:
            print(f"Unable to downcast column {col} as {dtype}")
            print(df[col])


def fix_dtypes(df):
    # Use new-style Pandas string types.
    for col in STRING_COLS:
        fix_type(df, col, na_value="", dtype="string")

    for col in BOOL_COLS:
        fix_type(df, col, na_value=0, dtype="bool")

    for col in INT_COLS:
        fix_type(df, col, na_value=0, dtype="int")

    for col in FLOAT_COLS:
        fix_type(df, col, na_value=0.0, dtype="float", downcast=True)
