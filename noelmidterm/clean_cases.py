# clean_cases.py
# Midterm Project: The Cold Case File
# ONE command turns the raw file into the clean files and a report:   python clean_cases.py
# Reads:  midterm_cases_raw.csv
# Writes: cases_clean.csv, quarantine.csv, report.txt
# Pipeline: csv.reader loads the file -> Case.from_row() cleans each field -> try/except quarantines bad rows
#           -> a set of case_ids drops duplicates -> csv.writer saves the output files

import csv                                           # Python's built-in CSV module: csv.reader to read (week 6), csv.writer to write
from case_model import Case                          # bring in the Case class (and, through it, every cleaner) from case_model.py

RAW_FILE = "midterm_cases_raw.csv"                   # the input file, as handed to us
CLEAN_FILE = "cases_clean.csv"                       # output 1: every usable case
QUARANTINE_FILE = "quarantine.csv"                   # output 2: every rejected row, with line number and reason
REPORT_FILE = "report.txt"                           # output 3: the numbers the briefing is built from
DECADES = ["1980s", "1990s", "2000s", "2010s", "2020s"]   # the decades the report must cover, in order


# ============================================================
# STEP 1: load_cases() - ONE pass over every row, with accumulators for every count
# ============================================================

def load_cases(path):                                # path = the raw CSV file name
    """Load every row into Case objects; skip blanks/headers, quarantine bad rows, drop duplicates."""   # docstring
    cases = []                                       # list of clean Case objects (accumulator, set up BEFORE the loop - week 3)
    quarantine = []                                  # list of (line_number, reason, raw_row) tuples for rejected rows
    seen_ids = set()                                 # a set keeps one of each - the dedupe machine (week 4)
    counts = {                                       # a dict of labeled counters, all starting at 0
        "lines": 0,                                  # every line in the file, including line 1
        "blank": 0,                                  # blank or whitespace-only lines (skipped, not quarantined)
        "header": 0,                                 # header rows: line 1 plus any repeated mid-file (skipped, not quarantined)
        "data_rows": 0,                              # every row that is NOT blank and NOT a header - the top of the intake funnel
        "duplicates": 0,                             # rows whose cleaned case_id was already kept
        "raw_closed": 0,                             # data rows whose raw status is EXACTLY "CLOSED" - for the raw-vs-clean comparison
    }                                                # end of the counts dict
    reasons = {}                                     # dict: quarantine reason -> how many rows had it

    with open(path, newline="") as f:                # open the file; newline="" lets csv handle line endings; "with" closes it automatically (week 6)
        reader = csv.reader(f)                       # csv.reader splits each line into a LIST of fields, keeping commas inside quotes ("Mendoza, C")
        for line_num, row in enumerate(reader, start=1):   # enumerate gives a counter AND the row; start=1 so line_num matches the line number in VS Code
            counts["lines"] += 1                     # count every line we read (update INSIDE the loop - week 3)

            if "".join(row).strip() == "":           # glue all fields together and strip spaces; "" means the line was empty or only spaces
                counts["blank"] += 1                 # count it as a skipped blank line
                continue                             # continue = skip to the next line; a blank line is not a record

            if row[0].strip().lower() == "case_id":  # the first field is the column title, so this is the header row (line 1 or a repeat from a merged export)
                counts["header"] += 1                # count it as a skipped header
                continue                             # skip it; a header is not a record

            counts["data_rows"] += 1                 # from here on, this is a real data row that must be accounted for
            if len(row) > 7 and row[7] == "CLOSED":  # face-value count: the status field exists and is EXACTLY "CLOSED" (no strip, no upper)
                counts["raw_closed"] += 1            # this is how a careless analyst would count clearances

            try:                                     # TRY the risky thing (week 6 quarantine pattern)...
                case = Case.from_row(row)            # ...clean every field; from_row raises ValueError with a reason if a critical field is broken
            except ValueError as err:                # ...catch ONLY ValueError (never a bare except) and call it err
                reason = str(err)                    # str(err) = the reason text we raised, e.g. "invalid date"
                quarantine.append((line_num, reason, ",".join(row)))   # log the line number, the reason, and the raw fields glued back with commas
                reasons[reason] = reasons.get(reason, 0) + 1           # count this reason: .get(reason, 0) gives 0 the first time we see it (week 4)
                continue                             # keep looping - one bad row never kills the others

            if case.case_id in seen_ids:             # the cleaned case_id is already in the set, so this row is a duplicate
                counts["duplicates"] += 1            # count it
                continue                             # keep the FIRST one only, so skip this one
            seen_ids.add(case.case_id)               # remember this id so later copies are caught
            cases.append(case)                       # a clean, unique case - keep it

    cases = sorted(cases, key=lambda c: c.case_id)   # sorted(key=lambda ...) sorts objects by any attribute (week 7); the output must be sorted by case_id
    return cases, quarantine, counts, reasons        # hand all four results back to the caller


