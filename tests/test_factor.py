# tests/test_factor.py - checks for src/factor.py and src/get_census.py
# Tiny hand-built frames only: data/census_dallas.csv is gitignored.

import pandas as pd
import pytest

from src.factor import fit, lag_by_year, merge_on_year
from src.get_census import tidy


def test_merge_casts_string_years():
    series = pd.DataFrame({"year": [2019, 2021], "clearance_pct": [50.0, 60.0]})
    factor = pd.DataFrame({"year": ["2019", "2021"], "poverty_pct": [18.0, 17.0]})
    merged = merge_on_year(series, factor, drop_years=())
    assert merged["year"].tolist() == [2019, 2021]


def test_merge_drops_partial_year():
    series = pd.DataFrame({"year": [2024, 2025], "clearance_pct": [46.0, 52.0]})
    factor = pd.DataFrame({"year": [2024, 2025], "poverty_pct": [17.0, 16.0]})
    assert merge_on_year(series, factor)["year"].tolist() == [2024]


def test_lag_uses_calendar_year_not_row_position():
    # no 2020 row, like the real ACS
    factor = pd.DataFrame({"year": [2018, 2019, 2021, 2022],
                           "poverty_pct": [20.0, 19.0, 17.0, 16.0]})
    lagged = lag_by_year(factor, "poverty_pct").set_index("year")
    assert lagged.loc[2019, "poverty_pct_lag1"] == 20.0
    assert pd.isna(lagged.loc[2021, "poverty_pct_lag1"])   # not 19.0
    assert lagged.loc[2022, "poverty_pct_lag1"] == 17.0


def test_fit_recovers_known_slope():
    df = pd.DataFrame({"x": [1.0, 2.0, 3.0, 4.0, 5.0]})
    df["y"] = 10 - 2 * df["x"]
    m = fit(df, "y ~ x")
    assert m.params["x"] == pytest.approx(-2.0)


def test_fit_drops_rows_missing_a_model_variable():
    df = pd.DataFrame({"x": [1.0, 2.0, None, 4.0], "y": [1.0, 2.0, 3.0, 4.0]})
    assert fit(df, "y ~ x").nobs == 3


def test_tidy_rates_and_suppressed_values():
    raw = pd.DataFrame([{
        "year": "2019", "B01003_001E": "1343573", "B19013_001E": "-666666666",
        "B17001_001E": "1000", "B17001_002E": "200",
        "B23025_003E": "500", "B23025_005E": "25",
    }])
    df = tidy(raw)
    assert df.loc[0, "year"] == 2019
    assert df.loc[0, "poverty_rate"] == pytest.approx(0.2)
    assert df.loc[0, "unemployment_rate"] == pytest.approx(0.05)
    assert pd.isna(df.loc[0, "median_income"])


def test_acs_keeps_year_when_employment_table_missing(monkeypatch):
    # pre-2011 ACS 1-year has no B23025; the poverty data must still come through
    import src.get_census as gc

    def fake_get(year, codes):
        if codes == gc.OPTIONAL:
            return None
        return {"NAME": "Dallas city, Texas", "B01003_001E": "1200000",
                "B19013_001E": "40000", "B17001_001E": "1000", "B17001_002E": "250"}

    monkeypatch.setattr(gc, "_get", fake_get)
    df = tidy(pd.DataFrame([gc.acs(2008)]))
    assert df.loc[0, "year"] == 2008
    assert df.loc[0, "poverty_rate"] == pytest.approx(0.25)
    assert pd.isna(df.loc[0, "unemployment_rate"])


def test_core_and_optional_cover_every_variable():
    import src.get_census as gc
    assert set(gc.CORE) | set(gc.OPTIONAL) == set(gc.VARIABLES)
