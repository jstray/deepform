import pandas as pd

STRING_COLS = ["slug", "token"]
INT_COLS = ["tok_id", "length", "label"]
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
]
BOOL_COLS = ["is_dollar"]


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
