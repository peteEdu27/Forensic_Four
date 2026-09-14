#Nguyen, Daniel | m | 17 | 2018-04-03 | 2846 QUAIL RIDGE ROAD | beat 537 |Open
record3 = "Nguyen, Daniel | m | 17 | 2018-04-03 | 2846 QUAIL RIDGE ROAD | beat 537 | Open"
fields3 = record3.strip().split(" | ")
name3 = fields3[0].title()
sex3 = fields3[1].upper()
age3 = int(fields3[2])
date3 = fields3[3]
year3 = int(date3[0:4])
addr3 = fields3[4].title()
status3 = fields3[5].upper()
years_unsolved3 = 2026 - year3
CASE3 = 'CASE'
AGE3 = 'AGE'
YEARS_UNSOLVED3 = 'YEARS_UNSOLVED'
print(f"{CASE3:<30}{AGE3:>5}{YEARS_UNSOLVED3:>17}")
print(f"{name3} ({sex3}){'':<13}{age3:>3}{years_unsolved3:>17}")
print()