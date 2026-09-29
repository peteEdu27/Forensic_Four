# lockers.py - Week 4: Evidence Lockers
# Goal: dedupe the case file, profile victim ages, rank beats by open cases.
#
# Each line in the data file is one case record that looks like this:
#
#   PALACIOS, GLORIA | M | 25 | 2015-12-21 | 1573 ILLINOIS AVENUE | BEAT 442 | OPEN
#     [0] name      [1]sex [2]age [3]date   [4] address            [5] beat  [6] status
#
# The raw file is messy: random spaces at the ends of lines, mixed upper/lower
# case, blank lines, and some cases entered more than once (duplicates).

# Import the "os" module, which is built into Python (no install needed).
# It gives us tools for working with file and folder paths, which we use
# below to find the data file no matter which folder the script is run from.
import os


# ============================================================
# STEP 2: READ + NORMALIZE
# Clean every line (strip + upper) and collect it into a list.
# ============================================================

# --- Build the full path to the data file ---
# A plain relative path like "data/wk04_data_raw_cases_dupes.txt" is looked up
# starting from whatever folder the TERMINAL is currently in, not the folder
# this script is in. If the terminal is somewhere else, Python can't find the
# file and raises a FileNotFoundError. So we build the path from this script's
# own location instead:
#
#   __file__              -> the path of this script (lockers.py)
#   os.path.abspath(...)  -> turns it into a full path, e.g.
#                            C:\Users\...\WK4ASSNMT\lockers.py
#   os.path.dirname(...)  -> drops the file name and keeps the folder, e.g.
#                            C:\Users\...\WK4ASSNMT
script_folder = os.path.dirname(os.path.abspath(__file__))

# os.path.join() glues the folder, "data", and the file name together using
# the correct separator for the operating system (\ on Windows, / on Mac/Linux).
data_path = os.path.join(script_folder, "data", "wk04_data_raw_cases_dupes.txt")

# Create an empty list BEFORE the loop starts.
# This is the "locker" that will hold every cleaned-up line.
# If it were created inside the loop, it would reset to empty on every pass
# and we'd lose everything we collected.
normalized = []

# Open the file for reading. "with" automatically closes the file when the
# block is finished, even if an error happens partway through.
# "f" is the name we give the open file so we can loop over it.
with open(data_path) as f:

    # Loop over the file one line at a time. Each pass, "line" holds the full
    # text of one line, including the invisible newline (\n) at the end.
    for line in f:

        # Clean the line in two chained steps:
        #   .strip() -> removes spaces, tabs, and the \n from both ends
        #   .upper() -> converts every letter to uppercase
        # This makes "  Reyes, Lamar | m ... open  " and "REYES, LAMAR | M ... OPEN"
        # identical strings, which is what lets the set in Step 3 catch them
        # as duplicates.
        clean = line.strip().upper()

        # An empty string means the line was blank. "continue" skips the rest
        # of this pass and moves on to the next line, so blanks never get added.
        if clean == "":
            continue

        # Add the cleaned line to the end of the list.
        normalized.append(clean)


# ============================================================
# STEP 3: DEDUPE WITH set()
# A set can never hold the same item twice. Converting the list into a set
# automatically throws away every repeated line.
# ============================================================

# set(normalized) builds a new set from the list; duplicates are dropped.
# Note: a set has no order, so the records won't be in file order anymore.
# That's fine here because we only count things, we don't care about order.
unique = set(normalized)

# How many lines were thrown away = (lines before) - (lines after).
# We calculate it once here and print it in the report in Step 5.
duplicates_removed = len(normalized) - len(unique)


# ============================================================
# STEP 4: LOOP THE UNIQUE RECORDS
# Collect every victim age into a list, and count OPEN cases per beat in a dict.
# We loop over "unique" (not "normalized") so a duplicated case is only
# counted once.
# ============================================================

# A list to hold every age, e.g. [25, 33, 39, ...]
ages = []

# A dictionary (dict) that maps each beat to its number of open cases,
# e.g. {"BEAT 442": 3, "BEAT 537": 1, ...}
# The beat name is the "key" and the count is the "value".
open_by_beat = {}

for record in unique:

    # .split("|") cuts the line into pieces wherever there's a "|".
    # Some lines have spaces around the "|" and some don't, so each piece may
    # have extra spaces stuck to it, like " 25 ". The list comprehension
    # [p.strip() for p in ...] runs .strip() on every piece to clean those off.
    # Result: ["PALACIOS, GLORIA", "M", "25", "2015-12-21", ..., "BEAT 442", "OPEN"]
    parts = [p.strip() for p in record.split("|")]

    # Pull out the fields we need by their position (index) in the list.
    # parts[2] is the age, but it's text ("25"), so int() converts it to a
    # number (25). We need a real number to do math like min, max, and average.
    age = int(parts[2])
    beat = parts[5]
    status = parts[6]

    # Every record has an age, so every age goes into the list.
    ages.append(age)

    # Only OPEN cases count toward a beat's workload.
    if status == "OPEN":
        # open_by_beat.get(beat, 0) looks up the beat's current count.
        # If the beat isn't in the dict yet (first time we see it), .get()
        # returns the default 0 instead of crashing with a KeyError.
        # We add 1 and store the new total back under that beat.
        open_by_beat[beat] = open_by_beat.get(beat, 0) + 1


# ============================================================
# STEP 5: PRINT THE REPORT
# Dedupe numbers, then the age profile, then beats ranked
# most-burdened-first with # bars.
# ============================================================

# --- Dedupe numbers ---
print("=== DEDUPE ===")
print("Lines in file:     ", len(normalized))    # expected: 60
print("Unique records:    ", len(unique))
print("Duplicates removed:", duplicates_removed)

# --- Age profile ---
# min() and max() find the smallest and largest numbers in the list.
# The average is the total of all ages divided by how many ages there are.
# round(..., 1) keeps just one digit after the decimal point.
# "\n" at the start of the heading prints a blank line first, for spacing.
print("\n=== AGE PROFILE ===")
print("Victims: ", len(ages))
print("Youngest:", min(ages))
print("Oldest:  ", max(ages))
print("Average: ", round(sum(ages) / len(ages), 1))

# --- Beats ranked by open cases ---
# open_by_beat.items() gives (beat, count) pairs, e.g. ("BEAT 442", 3).
# sorted() puts those pairs in order. The "key" tells it WHAT to sort by:
#   key=lambda pair: (-pair[1], pair[0])
#     -pair[1] -> the count (position 1 in each pair), made negative so the
#                 BIGGEST count comes first (-4 is smaller than -3, and
#                 sorted() goes smallest to largest). This gives us
#                 most-burdened-first.
#     pair[0]  -> the beat name (position 0), used only as a tie-breaker.
#                 When two beats have the same count, they're listed in
#                 alphabetical order. Without this, tied beats would come out
#                 in a random order that changes every run, because the set
#                 from Step 3 has no fixed order.
ranked = sorted(open_by_beat.items(), key=lambda pair: (-pair[1], pair[0]))

print("\n=== OPEN CASES BY BEAT (most burdened first) ===")
for beat, count in ranked:
    # This f-string builds one row of the bar chart:
    #   {beat:<10}   -> the beat name, padded to 10 characters wide and
    #                   left-aligned, so all the bars start in the same column
    #   {'#' * count} -> multiplying a string by a number repeats it,
    #                   so a count of 3 becomes "###"
    #   ({count})    -> the actual number in parentheses after the bar
    print(f"{beat:<10} {'#' * count} ({count})")
