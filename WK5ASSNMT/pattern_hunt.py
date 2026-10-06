# pattern_hunt.py - Week 5: Pattern Hunters
# Goal: pull phone numbers, case refs, beats, and dates out of free-text tips
# with regular expressions, then summarize each tip on one line.
#
# Each line in the data file is one tip, written however the caller said it:
#
#   Witness (784-550-8605) reports hearing shots on 4/7/2019 near 591 haskell avenue. ...
#   Email tip: 'I was there on 3/9/2023. ...' Case ref CC-28053. Reply to sender at (706) 706-7309.
#
# There are no columns to split on, so instead of .split() we describe the
# SHAPE of what we want (e.g. "3 digits, dash, 3 digits, dash, 4 digits") and
# let the regex engine find every piece of text with that shape.

# "os" builds the path to the data file (same trick as Week 4).
# "re" is Python's built-in regular expression module.
import os
import re


# ============================================================
# STEP 2: extract_phones()
# Phones show up in two shapes in this file:
#   784-550-8605     -> 3 digits, dash, 3 digits, dash, 4 digits
#   (783) 200-4610   -> (3 digits), space, 3 digits, dash, 4 digits
# ============================================================

# Reading the pattern left to right:
#   (?: ... | ... )  -> a group that matches EITHER the left side OR the right
#                       side. "?:" means "group only, don't capture it", so
#                       findall() returns the whole phone, not just this part.
#   \(\d{3}\)\s?     -> "(", 3 digits, ")", then an optional space.
#                       The parens are escaped with \ because ( and ) mean
#                       "group" in regex; \( means a literal "(" character.
#   \b\d{3}-         -> OR: 3 digits then a dash. \b is a "word boundary",
#                       so we don't start matching in the middle of a longer
#                       number.
#   \d{3}-\d{4}\b    -> both shapes end with 3 digits, dash, 4 digits.
PHONE_RE = re.compile(r"(?:\(\d{3}\)\s?|\b\d{3}-)\d{3}-\d{4}\b")


def extract_phones(text):
    """Return every phone number in text, in either (214) 555-1234 or
    214-555-1234 format. Returns [] if there are none."""
    # findall() returns a list of every match, in the order they appear.
    # If there are none, it returns an empty list [] (not an error).
    return PHONE_RE.findall(text)


# ============================================================
# STEP 3: THE REST OF THE EXTRACTORS
# ============================================================

# Case refs look like CC-14589: the letters "CC", a dash, then 5 digits.
CASE_REF_RE = re.compile(r"\bCC-\d{5}\b")

# Beats look like "beat 341". The ( ) around \d{3} is a CAPTURE GROUP:
# when a pattern has one, findall() returns only the captured part, so we
# get "341" instead of "beat 341". re.IGNORECASE also matches "Beat"/"BEAT".
BEAT_RE = re.compile(r"\bbeat (\d{3})\b", re.IGNORECASE)

# ISO dates look like 2019-02-19: 4-digit year, 2-digit month, 2-digit day.
ISO_DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")

# US dates look like 4/7/2019 or 10/1/2015: month and day can be 1 or 2
# digits ({1,2} means "between 1 and 2 of these"), year is always 4.
US_DATE_RE = re.compile(r"\b\d{1,2}/\d{1,2}/\d{4}\b")

# STRETCH: month-name dates come in two orders in this file:
#   February 15, 2017   -> Month day, year
#   15 December 2020    -> day Month year
# MONTHS is one long "January|February|...|December" alternation, built with
# "|".join() so we don't have to type it out twice.
MONTHS = "|".join([
    "January", "February", "March", "April", "May", "June", "July",
    "August", "September", "October", "November", "December",
])
MONTH_DATE_RE = re.compile(
    rf"\b(?:(?:{MONTHS}) \d{{1,2}}, \d{{4}}|\d{{1,2}} (?:{MONTHS}) \d{{4}})\b"
)
# (In an rf"..." string, {MONTHS} is filled in by Python, so the regex's own
# curly braces have to be doubled: \d{{4}} becomes \d{4}.)


def extract_case_refs(text):
    """Return every case reference in text, e.g. ['CC-14589']."""
    return CASE_REF_RE.findall(text)


def extract_beats(text):
    """Return the beat numbers mentioned in text, e.g. ['341'] for 'beat 341'."""
    return BEAT_RE.findall(text)


def extract_iso_dates(text):
    """Return every YYYY-MM-DD date in text, e.g. ['2019-02-19']."""
    return ISO_DATE_RE.findall(text)


def extract_us_dates(text):
    """Return every M/D/YYYY date in text, e.g. ['4/7/2019', '10/1/2015']."""
    return US_DATE_RE.findall(text)


def extract_month_dates(text):
    """STRETCH: return every month-name date in text, in either
    'February 15, 2017' or '15 December 2020' order."""
    return MONTH_DATE_RE.findall(text)


# ============================================================
# STEP 4: summarize_tip()
# Run every extractor on one tip and format the results as one line.
# ============================================================

def summarize_tip(number, text):
    """Run every extractor on one tip and return a one-line summary."""
    # Small helper: turn a list into "a, b" or "-" if the list is empty,
    # so every column always has something in it.
    def show(items):
        return ", ".join(items) if items else "-"

    phones = extract_phones(text)
    cases = extract_case_refs(text)
    beats = extract_beats(text)
    # A tip can use any of the date styles, so combine all three lists.
    dates = extract_iso_dates(text) + extract_us_dates(text) + extract_month_dates(text)

    # {number:>2} right-aligns the tip number in 2 characters (" 1" .. "24")
    # {...:<16} left-aligns a column in 16 characters so the columns line up.
    return (
        f"Tip {number:>2} | "
        f"phone: {show(phones):<16} | "
        f"case: {show(cases):<8} | "
        f"beat: {show(beats):<3} | "
        f"date: {show(dates)}"
    )


# ============================================================
# STEP 5: READ THE TIPS, PRINT SUMMARIES + CALLBACK COUNT
# ============================================================

script_folder = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_folder, "data", "wk05_data_tipline.txt")

# Read every non-blank line into a list of tips.
tips = []
with open(data_path) as f:
    for line in f:
        clean = line.strip()
        if clean == "":
            continue
        tips.append(clean)

# Step 2 check: run extract_phones() on ONE tip we can verify by eye first.
# Tip 2 says "Witness (784-550-8605) ..." so we expect ['784-550-8605'].
print("=== PHONE CHECK (tip 2) ===")
print(tips[1])
print("->", extract_phones(tips[1]))

# One summary line per tip. enumerate(tips, start=1) hands us both a counter
# (starting at 1, like a human would number them) and the tip text.
print("\n=== TIP SUMMARIES ===")
for number, tip in enumerate(tips, start=1):
    print(summarize_tip(number, tip))

# Callback count: a tip has a callback if it has at least one phone number.
# len(extract_phones(tip)) >= 1 is True/False; sum() counts each True as 1.
with_callback = sum(1 for tip in tips if len(extract_phones(tip)) >= 1)
no_callback = len(tips) - with_callback

print()
print(f"Tips processed:       {len(tips)}")
print(f"Tips with a callback: {with_callback}")
print(f"Tips with NO callback: {no_callback}  <- these leads die without follow-up")
