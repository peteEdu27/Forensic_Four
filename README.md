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
```

## Repo layout

```
Forensic_Four/
├─ data/              # raw inputs (gitignored except .gitkeep)
├─ src/
│  ├─ __init__.py
│  ├─ intake.py       # parse_row, load_cases
│  ├─ models.py       # the Case class
│  └─ patterns.py     # regex extractors
├─ tests/
└─ reports/           # outputs: CSVs, charts, maps
```
