# tests/test_intake.py - checks for src/intake.py
# Run from the repo root with:  pytest
#
# These tests build their own tiny CSV in a temp folder (pytest's tmp_path),
# so they don't depend on anything in data/ -- that folder is gitignored and
# a reviewer cloning the repo won't have the real case file.

from datetime import date

import pytest

from src.intake import parse_row, load_cases


# One known-good row, already split into its 8 columns.
GOOD_ROW = ["CC-20001", "OKAFOR, TASHA", "M", "61", "2011-10-24",
            "9897 buckner boulevard", "623", "CLOSED"]


# ============================================================
# parse_row()
# ============================================================

def test_parse_row_good_row_gets_real_types():
    case = parse_row(GOOD_ROW)
    assert case["case_id"] == "CC-20001"
    assert case["victim_name"] == "OKAFOR, TASHA"
    assert case["age"] == 61
    assert case["date"] == date(2011, 10, 24)


def test_parse_row_short_row():
    # Like CC-20024: beat and status are missing.
    with pytest.raises(ValueError, match="expected 8 fields, got 6"):
        parse_row(GOOD_ROW[:6])


def test_parse_row_age_not_a_number():
    # Like CC-20015: age is "unknown".
    row = GOOD_ROW.copy()
    row[3] = "unknown"
    with pytest.raises(ValueError, match="age is not a number"):
        parse_row(row)


def test_parse_row_age_out_of_range():
    row = GOOD_ROW.copy()
    row[3] = "150"
    with pytest.raises(ValueError, match="age out of range"):
        parse_row(row)


def test_parse_row_missing_date():
    # Like CC-20000: date is blank.
    row = GOOD_ROW.copy()
    row[4] = ""
    with pytest.raises(ValueError, match="date is missing"):
        parse_row(row)


def test_parse_row_impossible_date():
    # Right shape, but February 30th doesn't exist.
    row = GOOD_ROW.copy()
    row[4] = "2019-02-30"
    with pytest.raises(ValueError, match="date is not YYYY-MM-DD"):
        parse_row(row)


# ============================================================
# load_cases()
# ============================================================

def test_load_cases_splits_good_and_quarantine(tmp_path):
    csv_file = tmp_path / "cases.csv"
    csv_file.write_text(
        "case_id,victim_name,sex,age,date,address,beat,status\n"
        'CC-20001,"OKAFOR, TASHA",M,61,2011-10-24,9897 buckner boulevard,623,CLOSED\n'
        'CC-20003,"KIRKLAND, MONICA, JR, III",M,68,2007-04-07,7011 illinois avenue,518,OPEN\n'
        'CC-20015,"OSEI, GLORIA",F,unknown,1981-03-02,6999 kendale drive,326,OPEN\n'
        "\n"
        'CC-20024,"WINSLOW, JAMAL",M,62,1998-03-14,2149 peavy road\n'
    )

    good, quarantine = load_cases(csv_file)

    # The blank line is skipped, not quarantined: 2 good + 2 bad = 4 cases.
    assert [case["case_id"] for case in good] == ["CC-20001", "CC-20003"]
    assert [row[0] for _, _, row in quarantine] == ["CC-20015", "CC-20024"]


def test_load_cases_keeps_commas_inside_quoted_names(tmp_path):
    csv_file = tmp_path / "cases.csv"
    csv_file.write_text(
        "case_id,victim_name,sex,age,date,address,beat,status\n"
        'CC-20003,"KIRKLAND, MONICA, JR, III",M,68,2007-04-07,7011 illinois avenue,518,OPEN\n'
    )

    good, quarantine = load_cases(csv_file)

    assert quarantine == []
    assert good[0]["victim_name"] == "KIRKLAND, MONICA, JR, III"


def test_load_cases_quarantine_records_line_number_and_reason(tmp_path):
    csv_file = tmp_path / "cases.csv"
    csv_file.write_text(
        "case_id,victim_name,sex,age,date,address,beat,status\n"
        'CC-20001,"OKAFOR, TASHA",M,61,2011-10-24,9897 buckner boulevard,623,CLOSED\n'
        'CC-20000,"DELGADO, PATRICE",M,60,,6115 scyene road,326,CLOSED\n'
    )

    good, quarantine = load_cases(csv_file)

    line_num, reason, row = quarantine[0]
    # Header is line 1, so the bad row is line 3 -- same as VS Code shows.
    assert line_num == 3
    assert reason == "date is missing"
    assert row[0] == "CC-20000"
