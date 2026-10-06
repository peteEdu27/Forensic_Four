# test_intake.py - Week 6 tests for parse_row()
# Run from this folder with:  pytest test_intake.py
#
# pytest finds every function whose name starts with "test_" and runs it.
# A test PASSES if it finishes without an error, and FAILS if an assert is
# False or an unexpected exception is raised.

from datetime import date

# pytest.raises() lets a test say "this code SHOULD raise an error".
import pytest

from intake_safe import parse_row


# One good row, copied straight from the CSV (CC-20001).
GOOD_ROW = ["CC-20001", "OKAFOR, TASHA", "M", "61", "2011-10-24",
            "9897 buckner boulevard", "623", "CLOSED"]


def test_good_row_is_parsed():
    record = parse_row(GOOD_ROW)

    # The age and date come back as real types, not text.
    assert record["case_id"] == "CC-20001"
    assert record["age"] == 61
    assert record["date"] == date(2011, 10, 24)
    assert record["status"] == "CLOSED"


def test_short_row_is_rejected():
    # CC-20024 is missing its beat and status columns (6 fields, not 8).
    short_row = ["CC-20024", "PALACIOS, FELIX", "M", "38", "2002-10-02",
                 "5928 peavy road"]

    # "with pytest.raises(ValueError, match=...)" passes only if the code
    # inside raises ValueError AND the message contains the match text.
    with pytest.raises(ValueError, match="expected 8 fields, got 6"):
        parse_row(short_row)


def test_unknown_age_is_rejected():
    # CC-20015 has "unknown" where the age should be.
    bad_age_row = ["CC-20015", "REYES, ALICIA", "M", "unknown", "2009-06-08",
                   "405 lancaster road", "623", "CLOSED"]

    with pytest.raises(ValueError, match="age is not a number"):
        parse_row(bad_age_row)
