import pytest
from intake_safe import parse_row

def test_good_row_parses():
    row = ["CC-20001", "OKAFOR, TASHA", "M", "61", "2011-10-24", "9897 buckner boulevard", "623", "CLOSED"]
    case = parse_row(row)
    assert case["age"] == 61
    assert case["name"] == "Okafor, Tasha"


def test_bad_age_rejected():
    row = ["CC-20015", "REYES, ALICIA", "M", "unknown", "2009-06-08", "405 lancaster road", "623", "CLOSED"]
    with pytest.raises(ValueError):
        parse_row(row)


def test_missing_date_rejected():
    row = ["CC-20000", "DELGADO, PATRICE", "M", "60", "", "6115 scyene road", "326", "CLOSED"]
    with pytest.raises(ValueError):
        parse_row(row)
# python -m pytest Week_6/test_intake.py -v 