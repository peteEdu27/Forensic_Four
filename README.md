## The Dallas Clearance Project
# GitHub Usernames: ddt240000, uxp230006, pja230002, nxl240008
# Repo Link: https://github.com/peteEdu27/Forensic_Four.git
# Team Name: Forensic_Four
# Team mates: Peter, Utsab, David, Noel

## Setup from zero

```bash
git clone https://github.com/peteEdu27/Forensic_Four.git
cd Forensic_Four
python -m venv .venv
source .venv/bin/activate      # Mac/Linux
.venv\Scripts\activate         # Windows
pip install -r requirements.txt
pytest
python -m src.get_data         # downloads both sources into data/
python -m src.series           # writes reports/dallas_series.csv + sanity checks
```

## Repo layout

```
Forensic_Four/
├─ data/              # raw inputs (gitignored except .gitkeep)
├─ src/
│  ├─ __init__.py
│  ├─ get_data.py     # wk9: downloads MAP + WaPo into data/
│  ├─ intake.py       # parse_row, load_cases
│  ├─ models.py       # the Case class
│  ├─ patterns.py     # regex extractors
│  └─ series.py       # wk9: Dallas clearance-by-year series
├─ tests/
└─ reports/           # outputs: CSVs, charts, maps
```

## Data sources

Raw files live in `data/` and are gitignored; `python -m src.get_data` rebuilds them.
Aggregate analysis only. Victim names are dropped on load. See [reports/SOURCES.md](reports/SOURCES.md).

- Murder Accountability Project, UCR homicide and clearance data (UCR65_25), murderdata.org, accessed 2026-10-28.
- The Washington Post, Unsolved Homicide Database, github.com/washingtonpost/data-homicides, 2018. CC BY-NC-SA 4.0.
