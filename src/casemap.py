# src/casemap.py - Week 10: Operation The Picture (part 2, the map)
# Goal: put every Washington Post Dallas homicide (2007 to early 2017) on a
# map of Dallas, colored by whether anyone was arrested, and save it to
# reports/dallas_map.html. That file embeds as-is in week 14's dashboard.
#
# Run from the repo root (after python -m src.get_data):
#   python -m src.casemap
#
# Definition: this map uses the Post's disposition column. "Open/No arrest" is
# orange; "Closed by arrest" and "Closed without arrest" are green. That is
# NOT the FBI clearance definition used in src/charts.py.
#
# Aggregate analysis only. get_data.py already dropped victim names, and no
# marker carries a popup or tooltip with case details.

from pathlib import Path

import folium
import pandas as pd

WAPO_FILE = Path("data/wapo_dallas.csv")
OUT_FILE = Path("reports/dallas_map.html")

EXPECTED_MARKERS = 1567
OPEN = "Open/No arrest"
OPEN_COLOR, CLOSED_COLOR = "orange", "green"

DALLAS_CENTER = [32.78, -96.80]


# ============================================================
# STEP 1: load the cases, drop any that can't be placed
# ============================================================

def load_cases(path=WAPO_FILE):
    """Return (cases with coordinates, number of rows dropped for NaN lat/lon).

    A single NaN lat or lon makes the folium map render blank.
    """
    w = pd.read_csv(path)
    placed = w.dropna(subset=["lat", "lon"])
    return placed, len(w) - len(placed)


def marker_color(disposition):
    return OPEN_COLOR if disposition == OPEN else CLOSED_COLOR


# ============================================================
# STEP 2: build the map
# ============================================================

def legend_html(n_open, n_closed):
    """Fixed legend box; the counts come from the data, not typed in."""
    return f"""
<div style="position:fixed;bottom:30px;left:30px;background:white;padding:8px 12px;
border:1px solid #999;font-family:sans-serif;font-size:13px;z-index:9999">
<b>Dallas homicides 2007–2017</b><br>
<span style="color:{OPEN_COLOR}">●</span> Open / no arrest ({n_open:,})<br>
<span style="color:{CLOSED_COLOR}">●</span> Closed ({n_closed:,})<br>
Source: Washington Post Unsolved Homicide Database
</div>"""


ESRI_TILES = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}"
ESRI_ATTR = "Tiles &copy; Esri"


def make_map(w):
    """One CircleMarker per case, colored by disposition, plus a legend."""
    # default OpenStreetMap tiles (deck 10, slide 6) get blocked in some
    # environments, and the supplement's "cartodbpositron" now needs a CARTO
    # API key and can render blank. Esri's basemap needs neither.
    m = folium.Map(location=DALLAS_CENTER, zoom_start=11,
                    tiles=ESRI_TILES, attr=ESRI_ATTR)

    for _, row in w.iterrows():
        color = marker_color(row["disposition"])
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=3, color=color, fill=True, fill_opacity=0.6, weight=1,
        ).add_to(m)

    n_open = int((w["disposition"] == OPEN).sum())
    m.get_root().html.add_child(
        folium.Element(legend_html(n_open, len(w) - n_open)))
    return m


def main():
    w, dropped = load_cases()
    print(f"{WAPO_FILE}: {len(w)} cases with coordinates, "
          f"{dropped} dropped for missing lat/lon (expect {EXPECTED_MARKERS} markers)")
    print(w["disposition"].value_counts().to_string())

    m = make_map(w)
    OUT_FILE.parent.mkdir(exist_ok=True)
    m.save(OUT_FILE)
    print(f"wrote {OUT_FILE}: {len(w)} markers")


if __name__ == "__main__":
    main()
