# Week 5: Pattern Hunters

Use regular expressions to pull phone numbers, case refs, beats and dates out of free-text tipline reports.

## Files
- `pattern_hunt.py`: the extractors (each its own `def` with a docstring), the tip summaries and the callback count
- `data/wk05_data_tipline.txt`: 24 raw tips

## Steps
1. Read five tips out loud first to see the patterns before coding them
2. Build `extract_phones()`, test it on one tip by eye (tip 2), then run it on all 24
3. Write `extract_case_refs()`, `extract_beats()`, `extract_iso_dates()` and `extract_us_dates()`
4. `summarize_tip()` calls every extractor and prints one line per tip
5. Callback count: tips with at least one phone vs. tips without

Stretch: `extract_month_dates()` also catches month-name dates (`February 15, 2017` and `15 December 2020`), so every tip shows a date.

## Run
```
python WK5ASSNMT/pattern_hunt.py
```

## Results
```
Tips processed:       24
Tips with a callback: 15
Tips with NO callback: 9  <- these leads die without follow-up
```
- Phones are caught in both formats: `(214) 555-1234` and `214-555-1234`
- Both numeric date formats are extracted: ISO (`2019-02-19`) and US (`4/7/2019`)
