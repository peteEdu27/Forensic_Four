"""Fetch every murder incident from Dallas OpenData into data/case.db.
Run: python -m src.fetch_city"""
import json, os, sqlite3
from pathlib import Path
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.environ["DALLAS_APP_TOKEN"]
URL = "https://www.dallasopendata.com/resource/qv6i-rri7.json"
WHERE = "offincident like '%MURDER%' OR offincident = 'HOMICIDE'"
RAW = Path("data/raw_incidents.json")
DB = Path("data/case.db")
PAGE = 5000


def fetch_all() -> list[dict]:
    if RAW.exists():
        print("using cache", RAW)
        return json.loads(RAW.read_text())
    rows, offset = [], 0
    while True:
        r = requests.get(URL, params={
            "$where": WHERE, "$order": "incidentnum",
            "$limit": PAGE, "$offset": offset, "$$app_token": TOKEN,
        }, timeout=60)
        r.raise_for_status()
        page = r.json()
        rows.extend(page)
        print(f"offset {offset}: {len(page)} rows")
        if len(page) < PAGE:
            break
        offset += PAGE
    RAW.write_text(json.dumps(rows))
    return rows


def flatten(rows: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    geo = df.pop("geocoded_column")
    df["lat"] = geo.apply(lambda g: float(g["latitude"]) if isinstance(g, dict) else None)
    df["lon"] = geo.apply(lambda g: float(g["longitude"]) if isinstance(g, dict) else None)
    df = df[[c for c in df.columns if not c.startswith(":@")]]   # drop computed regions
    df["servyr"] = pd.to_numeric(df["servyr"], errors="coerce")
    return df


def main() -> None:
    df = flatten(fetch_all())
    con = sqlite3.connect(DB)
    df.to_sql("incidents", con, if_exists="replace", index=False)
    n = pd.read_sql("SELECT COUNT(*) AS n FROM incidents", con).n[0]
    print(f"case.db: {n} rows in incidents")


if __name__ == "__main__":
    main()
