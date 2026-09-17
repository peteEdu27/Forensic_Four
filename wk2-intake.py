# Raw record for reference: name | sex | age | date | address | beat | status
#Nguyen, Daniel | m | 17 | 2018-04-03 | 2846 QUAIL RIDGE ROAD | beat 537 |Open

# Pipe-delimited case record to parse
record3 = "Nguyen, Daniel | m | 17 | 2018-04-03 | 2846 QUAIL RIDGE ROAD | beat 537 | Open"

# Split the record into its individual fields
fields3 = record3.strip().split(" | ")

# Extract and format each field
name3 = fields3[0].title()
sex3 = fields3[1].upper()
age3 = int(fields3[2])
date3 = fields3[3]
year3 = int(date3[0:4])  # Pull the 4-digit year from the date string
addr3 = fields3[4].title()
status3 = fields3[5].upper()

# Number of years the case has been unsolved, relative to 2026
years_unsolved3 = 2026 - year3

# Column headers for the printed table
CASE3 = 'CASE'
AGE3 = 'AGE'
YEARS_UNSOLVED3 = 'YEARS_UNSOLVED'

# Print header row, then the formatted case details
print(f"{CASE3:<30}{AGE3:>5}{YEARS_UNSOLVED3:>17}")
print(f"{name3} ({sex3}){'':<13}{age3:>3}{years_unsolved3:>17}")
print()