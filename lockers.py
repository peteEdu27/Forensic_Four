# lockers.py
# Squad Lab: Operation Evidence Lockers (Week 4)
# Mission: dedupe the raw case file, profile victim ages, and rank beats
# by number of OPEN cases. Uses only lists, sets, and dicts (Week 4 material).

# ============================================================
# STEP 1: Read the raw file into a list, one entry per line
# ============================================================

raw_lines = []                                   # create an empty list; this is our "locker" that will hold every raw line from the file

with open("wk04_data_raw_cases_dupes.txt") as f: # open() returns a file object (read mode by default) and "as f" names that object f, our handle for reading the file; "with" auto-closes it when this block ends
    for line in f:                               # f is the file object defined above; looping over it yields one line of text per pass (including its trailing "\n")
        raw_lines.append(line)                   # .append() adds this line to the end of the raw_lines list, growing it by one item

print("Lines in file:     ", len(raw_lines))     # len() counts how many items are in the list; should print 60 to match the file's line count

# ============================================================
# STEP 2: Normalize every line (strip whitespace, force uppercase)
# ============================================================

normalized = []                                  # empty list to hold the cleaned version of every line

for line in raw_lines:                           # walk through each raw line collected in Step 1
    clean = line.strip().upper()                 # .strip() removes leading/trailing whitespace and the "\n"; .upper() forces consistent casing so "open" and "OPEN" match later
    normalized.append(clean)                     # add the cleaned-up line to the normalized list

print("Normalized lines:  ", len(normalized))    # sanity check: should still be 60, since normalizing doesn't remove any lines

# ============================================================
# STEP 3: Dedupe using a set
# ============================================================

unique_records = set(normalized)                 # set() takes the list and drops any values that are exact duplicates, keeping only one copy of each

print("Unique records:    ", len(unique_records))                       # count of distinct records left after deduping; should print 52
print("Duplicates removed:", len(normalized) - len(unique_records))     # total lines minus unique lines = how many duplicates were thrown out; should print 8

# ============================================================
# STEP 4: Loop the UNIQUE records; collect ages, count open cases per beat
# ============================================================

ages = []                                        # empty list locker that will collect every victim's age (from unique records only)
per_beat = {}                                    # empty dict locker: each key is a beat label, each value is that beat's count of OPEN cases

for rec in unique_records:                       # loop over the deduped set, one unique record string at a time
    fields = rec.split("|")                      # split the record string on the "|" character, producing a list of 7 fields: name, sex, age, date, address, beat, status

    age = int(fields[2].strip())                 # fields[2] is the age field as text; .strip() removes stray spaces, int() converts the text into a whole number
    ages.append(age)                             # add this record's age to the running ages list

    beat = fields[5].strip()                     # fields[5] is the beat label (e.g. "BEAT 442"); .strip() removes surrounding spaces
    status = fields[6].strip()                   # fields[6] is the case status (e.g. "OPEN" or "CLOSED"); .strip() removes surrounding spaces

    if status == "OPEN":                         # we only want to count/rank beats based on OPEN cases
        if beat in per_beat:                     # check whether this beat already exists as a key in the dict
            per_beat[beat] += 1                  # it exists -> increment its existing count by 1
        else:                                    # otherwise, this is the first OPEN case we've seen for this beat
            per_beat[beat] = 1                   # create the key and start its count at 1

# ============================================================
# STEP 5: Print the final report
# ============================================================

print()                                          # print an empty line so the report is visually separated from the setup output above
print("=== DEDUPE REPORT ===")                   # section header for the dedupe numbers
print("Lines in file:      ", len(raw_lines))          # total raw lines read from the file (60)
print("Unique records:     ", len(unique_records))     # distinct records after deduping (52)
print("Duplicates removed: ", len(normalized) - len(unique_records))  # how many duplicate lines were removed (8)

print()                                          # blank line before the next section
print("=== VICTIM AGE PROFILE (unique records only) ===")  # section header for age stats
print("Youngest:", min(ages))                    # min() scans the ages list and returns the smallest value
print("Oldest:  ", max(ages))                    # max() scans the ages list and returns the largest value
print("Average: ", round(sum(ages) / len(ages), 1))  # sum() adds every age together, divide by len() (count of ages) for the mean, round() keeps it to 1 decimal place

print()                                          # blank line before the last section
print("=== BEAT RANKING (most open cases first) ===")  # section header for the beat ranking

for beat in sorted(per_beat, key=per_beat.get, reverse=True):  # sorted() on a dict sorts its keys; key=per_beat.get tells it to sort by each key's VALUE (the count) instead of alphabetically; reverse=True puts the highest counts first
    count = per_beat[beat]                       # look up the open-case count for this beat
    bar = "#" * count                            # build a simple text bar chart by repeating "#" count times
    print(f"{beat:<10}{count:>3}  {bar}")        # f-string: left-align beat name in a 10-character field, right-align count in a 3-character field, then print the bar
