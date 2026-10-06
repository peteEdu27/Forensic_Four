# TRAMMELL, MONICA|m|39|2014-06-11|431 KIEST BOULEVARD|beat 352|OPEN

FILENAME = "wk03_data_raw_cases_50.txt"  # name of the pipe-delimited data file to read
CURRENT_YEAR = 2026  # reference year used to calculate how many years a case has been unsolved

total_records = 0        # counts every non-blank line processed
open_count = 0            # counts how many cases have status OPEN
stale_count = 0            # counts OPEN cases that have been unsolved for 5+ years
juvenile_open_count = 0    # counts OPEN cases where the victim/subject is under 18
oldest_open_year = CURRENT_YEAR   # start high, so the first open case seen becomes the oldest
oldest_open_name = ""              # name that goes with oldest_open_year

# print a header row for the report, using format specs to left/right align columns 'Text'; var name print actual value
print(f"{'CASE':<30}{'YEARS UNSOLVED':>15}  FLAG")

case_file = open(FILENAME, "r")  # open the data file for reading

for raw_line in case_file:      # loop over the file one line at a time
    line = raw_line.strip()      # remove leading/trailing whitespace and the newline

    if line == "":                # an empty string means it was a blank line
        continue                   # skip blanks, keep looping

    total_records = total_records + 1   # count each raw line as a real record

    fields = line.split("|")   # split the record into a list of fields on the "|" character

    # pull each field out by its position and clean it up
    # (the raw file is messy, so every field gets its own .strip())
    name = fields[0].strip().title()          # fields[0] is the name; title() fixes capitalization
    gender = fields[1].strip()                  # fields[1] is the gender
    age = int(fields[2].strip())                # fields[2] is the age; int() turns the text into a number
    date = fields[3].strip()                     # fields[3] is the date, e.g. "2014-06-11"
    address = fields[4].strip()                # fields[4] is the street address
    beat = fields[5].strip()                     # fields[5] is the police beat
    status = fields[6].strip().upper()          # fields[6] is OPEN/CLOSED; upper() standardizes it

    year = int(date[0:4])                 # the first 4 characters of the date string are the year
    years_unsolved = CURRENT_YEAR - year   # how many years have passed since that year

    flag = ""  # default flag shown in the report; stays blank unless the case is stale

    if status == "OPEN":  # only cases still open get counted/analyzed further
        open_count = open_count + 1  # tally this as an open case

        if age < 18:  # check if the person is a minor
            juvenile_open_count = juvenile_open_count + 1  # tally it as a juvenile open case

        if years_unsolved >= 5:  # check if the case has been open 5+ years
            stale_count = stale_count + 1  # tally it as stale
            flag = "*** STALE ***"  # mark it in the printed report

        if year < oldest_open_year:   # is this case older than the oldest one seen so far? if so then set the oldest_open_year and the oldest_open_name to this year and name
            oldest_open_year = year
            oldest_open_name = name

    # print one row of the report: name, years unsolved, and flag (if any)
    print(f"{name:<30}{years_unsolved:>15}  {flag}")

case_file.close()  # done reading, close the file

print()  # blank line to separate the per-case table from the summary
print(f"Total records:        {total_records}")
print(f"Open cases:           {open_count}")
print(f"Stale (>= 5 yrs):     {stale_count}")
print(f"Juvenile open cases:  {juvenile_open_count}")
print(f"Oldest open case:     {oldest_open_name} ({oldest_open_year})")
