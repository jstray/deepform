import re
from collections import namedtuple
from decimal import Decimal, InvalidOperation

BoundingBox = namedtuple("BoundingBox", ["x0", "y0", "x1", "y1"])


def is_dollar_amount(s):
    return re.match(r"^\$?[\d,]+(\.\d\d)?$", s) != None


def dollar_amount(s):
    if is_dollar_amount(s):
        return float(s.replace("$", "").replace(",", ""))
    else:
        return 0


def normalize_dollars(s) -> str:
    """Given a string like '$56,333.1' return the string '5633.10'."""
    try:
        return str(round(Decimal(s.replace("$", "").replace(",", "")), 2))
    except InvalidOperation:
        return ""


def docrow_to_bbox(t, min_height=10):
    """Create the array pdfplumber expects for bounding boxes from an input dict.

    If `min_height` is set, adjust the minimum size of the bounding boxes to fix the
    cases where pdfplumber has incorrectly underlined rather than boxed in the
    recognized text.
    """
    dims = {k: Decimal(t[k]) for k in ["x0", "y0", "x1", "y1"]}
    if min_height:
        dims["y0"] = min(dims["y1"] - Decimal(min_height), dims["y0"])
    return BoundingBox(**dims)
