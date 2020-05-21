import logging
import math
import re
from collections import namedtuple
from decimal import Decimal, InvalidOperation

BoundingBox = namedtuple("BoundingBox", ["x0", "y0", "x1", "y1"])


def is_dollar_amount(s):
    return bool(re.search(r"\d", s) and re.fullmatch(r"\$?\d*(,\d\d\d)*(\.\d\d)?", s))


def dollar_amount(s):
    if is_dollar_amount(s):
        try:
            return float(s.replace("$", "").replace(",", ""))
        except ValueError:
            logging.error(f"'{s}' could not be converted to a dollar amount.")
    return None


def log_dollar_amount(s):
    """Return the logarithm of 1 + a non-negative dollar amount."""
    d = dollar_amount(s)
    return math.log(d + 1) if d and d > 0 else None


def normalize_dollars(s) -> str:
    """Return a string of a number rounded to two digits (or None if not possible).
    
    Given a string like '$56,333.1' return the string '5633.10'.
    """
    try:
        return str(round(Decimal(s.replace("$", "").replace(",", "")), 2))
    except InvalidOperation:
        return None


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
