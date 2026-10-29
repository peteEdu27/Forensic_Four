# src/series.py - Week 9: Operation First Cut
# Goal: build Dallas PD's homicide clearance-by-year series from the MAP / FBI
# archive, write it to reports/dallas_series.csv, run the three mandatory
# sanity checks, and print the 5 most suspicious years with a reason each.
#
# Run from the repo root (after python -m src.get_data):
#   python -m src.series
#
# "cleared" in this series is the FBI UCR definition: cleared by arrest OR by
# exceptional means (suspect dead, prosecution declined). It also counts
# clearances made THIS year of murders from EARLIER years, which is how a
# clearance rate can jump (or go over 100%) without any change in policing.
# The Washington Post column in the stretch section counts "Closed by arrest"
# only. The two are different definitions; never put them on one axis unlabeled.
#
# Aggregate analysis only. Nothing here reads or prints a victim name.

from pathlib import Path

import pandas as pd

MAP_FILE = Path("data/map_ucr.csv")
WAPO_FILE = Path("data/wapo_dallas.csv")
OUT_FILE = Path("reports/dallas_series.csv")

# Dallas Police Department. Filtering on Agency == "Dallas" pulls in Dallas GA,
# NC and OR too (93 rows), and the Dallas County Sheriff is a different ORI.
DALLAS_ORI = "TXDPD00"
EXPECTED_ROWS = 61          # 1965 through 2025
FIRST_YEAR, LAST_YEAR = 1965, 2025

# The newest year in the archive is still being reported by the agency.
PARTIAL_YEAR = 2025


# ============================================================
# STEP 2: filter the national file down to Dallas PD
# ============================================================

def load_dallas(path=MAP_FILE):
    """Read the MAP archive and return only the Dallas PD rows."""
    df = pd.read_csv(path)
    dallas = df[df["ORI"] == DALLAS_ORI]
    return df, dallas


# ============================================================
# STEP 3: groupby year -> reported, cleared, clearance
# ============================================================

def build_series(dallas):
    """One row per year: reported, cleared, clearance (cleared / reported)."""
    per_year = dallas.groupby("YEAR").agg(
        reported=("MRD", "sum"),
        cleared=("CLR", "sum"),
    )
    # CLR loads as a float column; these are counts of cases
    per_year["cleared"] = per_year["cleared"].astype(int)
    per_year["clearance"] = per_year["cleared"] / per_year["reported"]
    per_year.index.name = "year"
    return per_year


# ============================================================
# STEP 4: the three mandatory sanity checks
# ============================================================

def rates_over_100(per_year):
    """Years where more murders were cleared than reported."""
    return per_year[per_year["clearance"] > 1]


def missing_years(per_year, first=FIRST_YEAR, last=LAST_YEAR):
    """Years in [first, last] that have no row in the series."""
    return sorted(set(range(first, last + 1)) - set(per_year.index))


def biggest_jumps(per_year, n=5):
    """The n largest year-over-year changes in clearance, as signed values."""
    change = per_year["clearance"].diff()
    order = change.abs().sort_values(ascending=False).index[:n]
    return change.loc[order]


# ============================================================
# STEP 5: the 5 most suspicious years, one line of reasoning each
# The reasons are written by us (that is the judgment part of the audit);
# the numbers inside them are pulled from the series so they can't go stale.
# ============================================================

def pct(x):
    return f"{x:.1%}"


