# tests/test_charts.py - checks for src/charts.py and src/casemap.py
# Run from the repo root with:  pytest
#
# Like test_series.py, these build tiny frames in memory instead of reading
# data/ (gitignored) or reports/, so they pass on a fresh clone.

import math

import pandas as pd

from src.casemap import (CLOSED_COLOR, OPEN, OPEN_COLOR, legend_html,
                         make_map, marker_color)
from src.charts import YLABEL, full_range, make_chart, split_partial


def make_series(years):
    s = pd.DataFrame({"year": years, "clearance": [0.5] * len(years)})
    s["pct"] = s["clearance"] * 100
    return s


def test_full_range_turns_missing_year_into_nan():
    full = full_range(make_series([2000, 2001, 2003]), first=2000, last=2003)
    assert list(full.index) == [2000, 2001, 2002, 2003]
    assert math.isnan(full.loc[2002, "pct"])


def test_split_partial_keeps_partial_year_off_the_line():
    full = full_range(make_series([2023, 2024, 2025]), first=2023, last=2025)
    complete, partial = split_partial(full, partial=2025)
    assert math.isnan(complete.loc[2025, "pct"])
    assert list(partial.index) == [2025]
    assert partial.loc[2025, "pct"] == 50


def test_chart_passes_honesty_checklist():
    s = make_series(list(range(1965, 2026)))
    fig, ax = make_chart(s)
    assert ax.get_ylim() == (0, 100)
    assert "Source" in ax.get_ylabel() and YLABEL == ax.get_ylabel()
    assert "Dallas" in ax.get_title() and "1965" in ax.get_title()
    assert any("2017" in t.get_text() for t in ax.texts)   # annotation


def test_marker_color_by_disposition():
    assert marker_color(OPEN) == OPEN_COLOR
    assert marker_color("Closed by arrest") == CLOSED_COLOR
    assert marker_color("Closed without arrest") == CLOSED_COLOR


def test_map_has_one_marker_per_case_and_legend():
    w = pd.DataFrame({"lat": [32.7, 32.8, 32.9], "lon": [-96.8] * 3,
                      "disposition": [OPEN, "Closed by arrest",
                                      "Closed without arrest"]})
    html = make_map(w).get_root().render()
    assert html.count("L.circleMarker(") == 3
    assert "Open / no arrest (1)" in html and "Closed (2)" in html


def test_legend_counts_formatted():
    assert "(1,567)" in legend_html(1567, 0)
