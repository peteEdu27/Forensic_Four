"""Download the week 9 sources into data/. Run: python -m src.get_data"""
# src/get_data.py - Week 9: Real Data
# Rebuilds data/ from nothing. Raw files are gitignored, so anyone who clones
# the repo runs this once and gets the exact same inputs we used.
#
# Sources (cited in README.md and reports/SOURCES.md):
#   Murder Accountability Project, UCR homicide and clearance data (UCR65_25)
#   The Washington Post, Unsolved Homicide Database (data-homicides)
from pathlib import Path
import pandas as pd
import requests

DATA = Path("data")
DATA.mkdir(exist_ok=True)

MAP_URL = ("https://www.dropbox.com/scl/fi/4y2a6yy0pv4lxffm7sa4v/UCR65_25.csv"
           "?rlkey=jhs7ktqhb9h3dnml1wety4nhb&st=7rxppnar&dl=1")
WAPO_URL = ("https://raw.githubusercontent.com/washingtonpost/"
            "data-homicides/master/homicide-data.csv")

# The Post's file must give exactly this many Dallas rows.
EXPECTED_WAPO_DALLAS = 1567


def fetch(url: str, dest: Path) -> None:
    if dest.exists():
        print(f"cached: {dest}")
        return
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    # Dropbox serves an HTML page instead of the CSV when a link rotates.
    if r.content[:200].lstrip().lower().startswith((b"<!doctype", b"<html")):
        raise RuntimeError(
            f"{url} returned HTML, not a CSV. The link probably rotated: "
            "copy the current one from murderdata.org/p/data-docs.html")
    dest.write_bytes(r.content)
    print(f"saved: {dest} ({dest.stat().st_size:,} bytes)")


def main() -> None:
    fetch(MAP_URL, DATA / "map_ucr.csv")
    fetch(WAPO_URL, DATA / "wapo_all.csv")

    # the Post's file is Latin-1, not UTF-8; without this pandas raises UnicodeDecodeError
    wapo = pd.read_csv(DATA / "wapo_all.csv", encoding="latin-1")
    # filter on city, not state: state == "TX" pulls in other Texas cities
    # victim names are dropped here so they never reach a script or a chart
    dallas = wapo[wapo["city"] == "Dallas"].drop(
        columns=["victim_last", "victim_first"])
    dallas.to_csv(DATA / "wapo_dallas.csv", index=False)
    print(f"wapo_dallas.csv: {len(dallas)} rows (expect {EXPECTED_WAPO_DALLAS})")


if __name__ == "__main__":
    main()
