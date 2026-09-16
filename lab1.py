
# BOOKER, TERRENCE | M | 41 | 2018-11-08 | 907 n. calloway drive | Beat 442 | OPEN

Case5 = "BOOKER, TERRENCE | M | 41 | 2018-11-08 | 907 n. calloway drive | Beat 442 | OPEN"

CleanCase5 = Case5.strip().split(" | ")
name = CleanCase5[0].lower().title()
gender = CleanCase5[1]
age = int(CleanCase5[2])  #Convert age to int
date = CleanCase5[3]
year = int(date[0:4])
years_unsolved = 2026 - year
address = CleanCase5[4].title()   #Title address
beat = CleanCase5[5].title()  #Title beat
case_status = CleanCase5[6]

print(f"CASE{'':<19}AGE {'':<13} Years Unsolved")
print(f"{name} ({gender}){age:>5}{years_unsolved:>17}")