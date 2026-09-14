#Nguyen, Daniel | m | 17 | 2018-04-03 | 2846 QUAIL RIDGE ROAD | beat 537 |Open
record = "Nguyen, Daniel | m | 17 | 2018-04-03 | 2846 QUAIL RIDGE ROAD | beat 537 | Open"
fields = record.strip().split(" | ")
name = fields[0].title()
sex = fields[1].upper()
age = int(fields[2])
date = fields[3]
year = int(date[0:4])
addr = fields[4].title() # "412 Larkmoor Lane"
status = fields[5].upper()
years_unsolved = 2026 - year

CASE = 'CASE'
AGE = 'AGE'
YEARS_UNSOLVED = 'YEARS UNSOLVED'

print(f"{'CASE':<30}{'AGE':>5}{'YEARS_UNSOLVED':>17}")
print(f"{name} ({sex}){'':<13}{age:>3}{years_unsolved:>17}")