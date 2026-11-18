"""Week 12: Operation The Factor. Run: python -m src.factor
(after python -m src.series and python -m src.get_census)"""
# src/factor.py - Week 12: The Factor
#
# Pre-registered hypothesis (locked at standup, no silent pivots):
#   "We hypothesize that the poverty rate in the City of Dallas is associated
#    with Dallas homicide clearance, in the negative direction."
#
# Pre-registered specification, fixed BEFORE looking at the merged data:
#   primary:  clearance_pct ~ poverty_pct
#   variant:  clearance_pct ~ poverty_pct_lag1   (last year's poverty)
#   window:   every year in both sources, minus 2025 (partial year in the FBI
#             series, see src/series.py PARTIAL_YEAR)
# Anything else we run is labeled exploratory in the writeup.
#
# Both variables are in percentage points, so coef reads as "clearance points
# per 1 point of poverty rate".
from pathlib import Path

import pandas as pd
import statsmodels.formula.api as smf

from src.series import PARTIAL_YEAR

SERIES_FILE = Path("reports/dallas_series.csv")
FACTOR_FILE = Path("data/census_dallas.csv")
OLS_OUT = Path("reports/factor_ols.txt")

PRIMARY = "clearance_pct ~ poverty_pct"
LAGGED = "clearance_pct ~ poverty_pct_lag1"


def load_series(path=SERIES_FILE) -> pd.DataFrame:
    s = pd.read_csv(path)
    s["year"] = s["year"].astype(int)
    s["clearance_pct"] = s["clearance"] * 100
    return s


def load_factor(path=FACTOR_FILE) -> pd.DataFrame:
    f = pd.read_csv(path)
    f["year"] = f["year"].astype(int)
    f["poverty_pct"] = f["poverty_rate"] * 100
    return f[["year", "poverty_pct", "population", "median_income"]]


def lag_by_year(factor: pd.DataFrame, col: str) -> pd.DataFrame:
    """Add <col>_lag1 = value from calendar year - 1.

    Matches on the year VALUE, not row position. The ACS has no 2020, so
    .shift(1) would quietly give 2021 the 2019 value. Here 2021's lag is NaN.
    """
    prev = factor[["year", col]].copy()
    prev["year"] = prev["year"] + 1
    prev = prev.rename(columns={col: f"{col}_lag1"})
    return factor.merge(prev, on="year", how="left")


def merge_on_year(series: pd.DataFrame, factor: pd.DataFrame,
                  drop_years=(PARTIAL_YEAR,)) -> pd.DataFrame:
    """Inner join on year. Casts both keys to int (the classic 0-row merge bug)."""
    series = series.assign(year=series["year"].astype(int))
    factor = factor.assign(year=factor["year"].astype(int))
    merged = series.merge(factor, on="year", how="inner")
    merged = merged[~merged["year"].isin(drop_years)]
    return merged.sort_values("year").reset_index(drop=True)


def fit(df: pd.DataFrame, formula: str):
    """OLS on the rows that have every variable in the formula."""
    needed = [c.strip() for side in formula.split("~") for c in side.split("+")]
    return smf.ols(formula, data=df.dropna(subset=needed)).fit()


def headline(name: str, model, term: str) -> str:
    lo, hi = model.conf_int().loc[term]
    return (f"{name}: coef = {model.params[term]:+.3f}, "
            f"95% CI [{lo:+.3f}, {hi:+.3f}], p = {model.pvalues[term]:.3f}, "
            f"R² = {model.rsquared:.3f} (n = {int(model.nobs)})")


def main() -> None:
    factor = lag_by_year(load_factor(), "poverty_pct")
    merged = merge_on_year(load_series(), factor)

    # eyeball before modeling
    print("merged shape:", merged.shape)
    print(merged[["year", "reported", "clearance_pct", "poverty_pct",
                  "poverty_pct_lag1"]].head().to_string(index=False))

    m1 = fit(merged, PRIMARY)
    m2 = fit(merged, LAGGED)
    print(m1.summary())
    print(m2.summary())

    lines = [headline("primary  " + PRIMARY, m1, "poverty_pct"),
             headline("lag-1    " + LAGGED, m2, "poverty_pct_lag1")]
    print("\n".join(lines))

    window = f"{merged.year.min()}-{merged.year.max()}"
    OLS_OUT.write_text(
        f"Window: {window}, years: {merged.year.tolist()}\n\n"
        + "\n".join(lines) + "\n\n"
        + "=== PRIMARY ===\n" + m1.summary().as_text() + "\n\n"
        + "=== LAG-1 ===\n" + m2.summary().as_text() + "\n",
        encoding="utf-8")
    print(f"saved: {OLS_OUT}")


if __name__ == "__main__":
    main()
