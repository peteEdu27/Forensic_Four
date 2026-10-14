import csv                               # standard library module for reading/writing CSV files
from case_model import Case              # the Case class that cleans + validates one row

DECADES = [1980, 1990, 2000, 2010, 2020] # the five decades the report breaks clearance rates down by

def load_cases(path):           # read the raw file, return (clean cases, quarantine log, intake stats)
    cases = []                  # clean, deduped Case objects, in file order
    quarantine = []             # [line_number, reason, raw_row] for every rejected row
    dupe_case_ids = set()       # a set catches duplicate case_ids after cleaning
    reasons = {}                # dict counts quarantine reasons, e.g. {"missing date": 41}

    rows_read = 0               # intake counters, all start at zero
    blanks = 0
    headers = 0
    duplicates = 0
    raw_cases_closed = 0
    raw_cases_count = 0

    with open(path, newline="") as f:      # open the raw case file for reading
        reader = csv.reader(f)             # csv.reader splits each line into a list of fields
        header = next(reader)              # read row 1 (the header) so we can detect it again later

        for number, row in enumerate(reader, 2):  # walk every data row; start=2 since line 1 was the header
            rows_read += 1                        # count every row, good or bad

            is_blank = True                 # assume blank until we find a non-empty field
            for field in row:               # check every field in this row
                if field.strip() != "":     # a field with real content in it
                    is_blank = False        # so this row isn't blank after all
                    break                   # no need to check the rest
            if is_blank:                    # no fields at all, or every field was empty/whitespace
                blanks += 1                 # count it
                continue                    # skip it, don't quarantine it

            if row == header:              # a repeated header row (merged exports)
                headers += 1               # count it
                continue                   # skip it, don't quarantine it

            raw_cases_count += 1                       # this is a real data row, count it toward the raw-vs-clean comparison
            if len(row) == 9 and row[7] == "CLOSED":   # tally the RAW status before any cleaning touches it
                raw_cases_closed += 1                  # this raw row's status field was exactly "CLOSED"

            try:
                case = Case.from_row(row)             # clean every field (in case_model); raises ValueError if something can't be fixed
            except ValueError as error:                              # the row has a critical field that couldn't be repaired
                reason = str(error)                                  # the quarantine reason, e.g. "missing date"
                reasons[reason] = reasons.get(reason, 0) + 1         # bump that reason's count
                quarantine.append([number, reason, ",".join(row)])   # log the line number, reason, and raw row
                continue                                             # keep looping, always keep looping

            if case.case_id in dupe_case_ids:        # same case_id already kept once, cleaned
                duplicates += 1                      # count it
                continue                             # drop this duplicate, keep the first one

            dupe_case_ids.add(case.case_id)          # remember this case_id so later duplicates get caught
            cases.append(case)                       # keep this clean case

    stats = {                          # bundle every intake number the report needs
        "rows_read": rows_read,
        "blanks_skipped": blanks,
        "headers_skipped": headers,
        "reason_counts": reasons,
        "duplicates_removed": duplicates,
        "raw_status_closed": raw_cases_closed,
        "raw_rows_counted": raw_cases_count,
    }
    return cases, quarantine, stats     # everything downstream needs

def case_id_key(c):                                                                            # sort key: sort Case objects by their case_id string
    return c.case_id                                                                           # e.g. "CC-10003" comes before "CC-10017
def write_clean_csv(cases, path):                                                              # write cases_clean.csv, sorted by case_id, in the exact spec format
    cases = sorted(cases, key=case_id_key)                                                     # alphabetical by case_id, as required
    with open(path, "w", newline="") as f:                                                     # open (or create) the output file for writing
        writer = csv.writer(f)                                                                 # csv.writer turns lists back into comma-separated lines
        writer.writerow(["case_id", "victim_name", "sex", "age", "incident_date", "year", "beat", "status", "callback_phone"])# header row, the exact column order from the spec

        for c in cases:                                                                        # one output row per clean case
            age = "" if c.age is None else c.age                                               # blank age stays blank, not "None"
            beat = "" if c.beat is None else c.beat                                            # blank beat stays blank too
            writer.writerow([c.case_id, c.victim_name, c.sex, age, c.incident_date.strftime("%Y-%m-%d"), c.year, beat, c.status, c.callback_phone])# one clean case, in the exact column order from the spec

def write_quarantine_csv(quarantine, path):                       # write quarantine.csv - one row per rejected line
    with open(path, "w", newline="") as f:                        # open (or create) the output file for writing
        writer = csv.writer(f)                                    # csv.writer turns lists back into comma-separated lines
        writer.writerow(["line_number", "reason", "raw_row"])     # header row
        writer.writerows(quarantine)                              # every rejected row, with its line number and reason

def clearance_rate(group):                                       # the fraction of a group of cases that are CLOSED
    closed_count = 0                                             # how many cases in this group are closed
    for c in group:                                              # look at every case in the group
        if c.status == "CLOSED":                                 # this one is closed
            closed_count += 1                                    # count it

    if not group:                                 # avoid dividing by zero on an empty group
        return 0
    return closed_count / len(group)              # fraction of the group that's closed

def incident_date_key(c):                                                                      # sort key: sort Case objects by their incident date
    return c.incident_date                                                                     # oldest incidents sort first

