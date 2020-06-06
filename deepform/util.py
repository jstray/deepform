import logging
import math
import random
import re
import subprocess
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


def dollar_match(predicted, actual):
    """Best-effort matching of dollar amounts, e.g. '$14,123.02' to '14123.02'."""
    return (
        is_dollar_amount(predicted)
        and is_dollar_amount(actual)
        and (normalize_dollars(predicted) == normalize_dollars(actual))
    )


def docrow_to_bbox(t, min_height=10):
    """Create the array pdfplumber expects for bounding boxes from an input namedtuple.

    If `min_height` is set, adjust the minimum size of the bounding boxes to fix the
    cases where pdfplumber has incorrectly underlined rather than boxed in the
    recognized text.
    """
    dims = {k: Decimal(float(getattr(t, k))) for k in ["x0", "y0", "x1", "y1"]}
    if min_height:
        dims["y0"] = min(dims["y1"] - Decimal(min_height), dims["y0"])
    return BoundingBox(**dims)


def config_desc(config):
    """A one-line text string describing the configuration of a run."""
    return (
        "len:{len_train} "
        "win:{window_len} "
        "str:{use_string} "
        "page:{use_page} "
        "geom:{use_geom} "
        "amt:{use_amount} "
        "voc:{vocab_size} "
        "emb:{vocab_embed_size} "
        "steps:{steps_per_epoch}"
    ).format(**config)


def sample(items, n=None, seed=None):
    """Get a sample of `n` items without replacement.

    If n is None, return the input after shuffling it.
    """
    if seed:
        random.seed(seed)
    if n is None:
        n = len(items)
    return random.sample(items, k=n)


def git_short_hash():
    try:
        out = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
        return out.strip().decode("ascii")
    except OSError:
        return "Unknown"
