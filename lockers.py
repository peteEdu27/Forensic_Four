# lockers.py
# Squad Lab: Operation Evidence Lockers (Week 4)
# Mission: dedupe the raw case file, profile victim ages, and rank beats
# by number of OPEN cases. Uses only lists, sets, and dicts (Week 4 material).

# ============================================================
# STEP 1: Read the raw file into a list, one entry per line
# ============================================================

raw_lines = []                                   # make an empty box called raw_lines - our "locker" that will hold every line from the file, nothing in it yet

with open("wk04_data_raw_cases_dupes.txt") as f: # open the file like opening a book, nickname it "f"; "with" means Python auto-closes the book for us when this block ends
    for line in f:                               # read the book one line at a time; each pass, "line" is the next sentence in the file
        raw_lines.append(line)                   # .append() = drop this line into the end of the raw_lines box

                                                  # (we'll print the line count later, as part of the final report)

# ============================================================
# STEP 2: Normalize every line (strip whitespace, force uppercase)
# ============================================================

normalized = []                                  # another empty box - will hold the CLEANED-UP version of each line

for line in raw_lines:                           # go through every messy line from Step 1, one at a time
    clean = line.strip().upper()                 # two chores in one: .strip() trims extra spaces + the invisible "\n"; .upper() SHOUTS it in caps so "open" and "OPEN" count as the same word later
    normalized.append(clean)                     # drop the cleaned-up line into the normalized box

# ============================================================
# STEP 3: Dedupe using a set
# ============================================================

unique_records = set(normalized)                 # a set is a magic box that refuses to hold two copies of the same thing - dump all 60 lines in, exact duplicates vanish automatically

# ============================================================
# STEP 4: Loop the UNIQUE records; collect ages, count open cases per beat
# ============================================================

ages = []                                        # empty box to collect every victim's age
per_beat = {}                                    # empty DICTIONARY - like a wall of labeled lockers: each locker has a name tag (key) and something stored inside (value); no lockers yet

for rec in unique_records:                       # go through the 52 deduplicated records one at a time (the CLEANED, DEDUPED set, not the original messy list)
    fields = rec.split("|")                      # each record looks like NAME | SEX | AGE | DATE | ADDRESS | BEAT | STATUS; .split("|") chops it into 7 little pieces wherever it sees a "|"

    age = int(fields[2].strip())                 # fields[2] = the 3rd piece (counting starts at 0) = age, but it's text like "34 "; .strip() trims spaces, int() turns text "34" into the real number 34
    ages.append(age)                             # drop that age into our ages box

    beat = fields[5].strip()                     # grab the 6th piece (the beat label, like "352"), trim spaces off it
    status = fields[6].strip()                   # grab the 7th piece ("OPEN" or "CLOSED"), trim spaces

    if status == "OPEN":                         # only bother counting this record if the case is still open - closed cases get skipped for the beat ranking
        if beat in per_beat:                     # ask the dictionary: "do we already have a locker labeled with this beat name?"
            per_beat[beat] += 1                  # yes we do - add 1 to whatever count is already sitting in that locker
        else:                                    # no we don't -
            per_beat[beat] = 1                   # create a brand new locker with this beat's name and put the number 1 in it (first open case we've seen for it)

# ============================================================
# STEP 5: Print the final report
# ============================================================

print("Lines in file:      ", len(raw_lines))                          # total raw lines read from the file (60)
print("Unique records:     ", len(unique_records))                     # distinct records after deduping (52)
print("Duplicates removed: ", len(normalized) - len(unique_records))   # how many duplicate lines were removed (8)

youngest = min(ages)                             # min() looks through the whole ages box and finds the smallest number
oldest = max(ages)                               # max() finds the biggest number in the box
average = round(sum(ages) / len(ages), 1)        # sum() adds up every age, len(ages) is how many ages there are, dividing gives the average; round(...,1) keeps it to 1 decimal (like 39.1)
print(f"Youngest {youngest} / Oldest {oldest} / Average {average}")   # one-line age profile summary

print("Beat ranking, most open cases first, with # bars")  # section title

for beat in sorted(per_beat, key=per_beat.get, reverse=True):  # sorted() would normally sort locker NAMES alphabetically; key=per_beat.get says "sort by what's stored inside each locker (the count)" instead; reverse=True = biggest count first
    count = per_beat[beat]                       # look up how many open cases this beat's locker holds
    bar = "#" * count                            # multiplying text by a number repeats it that many times - if count is 4, bar becomes "####", a mini bar chart made of hashtags
    print(f"{beat:<10}{count:>3}  {bar}")        # f-string "fill in the blank": {beat:<10} = beat name, left-aligned, padded to 10 chars wide; {count:>3} = count, right-aligned, padded to 3 chars; then the # bar