def suspicious_years(s):
    """Return [(year, reason), ...] for the years that smell wrong."""
    c, r, k = s["clearance"], s["reported"], s["cleared"]
    return [
        (2017, f"clearance jumps to {pct(c[2017])} from {pct(c[2016])} "
               f"(+{(c[2017] - c[2016]) * 100:.0f} pts) while reported stays flat "
               f"({r[2016]} -> {r[2017]}); cleared leaps {k[2016]} -> {k[2017]}. "
               "Likely prior-year cases cleared in bulk and counted in 2017's numerator."),
        (2018, f"clearance falls to {pct(c[2018])}, "
               + ("the lowest" if c.idxmin() == 2018 else "one of the lowest")
               + f" of all {len(c)} years, then rebounds to {pct(c[2019])} in 2019. Mirror image of 2017: "
               "check whether clearances were pulled forward or a records system changed."),
        (2007, f"clearance drops {pct(c[2006])} -> {pct(c[2007])} "
               f"({(c[2007] - c[2006]) * 100:.0f} pts) on similar volume, and starts "
               f"the 2007-2011 slide in reported murders ({r[2007]} -> {r[2011]}). "
               "First WaPo year, so it is the first year we can cross-check."),
        (1974, f"one-year dip to {pct(c[1974])} between {pct(c[1973])} and "
               f"{pct(c[1975])}; cleared drops {k[1973]} -> {k[1974]} then back "
               f"to {k[1975]}. A full reversal in a year looks like reporting, not policing."),
        (PARTIAL_YEAR, f"partial year, still being reported: {r[PARTIAL_YEAR]} "
               f"murders vs {r[PARTIAL_YEAR - 1]} in {PARTIAL_YEAR - 1} "
               f"({r[PARTIAL_YEAR] / r[PARTIAL_YEAR - 1] - 1:+.0%}). Provisional; "
               "keep it out of any trend line until the year closes."),
    ]


# ============================================================
# STRETCH: the Washington Post as a second source
# ============================================================

def wapo_by_year(path=WAPO_FILE):
    """WaPo Dallas cases and arrests per year (arrest = 'Closed by arrest')."""
    w = pd.read_csv(path)
    w["year"] = w["reported_date"].astype(str).str[:4].astype(int)
    return w.groupby("year").agg(
        wapo_cases=("uid", "count"),
        wapo_arrests=("disposition", lambda s: (s == "Closed by arrest").sum()),
    )


def main():
    # Step 1: know what you're holding before any analysis
    df, dallas = load_dallas()
    print(df.shape)
    print(df.columns.tolist())
    print(df.head())
    print(f"Dallas PD rows: {len(dallas)} (expect {EXPECTED_ROWS})")

    per_year = build_series(dallas)
    OUT_FILE.parent.mkdir(exist_ok=True)
    per_year.to_csv(OUT_FILE)
    print(f"wrote {OUT_FILE}: {len(per_year)} years, "
          f"{per_year.index.min()}-{per_year.index.max()}")

    print("\n--- sanity check 1: rates over 100% ---")
    over = rates_over_100(per_year)
    print(over if len(over) else "none")

    print("\n--- sanity check 2: missing years ---")
    gaps = missing_years(per_year)
    print(gaps if gaps else f"none ({FIRST_YEAR}-{LAST_YEAR} complete)")

    print("\n--- sanity check 3: biggest year-over-year jumps in clearance ---")
    for year, change in biggest_jumps(per_year).items():
        print(f"  {year}: {change * 100:+.1f} pts  (now {pct(per_year.clearance[year])})")

    print("\n--- 5 most suspicious years ---")
    for year, reason in suspicious_years(per_year):
        print(f"  {year}: {reason}")

    if WAPO_FILE.exists():
        print("\n--- stretch: FBI (MAP) vs Washington Post ---")
        merged = per_year.join(wapo_by_year(), how="inner")
        merged["case_gap"] = merged["reported"] - merged["wapo_cases"]
        merged["clear_gap"] = merged["cleared"] - merged["wapo_arrests"]
        print(merged.drop(columns="clearance").to_string())
        # .loc on one row turns it into a float Series; cast back to counts
        y = merged.drop(columns="clearance").loc[2010].astype(int)
        print(f"2010: FBI {y.reported} reported vs WaPo {y.wapo_cases} cases "
              f"(gap {y.case_gap}); FBI {y.cleared} cleared vs WaPo "
              f"{y.wapo_arrests} arrests (gap {y.clear_gap}).")
        print("2017 WaPo rows are a partial year (file ends early 2017); "
              "ignore that row's gap.")


if __name__ == "__main__":
    main()