# ============================================================
# STEP 2: write the two CSV files
# ============================================================

def write_clean(cases, path):                        # cases = list of Case objects, path = output file name
    """Write cases_clean.csv in the exact required column order."""   # docstring
    with open(path, "w", newline="") as f:           # "w" = write mode (creates or overwrites the file)
        writer = csv.writer(f)                       # csv.writer adds quotes automatically when a field contains a comma ("Ramirez, K")
        writer.writerow(["case_id", "victim_name", "sex", "age", "incident_date",   # the header row, columns 1-5
                         "year", "beat", "status", "callback_phone"])               # columns 6-9
        for case in cases:                           # one line per clean case
            writer.writerow(case.to_row())           # to_row() returns the 9 fields in the right order


def write_quarantine(quarantine, path):              # quarantine = list of (line_number, reason, raw_row) tuples
    """Write quarantine.csv: one row per rejected line with its line number and reason."""   # docstring
    with open(path, "w", newline="") as f:           # open for writing
        writer = csv.writer(f)                       # the raw_row text contains commas, so csv.writer will quote it
        writer.writerow(["line_number", "reason", "raw_row"])   # header row
        for line_num, reason, raw in quarantine:     # unpack each 3-item tuple into three names
            writer.writerow([line_num, reason, raw]) # write it as one CSV row


# ============================================================
# STEP 3: build_report() - every number report.txt must answer
# ============================================================

def rate(part, whole):                               # a tiny helper so we never divide by zero
    """Return part / whole as a fraction, or 0 when whole is 0."""   # docstring
    if whole == 0:                                   # dividing by zero would crash the program
        return 0                                     # treat an empty group as a 0% rate
    return part / whole                              # e.g. 3 / 4 = 0.75, printed later as 75.0% with :.1%


