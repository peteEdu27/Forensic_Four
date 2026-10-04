# Raw case file: name|sex|age|date|address|beat|status
data = "Week_4/wk04_data_raw_cases_dupes.txt"
total_cases = list()  # List to hold the case records as dictionaries
dedupe = set()  # Set to hold the unique case records for deduplication

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
       address = fields[4].strip().title()
       # Strip the "BEAT " prefix so the number alone can be a dict key, e.g. "442"
       beat = fields[5].strip().upper().replace("BEAT ", "")
       status = fields[6].strip().upper()

       # Keep every record as-read, including duplicates
       total_cases.append([name, sex, age, year, address, beat, status])
       # A tuple is hashable, so adding the same record twice collapses to one entry in the set
       dedupe.add((name, sex, age, year, address, beat, status))

   # Comparing the raw count to the deduped count shows how many exact-duplicate lines were in the file
   print(f"\nTotal Cases Before Deduplication: {len(total_cases)}")
   print(f"Total Cases After Deduplication: {len(dedupe)}")
   print(f"Duplicates Removed: {len(total_cases) - len(dedupe)}")

   # Collect the age (index 2) from every deduped case into a list
   # Must be a list, not a set, so two people who share the same age both count toward the average
   age = list()
   for case in dedupe:
      age.append(case[2])
   print(f"\nYoungest Age: {min(age)}, Oldest Age: {max(age)}, Average Age: {sum(age)/len(age):.1f}")

   # Tally how many OPEN cases fall in each beat
   beat_dict = dict()
   for case in dedupe:
       beat = case[5]
       status = case[6]
       # Only OPEN cases count toward the beat totals; closed cases are ignored here
       if status == "OPEN":
         if beat not in beat_dict:
            beat_dict[beat] = 1
         else:
            beat_dict[beat] += 1
   print("\nOpen Cases by Beat (sorted by count):")
   # Sort beats by their open-case count, highest first, and print a bar chart alongside each count
   for key in sorted(beat_dict, key=beat_dict.get, reverse=True):
      value = beat_dict[key]
      bar = "#" * value
      print(f"Beat {key:<6} {value} {bar}")