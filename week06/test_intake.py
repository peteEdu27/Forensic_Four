# test_intake.py
# pytest proof that parse_row() works. Run with:  pytest test_intake.py
# pytest automatically runs every function whose name starts with "test_".

import pytest                                        # pytest gives us pytest.raises(), which checks that an error really happens
from intake_safe import parse_row                    # bring in the function we are testing from intake_safe.py


def test_good_row_parses():                          # TEST 1: a healthy row should convert cleanly
    row = ["CC-1", " carter, d ", "m", "36",         # 8 fields: id, messy name (spaces + lowercase), sex, age as TEXT,
           "2018-03-22", "412 larkmoor", "352", "open"]   # date, address, beat, status
    case = parse_row(row)                            # run the parser and keep the dict it returns
    assert case["age"] == 36                         # assert = "this MUST be true or the test fails"; the text "36" must have become the number 36
    assert case["name"] == "Carter, D"               # the spaces must be trimmed and the name capitalized


def test_bad_age_rejected():                         # TEST 2: an age of "unknown" must be rejected
    row = ["CC-1", "carter, d", "m", "unknown",      # age is the word "unknown" instead of a number
           "2018-03-22", "412 larkmoor", "352", "open"]
    with pytest.raises(ValueError):                  # the test PASSES only if the code inside this block raises a ValueError
        parse_row(row)                               # int("unknown") should blow up with a ValueError


def test_truncated_row_rejected():                   # TEST 3: a row with too few fields must be rejected
    row = ["CC-1", "carter, d", "m", "36", "2018-03-22", "412 larkmoor"]   # only 6 fields instead of 8
    with pytest.raises(ValueError):                  # we expect a ValueError (our "expected 8 fields" check)
        parse_row(row)                               # run the parser; the test passes if it raises
