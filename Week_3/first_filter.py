# Raw case file: name|sex|age|date|address|beat|status
data = "wk03_data_raw_cases_50.txt"

# Running totals we build up as we scan through every case in the file
total = 0            # every case, open or closed
open_count = 0        # cases currently marked OPEN
stale_count = 0        # OPEN cases that have sat unsolved for 5+ years
juvenile_count = 0    # OPEN cases where the victim/suspect is under 18
oldest_age = 0

# Set up so the first open case always beats it when hunting for the actual oldest year
oldest_year = 2026
oldest_name = ""

with open(data, "r") as file:
   # Read the file one line (one case record) at a time
   for line in file:
    #Organizing the data into fields and cleaning it up
       # Split the pipe-delimited line into its 7 raw fields
       fields = line.strip().split("|")
       # .title() capitalizes each word, e.g. "john smith" -> "John Smith"
       name = fields[0].strip().title()
       # .upper() normalizes case so comparisons like "OPEN" always match
       sex = fields[1].strip().upper()
       age = int(fields[2].strip())
       # Date field looks like "2019-03-01...", so [0:4] grabs just the year
       year = int(fields[3].strip()[0:4])
       # How many years have passed between the case year and now (2026)
       years_unsolved = 2026 - year
       address = fields[4].strip().title()
       beat = fields[5].strip().upper()
       status = fields[6].strip().upper()

       # Count this line toward the overall case total
       total+=1
       if "OPEN" in status:
           open_count +=1
       # Stale = open and unsolved for 5+ years
       if "OPEN" in status and years_unsolved >= 5:
           stale_count +=1
           # Print a formatted row for every stale case as we find it
           # Pad each field so the printed columns line up
           print(f"***STALE***:  {name.ljust(20)} {sex.ljust(4)} {age:<4d} {address.ljust(25)} Years_Unsolved:{years_unsolved:<5d} {beat.ljust(10)} {status.ljust(10)}")
       if "OPEN" in status and age<18:
           juvenile_count +=1
       # Track the open case with the earliest year seen so far
       if year < oldest_year and "OPEN" in status:
           oldest_year = year
           oldest_name = name

   # Summary stats printed once, after every line has been processed
   print(f"\nTotal Cases: {total}")
   print(f"Open Cases: {open_count}")
   print(f"Stale Cases (open for 5+ years): {stale_count}")
   print(f"Juvenile Open Cases: {juvenile_count}")
   print(f"Oldest Open Case: {oldest_name} ({oldest_year})")