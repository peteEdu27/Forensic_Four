# intake_safe.py - Week 6: Bulletproof Intake
# Goal: load the case CSV without crashing on bad rows. Every row either
# passes validation and is LOADED, or fails and goes into QUARANTINE with its
# line number and the reason it failed.
#
# Each row in the CSV has 8 columns:
#
#   CC-20001,"OKAFOR, TASHA",M,61,2011-10-24,9897 buckner boulevard,623,CLOSED
#   [0]case_id [1]victim_name [2]sex [3]age [4]date [5]address [6]beat [7]status
#
# Bad rows found by eye before writing any code (Step 1):
#   CC-20000  -> date is blank
#   CC-20015  -> age is "unknown"
#   CC-20024  -> only 6 columns (beat and status are missing)
#   + a blank line after CC-20035 (not a case at all, so it is skipped,
#     not quarantined; 89 loaded + 11 quarantined = all 100 cases)
#
# Note: names like "KIRKLAND, MONICA, JR, III" have commas INSIDE them, so
# line.split(",") would cut them into pieces. The csv module understands the
# quotes around the name and keeps it as one column, which is why we use it.

# "csv" reads comma-separated files and handles quoted values for us.
# "datetime" lets us check that a date string is a real calendar date.
import csv
import os
from datetime import datetime

# How many columns a good row must have.
EXPECTED_FIELDS = 8


# ============================================================
# STEP 2: parse_row(row)
# Check one row. If anything is wrong, raise ValueError with a reason.
# If everything is fine, return the row as a dict with real types.
# ============================================================

def parse_row(row):
    """Validate one CSV row and return it as a dict with real types.
    Raises ValueError with a reason if the row is bad."""
    # --- Length check ---
    # A short row (like CC-20024) comes in with only 6 fields, so we
    # can't trust which column is which. Stop here.
    if len(row) != EXPECTED_FIELDS:
        raise ValueError(f"expected {EXPECTED_FIELDS} fields, got {len(row)}")

    # "Unpack" the list into named variables in one line.
    # This only works because we just proved there are exactly 8 items.
    case_id, name, sex, age_text, date_text, address, beat, status = row

    # --- Age check ---
    # int("unknown") raises ValueError on its own, but its message
    # ("invalid literal for int() with base 10") isn't helpful in a report,
    # so we catch it and raise our own, clearer ValueError instead.
    try:
        age = int(age_text)
    except ValueError:
        raise ValueError(f"age is not a number: {age_text!r}")

    # A number can still be impossible for a victim's age.
    if age < 0 or age > 120:
        raise ValueError(f"age out of range: {age}")

    # --- Date check ---
    if date_text.strip() == "":
        raise ValueError("date is missing")

    # strptime() reads a string using a format: %Y = 4-digit year,
    # %m = 2-digit month, %d = 2-digit day. If the string doesn't fit the
    # format, or isn't a real date (like 2019-02-30), it raises ValueError.
    try:
        date = datetime.strptime(date_text, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"date is not YYYY-MM-DD: {date_text!r}")

    # Everything passed: hand back a clean record with proper types.
    return {
        "case_id": case_id,
        "victim_name": name,
        "sex": sex,
        "age": age,
        "date": date,
        "address": address,
        "beat": beat,
        "status": status,
    }


# ============================================================
# STEP 3: load_cases(path)
# Read the whole CSV. Good rows go in one list, bad rows in another.
# One bad row never stops the rest of the file from loading.
# ============================================================

def load_cases(path):
    """Read the CSV at path and return (good, quarantine).
    good is a list of parsed rows; quarantine is a list of
    (line_number, reason, raw_row) for every row that failed."""
    good = []
    quarantine = []

    # newline="" is what the csv module docs ask for when opening a file
    # for csv.reader; it lets the reader handle line endings itself.
    with open(path, newline="") as f:
        reader = csv.reader(f)

        # The first row is the header (case_id,victim_name,...), not a case.
        # next() reads one row and throws it away.
        next(reader)

        for row in reader:
            # csv.reader gives a blank line back as an empty list [].
            # An empty list is "falsy", so "not row" is True for it.
            # A blank line isn't a case, so skip it instead of
            # quarantining it.
            if not row:
                continue

            # This is the "quarantine loop": TRY to parse the row. If
            # parse_row raises ValueError, EXCEPT catches it, and instead of
            # crashing we record the problem and move on to the next row.
            try:
                good.append(parse_row(row))
            except ValueError as err:
                # reader.line_num is the line in the file we just read,
                # counting the header as line 1, so it matches what you see
                # in VS Code's line numbers.
                # str(err) is the reason message we wrote in parse_row.
                quarantine.append((reader.line_num, str(err), row))

    # Return BOTH lists as a tuple; the caller unpacks them:
    #   good, quarantine = load_cases(path)
    return good, quarantine


# ============================================================
# STEP 4: PRINT THE REPORT
# Only runs when this file is run directly (python intake_safe.py), NOT when
# test_intake.py imports it. Otherwise every test run would print the report.
# ============================================================

if __name__ == "__main__":
    script_folder = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_folder, "data", "wk06_data_raw_cases_100.csv")

    good, quarantine = load_cases(data_path)

    print(f"Rows loaded cleanly:   {len(good)}")
    print(f"Rows quarantined:      {len(quarantine)}")

    print("\nQuarantine log:")
    for line_num, reason, row in quarantine:
        # row[0] is the case id. Blank lines were skipped, so every
        # quarantined row has at least one field.
        print(f"  line {line_num:>3} | {row[0]:<8} | {reason}")