def build_report(cases, stats):                                                                # build the report.txt text out of the cleaned cases + intake stats
    lines = []                                                                                 # every line of the report, joined together at the end
    open_cases = []                                                                            # just the still-open cases
    for c in cases:                                                                            # look at every clean case
        if c.status == "OPEN":                                                                 # this one is still open
            open_cases.append(c)                                                               # keep it

    rate = clearance_rate(cases)                                                               # overall clearance rate across every clean case

    lines.append("=== INTAKE ===")                                                             # section header
    lines.append(f"Data rows read: {stats['rows_read']}")                                      # every row the loop looked at
    lines.append(f"Blank lines skipped: {stats['blanks_skipped']}")                            # blank rows, not quarantined
    lines.append(f"Repeated header rows skipped: {stats['headers_skipped']}")                  # repeated headers, not quarantined
    lines.append("Rows quarantined by reason:")                                                # label for the breakdown below
    for reason in sorted(stats["reason_counts"]):                                              # alphabetical order, for a stable report
        lines.append(f"  {reason}: {stats['reason_counts'][reason]}")                          # how many rows hit this reason
    lines.append(f"Total quarantined: {sum(stats['reason_counts'].values())}")                 # sum of every reason's count
    lines.append(f"Duplicates removed: {stats['duplicates_removed']}")                         # same case_id seen more than once
    lines.append(f"Clean cases: {len(cases)}")                                                 # what's left after quarantine + dedup
    lines.append("")                                                                           # blank line between sections

    lines.append("=== CLEARANCE ===")                                                          # section header
    lines.append(f"Overall clearance rate: {rate:.1%}")                                        # CLOSED / total clean cases
    lines.append("By decade:")                                                                 # label for the breakdown below
    for decade in DECADES:                                                                     # one line per decade, in order
        group = [c for c in cases if c.decade == decade]                                       # every clean case from this decade
        if group:                                                                              # only compute a rate if there's at least one case
            lines.append(f"  {decade}s: {clearance_rate(group):.1%} ({len(group)} cases)")     # this decade's rate
        else:
            lines.append(f"  {decade}s: no cases")                                             # nothing to report for this decade
    lines.append("")                                                                           # blank line between sections

    lines.append("=== OPEN CASES ===")                                                         # section header
    stale = [c for c in open_cases if c.is_stale]                                              # open 5+ years
    lines.append(f"Open cases: {len(open_cases)}")                                             # how many cases are still open
    lines.append(f"Stale (open 5+ years): {len(stale)}")                                       # how many of those are stale
    lines.append("5 oldest open cases:")                                                       # label for the list below
    oldest = sorted(open_cases, key=incident_date_key)[:5]                                     # the five oldest open incidents
    for c in oldest:                                                                           # one line per oldest case
        lines.append(f"  {c.case_id}  {c.incident_date}  beat {c.beat}")                       # case id, date, beat
    lines.append("")                                                                           # blank line between sections

    lines.append("=== BEATS ===")                                                              # section header
    beats = {}                                                                                 # beat -> open case count
    for c in open_cases:                                                                       # only open cases count toward this tally
        if c.beat:                                                                             # skip cases with no beat on file
            beats[c.beat] = beats.get(c.beat, 0) + 1                                           # bump this beat's open count
    lines.append("Top 10 beats by open cases (with that beat's clearance rate):")              # label for the list below
    top_beats = sorted(beats, key=beats.get, reverse=True)[:10]                                # busiest beats first
    for beat in top_beats:                                                                     # one line per top beat
        beat_rate = clearance_rate([c for c in cases if c.beat == beat])                       # this beat's own clearance rate
        lines.append(f"  Beat {beat}: {beats[beat]} open, clearance rate {beat_rate:.1%}")     # beat, open count, rate
    lines.append("")                                                                           # blank line between sections

    lines.append("=== LEADS ===")                                                              # section header
    with_phone = [c for c in open_cases if c.callback_phone]                                   # open cases that have a usable tip phone number
    pct = len(with_phone) / len(open_cases) if open_cases else 0                               # avoid dividing by zero if nothing's open
    lines.append(f"Open cases with a callback phone in tip_notes: {pct:.1%}")                  # the leads number
    lines.append("")                                                                           # blank line between sections

    lines.append("=== RAW VS CLEAN ===")                                                       # section header
    raw_cases_closed, raw_cases_count = stats["raw_status_closed"], stats["raw_rows_counted"]  # pull the raw tallies out
    raw_rate = raw_cases_closed / raw_cases_count if raw_cases_count else 0                    # clearance rate before any cleaning happened
    lines.append(f"Raw clearance rate (status exactly 'CLOSED'): {raw_rate:.1%}")              # the naive, uncleaned number
    lines.append(f"Clean clearance rate: {rate:.1%}")                                          # the real number, after cleaning
    diff = (rate - raw_rate) * 100                                                             # how many percentage points apart they are
    direction = "higher" if diff >= 0 else "lower"                                             # which way the cleaning moved the rate
    lines.append(f"Difference: clean rate is {abs(diff):.1f} points {direction}")              # the headline comparison

    return "\n".join(lines)                                                                    # the whole report as one string

def main():                                                                                    # run the whole pipeline: raw file in, three files out
    cases, quarantine, stats = load_cases("Midterm/midterm_cases_raw.csv")                     # clean the raw file

    write_clean_csv(cases, "cases_clean.csv")                                                  # save every clean case
    write_quarantine_csv(quarantine, "quarantine.csv")                                         # save every rejected row
    report = build_report(cases, stats)                                                        # build the report text
    print(report)                                                                              # show it on console

    with open("report.txt", "w") as f:                                                         # also save it to a file
        f.write(report)                                                                        # write the report text to disk

if __name__ == "__main__":                                                                     # only run main() when this file is executed directly, not when imported
    main()