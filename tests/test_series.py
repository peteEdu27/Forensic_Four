# tests/test_series.py - checks for src/series.py
# Run from the repo root with:  pytest
#
# Like test_intake.py, these build their own tiny frames instead of reading
# data/map_ucr.csv -- that file is gitignored and a reviewer cloning the repo
# won't have it until they run python -m src.get_data.

import pandas as pd
import pytest

from src.series import (DALLAS_ORI, build_series, rates_over_100,
                        missing_years, biggest_jumps)


def make_rows(rows):
    """rows: [(ORI, YEAR, MRD, CLR), ...] -> a frame shaped like map_ucr.csv"""
    return pd.DataFrame(rows, columns=["ORI", "YEAR", "MRD", "CLR"])


def test_build_series_columns_and_rate():
    s = build_series(make_rows([(DALLAS_ORI, 2000, 200, 100.0),
                                (DALLAS_ORI, 2001, 100, 75.0)]))
    assert s.index.name == "year"
    assert s.columns.tolist() == ["reported", "cleared", "clearance"]
    assert s.loc[2000, "clearance"] == pytest.approx(0.5)
    assert s.loc[2001, "clearance"] == pytest.approx(0.75)


def test_build_series_cleared_is_integer_count():
    # CLR comes off disk as a float column
    s = build_series(make_rows([(DALLAS_ORI, 2000, 10, 4.0)]))
    assert s["cleared"].dtype.kind == "i"


def test_rates_over_100_flags_only_those_years():
    s = build_series(make_rows([(DALLAS_ORI, 2000, 10, 12.0),
                                (DALLAS_ORI, 2001, 10, 9.0)]))
    assert rates_over_100(s).index.tolist() == [2000]


def test_missing_years_finds_the_gap():
    s = build_series(make_rows([(DALLAS_ORI, 2000, 10, 5.0),
                                (DALLAS_ORI, 2003, 10, 5.0)]))
    assert missing_years(s, 2000, 2003) == [2001, 2002]


def test_biggest_jumps_ranks_by_size_keeps_sign():
    s = build_series(make_rows([(DALLAS_ORI, 2000, 10, 5.0),   # 50%
                                (DALLAS_ORI, 2001, 10, 6.0),   # +10
                                (DALLAS_ORI, 2002, 10, 2.0)])) # -40
    jumps = biggest_jumps(s, n=2)
    assert jumps.index.tolist() == [2002, 2001]
    assert jumps[2002] == pytest.approx(-0.4)
