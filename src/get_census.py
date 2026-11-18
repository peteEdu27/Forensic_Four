"""Fetch Dallas city ACS 1-year estimates into data/census_dallas.csv.
Run: python -m src.get_census"""
# src/get_census.py - Week 12: The Factor (Census ACS)
#
# One request per year to the Census Bureau API, Dallas city = state:48 place:19000.
# ACS 1-year starts in 2005 and has no 2020 release (withdrawn by the Bureau), so
# this series is ~20 rows at most. Any year the API does not have is skipped and
# reported, not invented.
#
# Needs CENSUS_API_KEY in .env (free: https://api.census.gov/data/key_signup.html).
# Without a key the API now redirects every request to missing_key.html.
import os
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

OUT = Path("data/census_dallas.csv")
FIRST_YEAR, LAST_YEAR = 2005, 2025
SKIP_YEARS = {2020}         # no ACS 1-year release for 2020

# code -> column name in our CSV
VARIABLES = {
    "B01003_001E": "population",
    "B19013_001E": "median_income",        # nominal dollars
    "B17001_001E": "poverty_universe",     # people whose poverty status is determined
    "B17001_002E": "below_poverty",
    "B23025_003E": "civilian_labor_force",
    "B23025_005E": "unemployed",
}


# B23025 (employment status) only exists in ACS 1-year from 2011 on. Asking for it
# in the same request as the poverty table makes the API reject the whole year
# ("unknown variable"), which silently dropped 2005-2010. So it is fetched separately
# and left blank where the table doesn't exist.
CORE = ["B01003_001E", "B19013_001E", "B17001_001E", "B17001_002E"]
OPTIONAL = ["B23025_003E", "B23025_005E"]


def _get(year: int, codes: list[str]) -> dict | None:
    """One request for Dallas city. Returns {code: value} or None if unavailable."""
    params = {"get": "NAME," + ",".join(codes), "for": "place:19000", "in": "state:48",
              "key": os.environ["CENSUS_API_KEY"]}
    r = requests.get(f"https://api.census.gov/data/{year}/acs/acs1", params=params,
                     timeout=60, allow_redirects=False)
    if "missing_key" in r.headers.get("location", "") or "invalid_key" in r.headers.get("location", ""):
        raise RuntimeError("Census API rejected the key. Check CENSUS_API_KEY in .env "
                           "and that you clicked the activation link in the email.")
    # 204 / 404 / 400 = that year-table combination doesn't exist.
    if r.status_code != 200 or not r.content.strip().startswith(b"["):
        print(f"  {year} {','.join(codes)}: no data (HTTP {r.status_code}) {r.text[:80].strip()}")
        return None
    header, row = r.json()[:2]
    return dict(zip(header, row))


def acs(year: int) -> dict | None:
    """One ACS 1-year row for Dallas city, or None if that year doesn't exist.
    Employment variables are blank (NaN after tidy) for years without table B23025."""
    core = _get(year, CORE)
    if core is None:
        return None
    extra = _get(year, OPTIONAL) or {code: None for code in OPTIONAL}
    return core | extra | {"year": year}


def tidy(raw: pd.DataFrame) -> pd.DataFrame:
    """Rename codes, cast to numbers, add the derived rates. One row per year."""
    df = raw.rename(columns=VARIABLES)[["year", *VARIABLES.values()]].copy()
    df["year"] = df["year"].astype(int)
    for col in VARIABLES.values():
        df[col] = pd.to_numeric(df[col], errors="coerce")
    # Census marks suppressed values with large negative sentinels (e.g. -666666666)
    for col in VARIABLES.values():
        df.loc[df[col] < 0, col] = pd.NA
    df["poverty_rate"] = df["below_poverty"] / df["poverty_universe"]
    df["unemployment_rate"] = df["unemployed"] / df["civilian_labor_force"]
    return df.sort_values("year").reset_index(drop=True)


def main() -> None:
    if not os.environ.get("CENSUS_API_KEY"):
        raise SystemExit("CENSUS_API_KEY is not set. Get a free key at "
                         "https://api.census.gov/data/key_signup.html and add "
                         "CENSUS_API_KEY=... to .env")
    rows = []
    for year in range(FIRST_YEAR, LAST_YEAR + 1):
        if year in SKIP_YEARS:
            print(f"  {year}: skipped (no ACS 1-year release)")
            continue
        row = acs(year)
        if row:
            rows.append(row)
    df = tidy(pd.DataFrame(rows))
    OUT.parent.mkdir(exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"saved: {OUT} ({len(df)} years, {df.year.min()}-{df.year.max()})")
    print(df[["year", "population", "poverty_rate", "median_income"]].to_string(index=False))


if __name__ == "__main__":
    main()
