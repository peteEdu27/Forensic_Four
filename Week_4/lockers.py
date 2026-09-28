# wk04_data_raw_cases_dupes.txt — 60 lines, but NOT 60 records. Duplicates with different formatting are hiding in there.
# THE PRODUCT lockers.py — dedupe report, victim age profile (min/max/avg), and the per-beat open-case ranking with # bars

# Raw case file: name|sex|age|date|address|beat|status
data = "wk04_data_raw_cases_dupes.txt"
cases = []  # List to hold the case records as dictionaries
dedupe = ()  # Set to hold the unique case records for deduplication

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
       address = fields[4].strip().title()
       beat = fields[5].strip().upper()
       status = fields[6].strip().upper()
       cases.append(fields) 
       print(cases) # Add the cleaned-up case record to the list
    