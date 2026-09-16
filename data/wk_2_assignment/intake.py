# Case Intake - Records 1 and 2

record1 = "  CARTER, DEMARCUS | m | 36 | 2018-03-22 | 412 larkmoor lane | beat 352 | OPEN  "
record2 = "reyes, miguel|M|32|2018-05-17| 3308 DELAFORD STREET |Beat 347|open"

# Clean Record 1
fields1 = record1.strip().split("|")

name1 = fields1[0].strip().title()
sex1 = fields1[1].strip().upper()
age1 = int(fields1[2].strip())
date1 = fields1[3].strip()
year1 = int(date1[0:4])
address1 = fields1[4].strip().title()
status1 = fields1[6].strip().upper()

years_unsolved1 = 2026 - year1

# Clean Record 2
# Split on "|" because Record 2 does not have spaces around every pipe.
fields2 = record2.strip().split("|")

name2 = fields2[0].strip().title()
sex2 = fields2[1].strip().upper()
age2 = int(fields2[2].strip())
date2 = fields2[3].strip()
year2 = int(date2[0:4])
address2 = fields2[4].strip().title()
status2 = fields2[6].strip().upper()

years_unsolved2 = 2026 - year2

# Report
print(f"{'CASE':<30}{'AGE':<8}{'YEARS UNSOLVED'}")
print(f"{name1 + ' (' + sex1 + ')':<30}{age1:<8}{years_unsolved1}")
print(f"{name2 + ' (' + sex2 + ')':<30}{age2:<8}{years_unsolved2}")