def build_report(cases, quarantine, counts, reasons):   # takes everything load_cases() returned
    """Return the report as a list of text lines."""     # docstring
    lines = []                                       # collect the lines first, then print AND save them (collect-then-analyze, week 4)

    # ---------- Section 1: Intake ----------
    lines.append("=" * 60)                           # "=" * 60 repeats the character 60 times, a divider line
    lines.append("1. INTAKE")                        # section title
    lines.append("=" * 60)                           # divider
    lines.append(f"{'Lines in file:':<34}{counts['lines']:>6,}")          # :<34 pads the label left, :>6, right-aligns the number with a thousands comma (week 2)
    lines.append(f"{'Blank lines skipped:':<34}{counts['blank']:>6,}")    # skipped, not quarantined
    lines.append(f"{'Header rows skipped:':<34}{counts['header']:>6,}")   # line 1 plus the repeated ones
    lines.append(f"{'Data rows read:':<34}{counts['data_rows']:>6,}")     # top of the funnel
    lines.append(f"{'Rows quarantined:':<34}{len(quarantine):>6,}")       # len() of the quarantine list
    for reason in sorted(reasons, key=reasons.get, reverse=True):         # rank the reasons, most common first (week 4 dict sort)
        lines.append(f"{'   ' + reason + ':':<34}{reasons[reason]:>6,}")  # indented reason label and its count
    lines.append(f"{'Duplicates removed:':<34}{counts['duplicates']:>6,}")   # same case_id after cleaning
    lines.append(f"{'Clean cases:':<34}{len(cases):>6,}")                 # what is left
    funnel = counts["data_rows"] - len(quarantine) - counts["duplicates"]  # the funnel must add up: data rows - quarantined - duplicates
    lines.append(f"Funnel check: {counts['data_rows']:,} - {len(quarantine):,} - {counts['duplicates']:,} = {funnel:,}")   # show the subtraction itself
    lines.append("")                                 # blank line between sections

    # ---------- Section 2: Clearance ----------
    closed_total = 0                                 # accumulator: CLOSED clean cases
    open_cases = []                                  # list of OPEN Case objects, used by sections 3-5
    decade_total = {}                                # dict: decade label -> number of cases
    decade_closed = {}                               # dict: decade label -> number of CLOSED cases
    for case in cases:                               # one pass over the clean cases
        decade = str(case.year)[0:3] + "0s"          # slice the first 3 digits of the year: "1987" -> "198" -> "1980s" (week 2 slicing)
        decade_total[decade] = decade_total.get(decade, 0) + 1   # count the case in its decade
        if case.status == "CLOSED":                  # a cleared case
            closed_total += 1                        # overall closed counter
            decade_closed[decade] = decade_closed.get(decade, 0) + 1   # closed counter for this decade
        else:                                        # the only other status left after cleaning is OPEN
            open_cases.append(case)                  # keep it for the open-case questions
    clean_rate = rate(closed_total, len(cases))      # overall clearance rate = CLOSED / clean cases

    lines.append("=" * 60)                           # divider
    lines.append("2. CLEARANCE")                     # section title
    lines.append("=" * 60)                           # divider
    lines.append(f"Overall clearance rate: {closed_total:,} CLOSED / {len(cases):,} clean cases = {clean_rate:.1%}")   # :.1% turns 0.512 into 51.2%
    lines.append("")                                 # spacing
    lines.append(f"{'DECADE':<10}{'CASES':>8}{'CLOSED':>8}{'RATE':>9}")   # table header, columns lined up with padding
    for decade in DECADES:                           # 1980s through 2020s, in order
        total = decade_total.get(decade, 0)          # .get(..., 0) is safe even if a decade had no cases
        closed = decade_closed.get(decade, 0)        # closed cases in this decade
        lines.append(f"{decade:<10}{total:>8,}{closed:>8,}{rate(closed, total):>9.1%}")   # one table row per decade
    lines.append("")                                 # spacing

    # ---------- Section 3: Open cases ----------
    stale = [c for c in open_cases if c.is_stale]    # list comprehension (week 7): keep only the open cases whose is_stale property is True
    oldest = sorted(open_cases, key=lambda c: c.incident_date)[:5]   # sort open cases by date (YYYY-MM-DD text sorts in time order), [:5] = the first five
    lines.append("=" * 60)                           # divider
    lines.append("3. OPEN CASES")                    # section title
    lines.append("=" * 60)                           # divider
    lines.append(f"Open cases:                  {len(open_cases):,}")   # how many are still open
    lines.append(f"Stale (open 5+ years):         {len(stale):,}  ({rate(len(stale), len(open_cases)):.1%} of open cases)")   # stale count and share
    lines.append("The 5 oldest open cases:")     # sub-heading
    for case in oldest:                              # loop the five oldest
        lines.append(f"   {case.summary()}")         # summary() is the Case method that formats one line
    lines.append("")                                 # spacing

    # ---------- Section 4: Beats ----------
    beat_open = {}                                   # dict: beat -> open cases
    beat_total = {}                                  # dict: beat -> all cases
    beat_closed = {}                                 # dict: beat -> closed cases
    for case in cases:                               # one pass over the clean cases
        if case.beat == "":                          # a blank beat cannot be ranked
            continue                                 # skip it for this section only
        beat_total[case.beat] = beat_total.get(case.beat, 0) + 1   # count every case in its beat
        if case.status == "OPEN":                    # open case
            beat_open[case.beat] = beat_open.get(case.beat, 0) + 1   # count it as open
        else:                                        # closed case
            beat_closed[case.beat] = beat_closed.get(case.beat, 0) + 1   # count it as closed
    top_beats = sorted(beat_open, key=beat_open.get, reverse=True)[:10]   # rank beats by open-case count, biggest first, keep the top 10 (week 4)
    lines.append("=" * 60)                           # divider
    lines.append("4. TOP 10 BEATS BY OPEN CASES")    # section title
    lines.append("=" * 60)                           # divider
    lines.append(f"{'BEAT':<6}{'OPEN':>6}{'TOTAL':>7}{'CLEARANCE':>11}")   # table header
    for beat in top_beats:                           # loop the 10 beats in rank order
        beat_rate = rate(beat_closed.get(beat, 0), beat_total[beat])        # this beat's clearance rate = closed / total in the beat
        lines.append(f"{beat:<6}{beat_open[beat]:>6}{beat_total[beat]:>7}{beat_rate:>11.1%}  {'#' * beat_open[beat]}")   # the # bar is a zero-library histogram (week 4)
    lines.append("")                                 # spacing

    # ---------- Section 5: Leads ----------
    with_phone = [c for c in open_cases if c.callback_phone != ""]   # open cases whose tip notes held a phone number
    lines.append("=" * 60)                           # divider
    lines.append("5. LEADS")                         # section title
    lines.append("=" * 60)                           # divider
    lines.append(f"Open cases with a callback phone: {len(with_phone):,} / {len(open_cases):,} = {rate(len(with_phone), len(open_cases)):.1%}")   # the % the briefing asks for
    lines.append("")                                 # spacing

    # ---------- Section 6: Raw vs clean ----------
    raw_rate = rate(counts["raw_closed"], counts["data_rows"])   # face-value rate: exact "CLOSED" rows / all raw data rows
    gap = (clean_rate - raw_rate) * 100              # the difference in percentage points (x 100 turns 0.12 into 12)
    lines.append("=" * 60)                           # divider
    lines.append("6. RAW VS CLEAN")                  # section title
    lines.append("=" * 60)                           # divider
    lines.append(f"Raw rows with status exactly 'CLOSED': {counts['raw_closed']:,} / {counts['data_rows']:,} raw data rows = {raw_rate:.1%}")   # the naive number
    lines.append(f"Clean clearance rate:                  {closed_total:,} / {len(cases):,} clean cases = {clean_rate:.1%}")                  # our number
    lines.append(f"The raw count is off by {gap:.1f} percentage points.")   # :.1f = one decimal place
    return lines                                     # hand the finished list of lines back


# ============================================================
# STEP 4: Run it. The guard means pytest can import from this file without running the whole pipeline.
# ============================================================

if __name__ == "__main__":                           # True only when run directly: python clean_cases.py
    cases, quarantine, counts, reasons = load_cases(RAW_FILE)   # load and clean; unpack the four results
    write_clean(cases, CLEAN_FILE)                   # save output 1
    write_quarantine(quarantine, QUARANTINE_FILE)    # save output 2
    report_lines = build_report(cases, quarantine, counts, reasons)   # build the report text
    with open(REPORT_FILE, "w") as f:                # save output 3
        for line in report_lines:                    # one line at a time
            print(line)                              # show it on screen
            f.write(line + "\n")                     # and write it to report.txt; "\n" ends the line
