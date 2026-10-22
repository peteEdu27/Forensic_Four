import pytest
from src.models import (Case, clean_case_id, clean_name, clean_sex,
                         clean_age, clean_beat, clean_status, clean_date,
                         extract_callback_phone)


def test_clean_case_id_valid_variants():
    assert clean_case_id(" CC-19495 ") == "CC-19495"
    assert clean_case_id("CC 16288") == "CC-16288"
    assert clean_case_id("cc81472") == "CC-81472"


def test_clean_case_id_bad_rejected():
    with pytest.raises(ValueError):
        clean_case_id("CASE?")


def test_clean_name_strips_collapses_and_titles():
    assert clean_name("  walker,   g ") == "Walker, G"


def test_clean_sex_maps_unknown_to_u():
    assert clean_sex("M") == "M"
    assert clean_sex("female") == "F"
    assert clean_sex("unk") == "U"


def test_clean_age_out_of_range_is_blank():
    assert clean_age("36") == 36
    assert clean_age("999") is None
    assert clean_age("unknown") is None


def test_clean_beat_extracts_three_digits():
    assert clean_beat("B-150") == "150"
    assert clean_beat("Beat 418") == "418"
    assert clean_beat("") is None


def test_clean_status_maps_variants():
    assert clean_status("OPN") == "OPEN"
    assert clean_status("CLSD") == "CLOSED"


def test_clean_date_missing_rejected():
    with pytest.raises(ValueError):
        clean_date("unknown")


def test_clean_date_invalid_rejected():
    with pytest.raises(ValueError):
        clean_date("2004-02-30")


def test_clean_date_future_rejected():
    with pytest.raises(ValueError):
        clean_date("2099-01-01")


def test_extract_callback_phone_finds_first_number():
    tip = "Caller left callback (214) 555-3072, said dark sedan"
    assert extract_callback_phone(tip) == "214-555-3072"


def test_extract_callback_phone_blank_when_missing():
    assert extract_callback_phone("Witness declined to give contact") == ""


def test_case_from_row_builds_case():
    row = ["CC-10003", "Ramirez, K", "M", "24", "1992-06-14",
           "123 Main St", "451", "CLOSED", "no callback left"]
    case = Case(row)
    assert case.case_id == "CC-10003"
    assert case.victim_name == "Ramirez, K"
    assert case.age == 24
    assert case.year == 1992
    assert case.beat == "451"
    assert case.status == "CLOSED"


def test_case_from_row_wrong_field_count_rejected():
    with pytest.raises(ValueError):
        Case(["CC-10003", "Ramirez, K"])


def test_case_is_stale():
    row = ["CC-10017", "Okafor, T", "F", "", "2015-11-02",
           "999 Elm St", "157", "OPEN", ""]
    case = Case(row)
    assert case.is_stale is True
