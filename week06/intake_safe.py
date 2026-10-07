# intake_safe.py
# Squad Lab: Operation Bulletproof (Week 6)
# Mission: load 100 CSV rows that contain damage. Zero crashes. Full quarantine log.
# Uses only: open(), the csv module, try/except (ValueError), and the quarantine pattern.

import csv                                           # csv is Python's built-in module for reading comma-separated files


# ============================================================
# STEP 1: parse_row() - validate ONE row, or raise ValueError with a reason
# ============================================================

def parse_row(row):                                  # "row" is a LIST of 8 text fields that csv.reader already split for us
    """Validate one CSV row and return it as a clean dict, or raise ValueError saying why it is bad."""   # docstring
    if len(row) != 8:                                # a healthy row has exactly 8 fields; len() counts the items in the list
        raise ValueError(f"expected 8 fields, got {len(row)}")   # raise = deliberately throw an error; the message becomes the "reason" in the quarantine log

    age = int(row[3])                                # row[3] is the age text; int() turns "36" into 36 - but if it says "unknown", int() raises ValueError on its own

    if row[4].strip() == "":                         # row[4] is the date; .strip() removes spaces, and "" (empty text) means the date is missing
        raise ValueError("missing date")             # throw our own ValueError so this row gets quarantined with this reason

    return {                                         # everything passed, so hand back the clean record as a dictionary (label -> value)
        "case_id": row[0].strip(),                   # field 0 = case number, trimmed of spaces
        "name": row[1].strip().title(),              # field 1 = victim name; .title() capitalizes each word ("carter, d" -> "Carter, D")
        "sex": row[2].strip().upper(),               # field 2 = sex, forced to capital letters
        "age": age,                                  # the age we already converted into a real number
        "date": row[4].strip(),                      # field 4 = date text, trimmed
        "address": row[5].strip(),                   # field 5 = street address, trimmed
        "beat": row[6].strip(),                      # field 6 = beat number, trimmed
        "status": row[7].strip().upper(),            # field 7 = OPEN/CLOSED, forced to capital letters
    }


# ============================================================
# STEP 2: load_cases() - csv.reader + the try/except quarantine loop
# ============================================================

def load_cases(path):                                # "path" is the file name to open
    """Load every row we can; quarantine the rest. Returns (good, quarantine)."""   # docstring
    good = []                                        # empty list for rows that passed validation
    quarantine = []                                  # empty list for rejected rows; each entry will be (line number, reason, raw row)

    with open(path, newline="") as f:                # open the file; newline="" is what the csv module wants so it handles line endings itself; "with" auto-closes the file
        reader = csv.reader(f)                       # csv.reader splits each line into a LIST of fields, even when a comma sits inside quotes ("KIRKLAND, MONICA")
        header = next(reader)                        # next() pulls the FIRST row (the column titles) so the loop below only sees data rows

        for line_num, row in enumerate(reader, start=2):   # enumerate hands us a counter AND the row; start=2 because line 1 was the header, so the first data row is line 2
            if row == []:                            # a completely blank line comes through as an empty list
                continue                             # continue = skip this pass of the loop; a blank line is not a record, so it is not counted as good OR bad

            try:                                     # TRY the risky thing...
                good.append(parse_row(row))          # ...validate the row; if it passes, add the clean dict to the good list
            except ValueError as err:                # ...but if parse_row raised a ValueError, catch it HERE (only ValueError, never a bare except) and call it "err"
                quarantine.append((line_num, str(err), ",".join(row)))   # log line number, the reason (str(err) = the error message as text), and the row glued back together with commas
                                                     # after the except, the loop simply keeps going - one bad row never kills the other rows

    return good, quarantine                          # hand BOTH lists back to whoever called the function


# ============================================================
# STEP 3: report() - print the counts and the full quarantine log
# ============================================================

def report(good, quarantine):                        # takes the two lists that load_cases() returned
    """Print how many rows loaded, how many were quarantined, and why each one was rejected."""   # docstring
    print("Rows loaded cleanly:  ", len(good))       # len(good) = number of rows that passed
    print("Rows quarantined:     ", len(quarantine)) # len(quarantine) = number of rows that failed
    print()                                          # blank line for readability
    print("QUARANTINE LOG - every rejected row, with the reason:")   # section title

    for line_num, reason, raw in quarantine:         # each quarantine entry is a 3-item tuple; this unpacks it into three named variables
        print(f"  line {line_num}: {reason} | {raw[:25]}...")   # {line_num} = the file line number; {reason} = why the row was rejected; raw[:25] = only the first 25 characters of the row


# ============================================================
# STEP 4: Run it. The "if __name__" guard means this block runs when you
# type "python intake_safe.py" but NOT when pytest imports parse_row from this file.
# ============================================================

if __name__ == "__main__":                           # True only when this file is run directly, not when it is imported by another file
    good, quarantine = load_cases("wk06_data_raw_cases_100.csv")   # load the file; the function returns two lists and we unpack them into two variables
    report(good, quarantine)                         # print the final report
