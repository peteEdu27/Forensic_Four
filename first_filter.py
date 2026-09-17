total_records = 0
open_count = 0
stale_count = 0
juvenile_count = 0
oldest_year = 2026   # start high, get replaced once we see an older open case
oldest_name = ""

for line in open("wk03_data_raw_cases_50.txt"):
    line = line.strip()

    if line == "":
        continue        # skip blanks, keep looping

    fields = line.split("|")

    name = fields[0].strip().lower().title()
    age = int(fields[2].strip())
    year = int(fields[3].strip()[0:4])
    status = fields[6].strip().upper()

    years_unsolved = 2026 - year
    total_records = total_records + 1

    flag = ""

    if status == "OPEN":
        open_count = open_count + 1

        if years_unsolved >= 5:
            stale_count = stale_count + 1
            flag = "*** STALE ***"

        if age < 18:
            juvenile_count = juvenile_count + 1

        if year < oldest_year:
            oldest_year = year
            oldest_name = name

    print(f"{name}: {years_unsolved} years {flag}")

print()
print(f"Total records: {total_records}")
print(f"Open cases: {open_count}")
print(f"Stale (>= 5 yrs): {stale_count}")
print(f"Oldest open case: {oldest_name} ({oldest_year})")
print(f"Juvenile open cases: {juvenile_count}")
