# Week 3 Squad Lab - Operation: First Filter

# Accumulators: set up BEFORE the loop
total_count = 0
open_count = 0
stale_count = 0
juvenile_count = 0
oldest_year = 2026        # start high
oldest_name = ""

# Read every line of the data file into a list
file = open("wk03_data_raw_cases_50.txt")
records = file.readlines()
file.close()

for line in records:
    line = line.strip()
    if line == "":
        continue        # skip blanks, keep looping

    # Parse fields: split on the bare pipe, strip every field
    fields = line.split("|")
    name = fields[0].strip().title()
    age = int(fields[2].strip())
    year = int(fields[3].strip()[0:4])
    status = fields[6].strip().upper()
    years_unsolved = 2026 - year

    # Accumulators: update INSIDE the loop
    total_count = total_count + 1

    if status == "OPEN":
        open_count = open_count + 1

    flag = ""
    if status == "OPEN" and years_unsolved >= 5:
        flag = "*** STALE ***"
        stale_count = stale_count + 1

    if status == "OPEN" and age < 18:
        juvenile_count = juvenile_count + 1

    if status == "OPEN" and year < oldest_year:
        oldest_year = year
        oldest_name = name

    print(f"{name}: {years_unsolved} years {flag}")

# Report AFTER the loop
print()
print(f"Total records:        {total_count}")
print(f"Open cases:           {open_count}")
print(f"Stale (>= 5 yrs):     {stale_count}")
print(f"Juveniles (open):     {juvenile_count}")
print(f"Oldest open case:     {oldest_name} ({oldest_year})")