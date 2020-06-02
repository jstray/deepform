from decimal import Decimal
from math import isclose

import hypothesis.strategies as st
from deepform.util import (
    BoundingBox,
    docrow_to_bbox,
    dollar_amount,
    is_dollar_amount,
    log_dollar_amount,
    normalize_dollars,
)
from hypothesis import example, given


def test_is_dollar_amount():
    assert is_dollar_amount("$10")
    assert is_dollar_amount("$15.00")
    assert is_dollar_amount("$2.03")
    assert is_dollar_amount("3")
    assert is_dollar_amount("04")
    assert is_dollar_amount("9,000")
    assert not is_dollar_amount("")
    assert not is_dollar_amount("$")
    assert not is_dollar_amount(",")
    assert not is_dollar_amount(".")
    assert not is_dollar_amount("$,")
    assert not is_dollar_amount("$.")
    assert not is_dollar_amount("C")
    assert not is_dollar_amount("$x")
    assert not is_dollar_amount("3 .17")


def test_dollar_amount():
    assert dollar_amount("$10") == 10
    assert dollar_amount("$15.00") == 15
    assert dollar_amount("$2.03") == 2.03
    assert dollar_amount("3") == 3
    assert dollar_amount("04") == 4
    assert dollar_amount("9,000") == 9000
    assert dollar_amount("") is None
    assert dollar_amount("C") is None
    assert dollar_amount("$x") is None
    assert dollar_amount("3 .17") is None


@given(st.text())
@example("$.01")
@example("$6.010.01")
@example("$3,020,01")
def test_dollar_amount_accepts_arbitratry_strings(s):
    if not is_dollar_amount(s):
        assert dollar_amount(s) is None
    else:
        assert normalize_dollars(s) is not None
        n = dollar_amount(s)
        assert normalize_dollars(str(n)) == normalize_dollars(s)


@given(st.text())
@example("0.02")
@example("-1")
@example("$-0.5")
def test_log_dollar_amount_accepts_arbitratry_strings(s):
    if is_dollar_amount(s) and dollar_amount(s) > 0:
        assert log_dollar_amount(s) > 0
    else:
        assert log_dollar_amount(s) is None


def test_normalize_dollars():
    assert normalize_dollars("0") == "0.00"
    assert normalize_dollars("$10") == "10.00"
    assert normalize_dollars("$15.00") == "15.00"
    assert normalize_dollars("$2.03") == "2.03"
    assert normalize_dollars("3") == "3.00"
    assert normalize_dollars("04") == "4.00"
    assert normalize_dollars("9,000") == "9000.00"
    assert normalize_dollars("") is None
    assert normalize_dollars("C") is None
    assert normalize_dollars("$x") is None
    assert normalize_dollars("3 .17") is None


coord = st.floats(min_value=-10, max_value=800, allow_nan=False)
height = st.floats(min_value=0, max_value=100)


@given(x0=coord, y0=coord, x1=coord, y1=coord, mh=height)
def test_docrow_to_bbox(x0, y0, x1, y1, mh):
    t = BoundingBox(x0=x0, x1=x1, y0=y0, y1=y1)
    bbox0 = docrow_to_bbox(t, min_height=None)
    bbox1 = docrow_to_bbox(t)
    bbox2 = docrow_to_bbox(t, min_height=mh)
    for box in (bbox0, bbox1, bbox2):
        assert box.x0 == Decimal(x0)
        assert box.x1 == Decimal(x1)
        assert box.y1 == Decimal(y1)
    assert bbox0.y0 == Decimal(y0)
    # Floating point arithmetic, yo.
    assert bbox1.y1 - bbox1.y0 >= 10 or isclose(bbox1.y1 - bbox1.y0, 10)
    assert bbox2.y1 - bbox2.y0 >= mh or isclose(bbox2.y1 - bbox2.y0, mh)
