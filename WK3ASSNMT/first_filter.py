# Week 3 - Operation: First Filter

# Read the data file
with open("data/wk03_data_raw_cases_50.txt", "r") as file:
    records = file.readlines()


# Set up accumulators
juvenile_count = 0
total = 0
open_count = 0
stale_count = 0

oldest_year = 2026
oldest_name = ""


# Process every record
for line in records:
    line = line.strip()

    # Skip blank lines
    if line == "":
        continue

    fields = line.split("|")

    # Skip incomplete/odd lines
    if len(fields) < 7:
        continue

    # Clean and convert fields
    name = fields[0].strip().title()
    age = int(fields[2].strip())

    date = fields[3].strip()
    year = int(date[0:4])

    status = fields[6].strip().upper()

    years_unsolved = 2026 - year

    # Count valid records
    total = total + 1

    # Count open cases
    if status == "OPEN":
        open_count = open_count + 1

        # Find oldest open case
        if year < oldest_year:
            oldest_year = year
            oldest_name = name

    # Flag and count stale open cases
    if status == "OPEN" and years_unsolved >= 5:
        stale_count = stale_count + 1
        print(f"{name}: {years_unsolved} years unsolved *** STALE ***")

    # Count juvenile open cases
    if status == "OPEN" and age < 18:
        juvenile_count = juvenile_count + 1


# Final report
print()
print(f"Total records:        {total}")
print(f"Open cases:           {open_count}")
print(f"Stale (>= 5 yrs):     {stale_count}")
print(f"Oldest open case:     {oldest_name} ({oldest_year})")
print(f"Juvenile open cases:  {juvenile_count}")