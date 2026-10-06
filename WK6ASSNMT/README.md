# Week 6: Armor

Load the case CSV without crashing on bad rows. Good rows are loaded. Bad rows go into a quarantine log with their line number and the reason they failed.

## Files
- `intake.py`: `parse_row()`, `load_cases()` and the report
- `test_intake.py`: pytest tests for `parse_row()`
- `data/wk06_data_raw_cases_100.csv`: 100 raw case rows plus a header

## Steps
1. Open the CSV and find bad rows by hand before writing any code
2. `parse_row(row)` checks the field count, converts the age and checks the date, raising `ValueError` with a reason when any check fails
3. `load_cases(path)` runs `csv.reader` with a try/except quarantine loop and returns `(good, quarantine)`
4. Report: loaded count, quarantined count, and the full quarantine log with line numbers and reasons
5. `test_intake.py`: one good-row test and two bad-row tests

## Run
```
python WK6ASSNMT/intake.py
python -m pytest WK6ASSNMT
```
(Install pytest first if needed: `python -m pip install pytest`)

## Results
- **Loaded:** 89
- **Quarantined:** 12

| Line | Case     | Reason                      |
|------|----------|-----------------------------|
| 2    | CC-20000 | date is missing             |
| 17   | CC-20015 | age is not a number: 'unknown' |
| 26   | CC-20024 | expected 8 fields, got 6    |
| 30   | CC-20028 | expected 8 fields, got 6    |
| 34   | CC-20032 | expected 8 fields, got 6    |
| 38   | (blank)  | expected 8 fields, got 0    |
| 42   | CC-20039 | date is missing             |
| 43   | CC-20040 | expected 8 fields, got 6    |
| 44   | CC-20041 | expected 8 fields, got 6    |
| 50   | CC-20047 | age is not a number: 'unknown' |
| 64   | CC-20061 | age is not a number: 'unknown' |
| 86   | CC-20083 | expected 8 fields, got 6    |

Names such as `"KIRKLAND, MONICA, JR, III"` have commas inside quotes. They look broken, but `csv.reader` reads them as one field, so those rows load fine.

Tests: 3 passed.
