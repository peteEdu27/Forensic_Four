# test_cases.py
# pytest proof that the cleaners and Case.from_row() work. Run with:  pytest test_cases.py
# pytest automatically runs every function whose name starts with "test_".
# Every test row below is copied from the shape of a real row in midterm_cases_raw.csv.

import pytest                                        # pytest gives us pytest.raises(), which checks that an error really happens
from case_model import Case, clean_age, clean_phone  # bring in what we are testing from case_model.py


def make_row():                                      # helper (not a test - its name does not start with "test_"): a fresh messy-but-valid row
    """Return a messy but valid raw row with all 9 fields."""   # docstring
    return [" CC-76856 ", "  walker,  g ", " m", " 41 ", "6/7/2000",       # id with spaces, name with extra spaces, sex " m", age " 41 ", US date
            "7840 Webb Chapel Rd", "Beat 157", " OPEN ",                    # address (dropped), beat with a word, status with spaces
            "Caller left callback (214) 555-4240; possibly linked to CC-12345"]   # tip notes holding a phone AND a case ref


# ---------- happy paths: a good row must clean correctly ----------

def test_good_row_cleans_every_field():              # TEST 1: every field is repaired to the standard
    case = Case.from_row(make_row())                 # build a Case from the messy row
    assert case.case_id == "CC-76856"                # spaces stripped
    assert case.victim_name == "Walker, G"           # spaces collapsed and Title Case
    assert case.sex == "M"                           # " m" -> "M"
    assert case.age == 41                            # " 41 " -> the number 41
    assert case.incident_date == "2000-06-07"        # 6/7/2000 -> YYYY-MM-DD
    assert case.year == 2000                         # year column
    assert case.beat == "157"                        # "Beat 157" -> "157"
    assert case.status == "OPEN"                     # " OPEN " -> "OPEN"
    assert case.callback_phone == "214-555-4240"     # the phone, not the CC-12345 case ref


def test_messy_values_are_normalized():              # TEST 2: other messy shapes from the file
    row = make_row()                                 # start from the good row
    row[0] = "CC 16288"                              # case_id with a space instead of a dash
    row[2] = "female"                                # sex spelled out
    row[4] = "July 1, 2022"                          # month-name date format
    row[6] = "B-150"                                 # beat with a B- prefix
    row[7] = "CLSD"                                  # abbreviation for CLOSED
    row[8] = "Caller left callback 214.555.3072"     # phone written with dots
    case = Case.from_row(row)                        # clean it
    assert case.case_id == "CC-16288"                # the space became a dash
    assert case.sex == "F"                           # "female" -> "F"
    assert case.incident_date == "2022-07-01"        # month name -> month number
    assert case.beat == "150"                        # only the 3 digits
    assert case.status == "CLOSED"                   # CLSD maps to CLOSED
    assert case.callback_phone == "214-555-3072"     # dots became dashes


def test_bad_age_and_missing_phone_become_blank():   # TEST 3: non-critical fields are repaired, not rejected
    assert clean_age("999") is None                  # out of range 0-110 -> blank
    assert clean_age("unknown") is None              # not a number -> blank
    assert clean_age("-1") is None                   # negative -> blank
    assert clean_phone("Walk-in tip, declined to give contact") == ""   # no phone in the notes -> blank


def test_stale_property():                           # TEST 4: the Case answers its own questions
    case = Case.from_row(make_row())                 # an OPEN case from 2000
    assert case.years_unsolved == 26                 # 2026 - 2000
    assert case.is_stale                             # OPEN and 26 >= 5 -> stale


# ---------- failure paths: a broken critical field must raise ValueError ----------

def test_wrong_field_count_rejected():               # TEST 5: a truncated row
    row = ["CC-61159", "HALL, C", " M", "18", "06/20/1998"]   # only 5 fields instead of 9 (real shape from line 67)
    with pytest.raises(ValueError):                  # the test PASSES only if the code inside raises ValueError
        Case.from_row(row)                           # from_row should refuse it


def test_bad_case_id_rejected():                     # TEST 6: an id that cannot become CC- + 5 digits
    row = make_row()                                 # good row...
    row[0] = "XX-46752"                              # ...with the wrong prefix
    with pytest.raises(ValueError):                  # expect the "bad case_id" error
        Case.from_row(row)                           # run it


def test_impossible_date_rejected():                 # TEST 7: February 30 does not exist
    row = make_row()                                 # good row...
    row[4] = "2008-02-30"                            # ...with an impossible date
    with pytest.raises(ValueError):                  # expect "invalid date"
        Case.from_row(row)                           # run it


def test_future_date_rejected():                     # TEST 8: a date after 10/07/2026
    row = make_row()                                 # good row...
    row[4] = "2027-04-01"                            # ...that has not happened yet
    with pytest.raises(ValueError):                  # expect "future date"
        Case.from_row(row)                           # run it


def test_unknown_status_rejected():                  # TEST 9: a status that maps to neither OPEN nor CLOSED
    row = make_row()                                 # good row...
    row[7] = "PENDING?"                              # ...with an unmappable status
    with pytest.raises(ValueError):                  # expect "unknown status"
        Case.from_row(row)                           # run it
