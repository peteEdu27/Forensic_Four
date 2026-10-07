# Week 6 Squad Lab - tests for intake_safe.py

import pytest                                  # bring in pytest so we can check that errors get raised
from intake_safe import parse_row              # bring in the function we're testing


def good_row():                                # helper: builds a fresh good row for each test
    """Return a valid 8-field row with messy spacing and casing."""  # docstring: explains what the function does
    return ["CC-1", " carter, d ", "m", "36", "2018-03-22", "412 larkmoor", "352", "open"]  # a known-good row


def test_good_row_parses():                    # test 1: a good row comes back clean
    case = parse_row(good_row())               # parse the good row
    assert case["age"] == 36                   # the age text became the number 36
    assert case["name"] == "Carter, D"         # the name got trimmed and title-cased


def test_bad_age_rejected():                   # test 2: an 'unknown' age gets rejected
    row = good_row()                           # start from a good row
    row[3] = "unknown"                         # damage the age field
    with pytest.raises(ValueError):            # parse_row must raise ValueError here
        parse_row(row)                         # try to parse the damaged row


def test_missing_date_rejected():              # test 3: an empty date gets rejected
    row = good_row()                           # start from a good row
    row[4] = ""                                # blank out the date field
    with pytest.raises(ValueError, match="missing date"):  # parse_row must raise ValueError with this reason
        parse_row(row)                         # try to parse the damaged row
