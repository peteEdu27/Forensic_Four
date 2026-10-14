import pytest                                                              # testing framework, provides pytest.raises for failure-path tests
from case_model import (Case, clean_case_id, clean_name, clean_sex,        # the Case class and every field-cleaner function under test
                         clean_age, clean_beat, clean_status, clean_date,
                         extract_callback_phone)

def test_clean_case_id_valid_variants():                                   # messy but fixable case_id strings all normalize the same way
    assert clean_case_id(" CC-19495 ") == "CC-19495"                       # extra whitespace around a well-formed id
    assert clean_case_id("CC 16288") == "CC-16288"                         # space instead of a dash
    assert clean_case_id("cc81472") == "CC-81472"                          # lower-case, no dash at all

def test_clean_case_id_bad_rejected():                                     # failure path: an id that can't be normalized
    with pytest.raises(ValueError):                                        # anything not "CC" + 5 digits must raise
        clean_case_id("CASE?")

def test_clean_name_strips_collapses_and_titles():                         # victim name gets whitespace collapsed and title-cased
    assert clean_name("  walker,   g ") == "Walker, G"

def test_clean_sex_maps_unknown_to_u():                                    # sex normalizes to M/F, anything else becomes U
    assert clean_sex("M") == "M"                                           # already a clean code
    assert clean_sex("female") == "F"                                      # full word, different case
    assert clean_sex("unk") == "U"                                         # unrecognized value falls back to "U"

def test_clean_age_out_of_range_is_blank():                                # age is kept only when it's a plausible whole number
    assert clean_age("36") == 36                                           # normal age, parsed as int
    assert clean_age("999") is None                                        # digits, but outside the plausible range
    assert clean_age("unknown") is None                                    # not digits at all

def test_clean_beat_extracts_three_digits():                               # beat is whatever 3-digit run appears in the raw text
    assert clean_beat("B-150") == "150"                                    # digits embedded in a short code
    assert clean_beat("Beat 418") == "418"                                 # digits embedded in a longer label
    assert clean_beat("") is None                                          # nothing to extract

def test_clean_status_maps_variants():                                     # status abbreviations normalize to OPEN/CLOSED
    assert clean_status("OPN") == "OPEN"                                   # abbreviation for open
    assert clean_status("CLSD") == "CLOSED"                                # abbreviation for closed

def test_clean_date_missing_rejected():                                    # failure path: a blank/placeholder date
    with pytest.raises(ValueError):                                        # "unknown" is treated as a missing date
        clean_date("unknown")

def test_clean_date_invalid_rejected():                                    # failure path: a date that parses but isn't real
    with pytest.raises(ValueError):                                        # February never has a 30th
        clean_date("2004-02-30")

def test_clean_date_future_rejected():                                     # failure path: a date after TODAY
    with pytest.raises(ValueError):                                        # incidents can't happen in the future
        clean_date("2099-01-01")

def test_extract_callback_phone_finds_first_number():                      # a phone number embedded in free-text tip notes
    tip = "Caller left callback (214) 555-3072, said dark sedan"           # realistic tip_notes value with a phone number in it
    assert extract_callback_phone(tip) == "214-555-3072"                   # normalized to dash-separated digits

def test_extract_callback_phone_blank_when_missing():                      # no phone number present in the notes at all
    assert extract_callback_phone("Witness declined to give contact") == ""

def test_case_from_row_builds_case():                                      # a well-formed row builds a fully cleaned Case
    row = ["CC-10003", "Ramirez, K", "M", "24", "1992-06-14",              # case_id, name, sex, age, incident_date
           "123 Main St", "451", "CLOSED", "no callback left"]             # address (unused), beat, status, tip_notes
    case = Case(row)                                                       # build the Case from the raw row
    assert case.case_id == "CC-10003"                                      # id normalized with its dash
    assert case.victim_name == "Ramirez, K"                                # name passed through clean_name
    assert case.age == 24                                                  # age parsed to an int
    assert case.year == 1992                                               # year derived from incident_date
    assert case.beat == "451"                                              # beat extracted from the raw field
    assert case.status == "CLOSED"                                         # status normalized

def test_case_from_row_wrong_field_count_rejected():                       # failure path: a truncated row
    with pytest.raises(ValueError):                                        # every valid row must have exactly 9 fields
        Case(["CC-10003", "Ramirez, K"])

def test_case_is_stale():                                                  # an open case from 2015 counts as stale by TODAY
    row = ["CC-10017", "Okafor, T", "F", "", "2015-11-02",                 # age left blank on purpose, still a valid row
           "999 Elm St", "157", "OPEN", ""]                                # no tip phone number either
    case = Case(row)                                                       # build the Case from the raw row
    assert case.is_stale is True                                           # open for more than 5 years as of TODAY

# python -m pytest test_cases.py -v                                        # command to run the full suite verbosely