# Week 5: Pattern Hunters

Use regular expressions to pull phone numbers, case refs, beats and dates out of free-text tipline reports.

## Files
- `patterns.py`: the extractors, the tip summaries and the callback count
- `data/wk05_data_tipline.txt`: 24 raw tips

## Steps
1. Read five tips out loud first to see the patterns before coding them
2. Build `extract_phones()`, test it on one tip by eye (tip 2), then run it on all 24
3. Write `extract_case_refs()`, `extract_beats()`, `extract_iso_dates()` and `extract_us_dates()`
4. `summarize_tip()` calls every extractor and prints one line per tip
5. Callback count: tips with at least one phone vs. tips without

## Run
```
python WK5ASSNMT/patterns.py
```

## Results
- 24 tips: 15 have a phone, 9 do not
- Phones come in two formats: `784-550-8605` and `(783) 200-4610`
- Dates written out in words (e.g. "February 15, 2017") are not captured, because the assignment only asks for ISO (`2019-02-19`) and US (`4/7/2019`) formats
