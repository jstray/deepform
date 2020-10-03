import math
import random
import re
import subprocess
from collections import namedtuple
from datetime import datetime
from decimal import Decimal, InvalidOperation

from fuzzywuzzy import fuzz

from deepform.logger import logger

BoundingBox = namedtuple("BoundingBox", ["x0", "y0", "x1", "y1"])

_whitespace = re.compile(r"\s")


def simple_string(s):
    """Lowercase and remove whitespace from a string."""
    return _whitespace.sub("", s.casefold()) if isinstance(s, str) else ""


def num_digits(s):
    return sum(c.isdigit() for c in s)


def loose_match(s1, s2):
    """Match two strings irrespective of case and whitespace."""
    return simple_string(s1) == simple_string(s2)


def default_similarity(lhs, rhs):
    return fuzz.ratio(simple_string(lhs), simple_string(rhs)) / 100


def is_dollar_amount(s):
    try:
        return num_digits(s) > 0 and bool(re.match(r"^\$?\d*(,\d\d\d)*(\.\d\d)?$", s))
    except TypeError:
        return False


def dollar_amount(s):
    if is_dollar_amount(s):
        try:
            return float(s.replace("$", "").replace(",", ""))
        except ValueError:
            logger.error(f"'{s}' could not be converted to a dollar amount.")
    return None


def dollar_similarity(lhs, rhs):
    lh_dollar, rh_dollar = normalize_dollars(lhs), normalize_dollars(rhs)
    if lh_dollar and rh_dollar:
        return fuzz.ratio(lh_dollar, rh_dollar) / 100
    return default_similarity(lhs, rhs)


def log_dollar_amount(s):
    """Return the logarithm of 1 + a non-negative dollar amount."""
    d = dollar_amount(s)
    return math.log(d + 1) if d and d > 0 else None


def normalize_dollars(s) -> str:
    """Return a string of a number rounded to two digits (or None if not possible).

    Given a string like '$56,333.1' return the string '56333.10'.
    """
    try:
        return str(round(Decimal(str(s).replace("$", "").replace(",", "")), 2))
    except InvalidOperation:
        return None


def dollar_match(predicted, actual):
    """Best-effort matching of dollar amounts, e.g. '$14,123.02' to '14123.02'."""
    return (
        is_dollar_amount(predicted)
        and is_dollar_amount(actual)
        and (normalize_dollars(predicted) == normalize_dollars(actual))
    )


date_formats = {
    # If a string matches the regex key, it can be passed to strptime()
    # with the respective format string. Ordered from most to least common.
    re.compile(r"^[01]?\d/[0123]?\d/\d\d$"): "%m/%d/%y",
    re.compile(r"^[01]?\d/[0123]?\d/20\d\d$"): "%m/%d/%Y",
    re.compile(r"^[a-z]{3}\d?\d/\d\d$"): "%b%d/%y",
    re.compile(r"^[a-z]{3}\d?\d/20\d\d$"): "%b%d/%Y",
    re.compile(r"^[a-z]{4,9}\d?\d/\d\d$"): "%B%d/%y",
    re.compile(r"^[a-z]{4,9}\d?\d/20\d\d$"): "%B%d/%Y",
}
_time_punc = re.compile(r"[-,\\]")
_no_year = re.compile(r"^[01]?\d/[0123]?\d$")


def normalize_date(s):
    """Turn a string in a common date format into a date."""
    try:
        if num_digits(s) == 0:
            return None
        # Turn dashes, commas and back slashes into forward slashes.
        s = _time_punc.sub("/", simple_string(s))
        # Check the string against each possible date format.
        for date_regex, strp_format in date_formats.items():
            if date_regex.match(s):
                return datetime.strptime(s, strp_format).date()
        if _no_year.match(s):
            # If no date is present, assume 2020.
            return datetime.strptime(s + "/20", "%m/%d/%y").date()
    except (TypeError, ValueError):
        return None


def date_similarity(lhs, rhs):
    lh_date, rh_date = normalize_date(lhs), normalize_date(rhs)
    if lh_date and rh_date and lh_date == rh_date:
        return 1
    return default_similarity(lhs, rhs)


def date_match(predicted, actual):
    """Best-effort matching of dates, e.g. '02-03-2020' to '2/3/20'."""
    lhs, rhs = normalize_date(predicted), normalize_date(actual)
    return bool(lhs and rhs and lhs == rhs)


def any_similarity(lhs, rhs):
    return max(dollar_similarity(lhs, rhs), date_similarity(lhs, rhs))


def any_match(lhs, rhs):
    return loose_match(lhs, rhs) or dollar_match(lhs, rhs) or date_match(lhs, rhs)


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
    except (OSError, subprocess.CalledProcessError):
        return "UnknownGitRevsion"
