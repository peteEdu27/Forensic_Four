# src/charts.py - Week 10: Operation The Picture (part 1, the trend chart)
# Goal: turn reports/dallas_series.csv into a publication-honest trend chart,
# reports/clearance_trend.png, that makes our week-9 argument on its own.
#
# Run from the repo root (after python -m src.get_data and python -m src.series):
#   python -m src.charts
#
# The honesty checklist this chart has to pass (wk10 supplement, section 1):
#   - y-axis runs 0 to 100            -> no truncated baseline
#   - source named in the axis label  -> "clearance" is the FBI's definition
#   - gaps broken, not bridged        -> reindex to every year, NaN breaks the line
#   - partial years marked            -> 2025 is still being reported
#   - title says what, where, when
#
# "Clearance" here is the FBI UCR definition (arrest OR exceptional means,
# counted in the year the clearance happened). It is NOT the Washington Post's
# "Closed by arrest"; that one belongs to the map in src/casemap.py.

from pathlib import Path

import matplotlib

matplotlib.use("Agg")       # write a file, never open a window (works on the server too)
import matplotlib.pyplot as plt
import pandas as pd

from src.series import FIRST_YEAR, LAST_YEAR, PARTIAL_YEAR

SERIES_FILE = Path("reports/dallas_series.csv")
OUT_FILE = Path("reports/clearance_trend.png")

# Our #1 suspicious year from week 9: clearance leaps ~30 points while the
# number of murders stays flat -> prior-year cases cleared in bulk.
SUSPICIOUS_YEAR = 2017

TITLE = (f"Dallas Police Department homicide clearance rate, "
         f"{FIRST_YEAR}–{LAST_YEAR}")
YLABEL = ("Homicide clearance (%)\n"
          "Source: FBI UCR via Murder Accountability Project")


# ============================================================
# STEP 1: load the series and put every year on the axis
# ============================================================

def load_series(path=SERIES_FILE):
    """Read dallas_series.csv and add pct (clearance * 100)."""
    s = pd.read_csv(path)
    s["pct"] = s["clearance"] * 100
    return s


def full_range(s, first=FIRST_YEAR, last=LAST_YEAR):
    """Reindex to every year in [first, last] so a missing year becomes NaN.

    plt.plot draws a straight line across a gap by default, which invents
    data. A NaN row makes matplotlib break the line instead.
    """
    return s.set_index("year").reindex(range(first, last + 1))


def split_partial(full, partial=PARTIAL_YEAR):
    """(complete years, partial year) -- the partial year is plotted apart."""
    complete = full.copy()
    complete.loc[partial, "pct"] = float("nan")
    return complete, full.loc[[partial]]


# ============================================================
# STEP 2: draw the chart
# ============================================================

def make_chart(s, suspicious_year=SUSPICIOUS_YEAR):
    """Build the figure. Returns (fig, ax) so tests can inspect it."""
    full = full_range(s)
    complete, partial = split_partial(full)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(complete.index, complete["pct"], marker="o", markersize=3.5,
            linewidth=1.5, color="#196B24", label="Cleared (FBI definition)")

    # 2025 is still being reported: hollow marker, no line into it, labeled
    ax.plot(partial.index, partial["pct"], marker="o", markersize=6,
            linestyle="none", markerfacecolor="white", color="#196B24",
            label=f"{PARTIAL_YEAR}: partial year, provisional")

    ax.set_ylim(0, 100)
    ax.set_xlim(FIRST_YEAR - 1, LAST_YEAR + 1)
    ax.set_xlabel("Year")
    ax.set_ylabel(YLABEL)
    ax.set_title(TITLE)
    ax.grid(alpha=0.3)
    ax.legend(loc="lower left", frameon=False)

    # annotate the #1 suspicious year: the chart makes the week-9 argument
    val = float(full.loc[suspicious_year, "pct"])
    prev = float(full.loc[suspicious_year - 1, "pct"])
    ax.annotate(f"{suspicious_year}: {val:.0f}% (from {prev:.0f}% in "
                f"{suspicious_year - 1}) — reporting change?",
                xy=(suspicious_year, val),
                xytext=(suspicious_year - 30, val + 10),
                arrowprops=dict(arrowstyle="->"))

    fig.tight_layout()
    return fig, ax


def main():
    s = load_series()
    gaps = full_range(s)["pct"].isna().sum()
    print(f"{SERIES_FILE}: {len(s)} years, {s.year.min()}-{s.year.max()}, "
          f"{gaps} missing year(s)")

    fig, _ = make_chart(s)
    OUT_FILE.parent.mkdir(exist_ok=True)
    fig.savefig(OUT_FILE, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {OUT_FILE}")


if __name__ == "__main__":
    main()
