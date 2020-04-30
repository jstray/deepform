import re


def is_dollar_amount(s):
    return re.search(r'\$?\d[\d,]+(\.\d\d)?', s) is not None
