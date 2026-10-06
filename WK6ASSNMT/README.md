# Week 6: Bulletproof Intake

Load the case CSV without crashing on bad rows. Good rows are loaded. Bad rows go into a quarantine log with their line number and the reason they failed.

## Files
- `intake_safe.py`: `parse_row()`, `load_cases()` and the report
- `test_intake.py`: pytest tests for `parse_row()` (one good row, two bad rows)
- `data/wk06_data_raw_cases_100.csv`: 100 raw case rows plus a header

## Steps
1. Open the CSV and find bad rows by hand before writing any code
2. `parse_row(row)` checks the field count, converts the age and checks the date, raising `ValueError` with a reason when any check fails
3. `load_cases(path)` runs `csv.reader` with a try/except quarantine loop and returns `(good, quarantine)`
4. Report: loaded count, quarantined count, and the full quarantine log with line numbers and reasons
5. `test_intake.py`: one good-row test and two bad-row tests

## Run
From inside `WK6ASSNMT/`:
```
python intake_safe.py
pytest test_intake.py
```
(Install pytest first if needed: `python -m pip install pytest`)

## Results
```
Rows loaded cleanly:   89
Rows quarantined:      11

Quarantine log:
  line   2 | CC-20000 | date is missing
  line  17 | CC-20015 | age is not a number: 'unknown'
  line  26 | CC-20024 | expected 8 fields, got 6
  line  30 | CC-20028 | expected 8 fields, got 6
  line  34 | CC-20032 | expected 8 fields, got 6
  line  42 | CC-20039 | date is missing
  line  43 | CC-20040 | expected 8 fields, got 6
  line  44 | CC-20041 | expected 8 fields, got 6
  line  50 | CC-20047 | age is not a number: 'unknown'
  line  64 | CC-20061 | age is not a number: 'unknown'
  line  86 | CC-20083 | expected 8 fields, got 6
```
```
$ pytest test_intake.py  ->  3 passed
```

- **No crashes:** the whole file runs from start to finish.
- **Specific excepts:** every `except` catches `ValueError` by name; there is no bare `except`.
- **Blank line skipped:** the blank line after CC-20035 is not a case, so it is skipped rather than quarantined.
- **Quoted names load fine:** names like `"KIRKLAND, MONICA, JR, III"` have commas inside quotes, but `csv.reader` reads them as one field.
