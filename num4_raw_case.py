# OKAFOR, SAMUEL J | M | 55 | 2018-07-09 | 1519 westhollow avenue | beat 341 | OPEN
# Strip whitespace for all, lowercase and title name, , convert age to int, title address, title beat, 

record = "OKAFOR, SAMUEL J | M | 55 | 2018-07-09 | 1519 westhollow avenue | beat 341 | OPEN"

#Strip whitespace and split record

clean_record = record.strip().split(" | ")

name = clean_record[0].lower().title()
gender = clean_record[1]
age = int(clean_record[2])  #Convert age to int
date = clean_record[3]
year = int(date[0:4])
years_unsolved = 2026 - year
address = clean_record[4].title()   #Title address
beat = clean_record[5].title()  #Title beat
case_status = clean_record[6]

print(f"CASE{'':<19}AGE {'':<13} Years Unsolved")
print(f"{name} ({gender}){age:>5}{years_unsolved:>17}")




