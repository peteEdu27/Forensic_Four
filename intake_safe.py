# Week 6 Squad Lab - Operation: Bulletproof

import csv                                     # bring in Python's csv tools so commas inside quoted names don't break our split


def parse_row(row):                            # define a function named parse_row that takes one input, row (a list of fields)
    """Validate one CSV row and return it as a clean case dict, or raise ValueError with the reason."""  # docstring: explains what the function does
    if len(row) != 8:                          # a good row has exactly 8 fields; anything else was cut off
        raise ValueError(f"expected 8 fields, got {len(row)}")  # stop here and report how many fields we actually got
    age = int(row[3])                          # turn the age text into a number; 'unknown' raises ValueError on its own
    if row[4].strip() == "":                   # if the date field is empty (or only spaces)
        raise ValueError("missing date")       # stop here and report the missing date
    return {                                   # everything checked out, so build and hand back the clean case dict
        "case_id": row[0].strip(),             # case id with extra spaces removed
        "name": row[1].strip().title(),        # victim name trimmed and title-cased (" carter, d " -> "Carter, D")
        "sex": row[2].strip().upper(),         # sex trimmed and upper-cased ("m" -> "M")
        "age": age,                            # the age number we converted above
        "date": row[4].strip(),                # date with extra spaces removed
        "address": row[5].strip(),             # address with extra spaces removed
        "beat": row[6].strip(),                # beat kept as text so leading zeros survive
        "status": row[7].strip().upper(),      # status trimmed and upper-cased ("open" -> "OPEN")
    }


def load_cases(path):                          # define a function named load_cases that takes one input, the file path
    """Read every row in the CSV; return (good, quarantine) where quarantine holds (line_num, reason, raw_row)."""  # docstring: explains what the function does
    good = []                                  # list for rows that parsed cleanly
    quarantine = []                            # list for rows that failed, with their line number and reason
    with open(path, newline="") as f:          # open the file; 'with' guarantees it closes even if something explodes
        reader = csv.reader(f)                 # csv.reader splits each line into a list of fields for us
        next(reader)                           # eat the header row so the loop only sees data
        for line_num, row in enumerate(reader, start=2):  # go through each row; start=2 because line 1 was the header
            if row == []:                      # a blank line comes back as an empty list; it's not a record, so skip it
                continue                       # move on to the next row
            try:                               # attempt the risky thing
                good.append(parse_row(row))    # parse the row and keep it if it's clean
            except ValueError as err:          # catch ONLY ValueError, so our own bugs still show up
                quarantine.append((line_num, str(err), ",".join(row)))  # log the line number, the reason, and the raw row
    return good, quarantine                    # hand back both lists


def report(good, quarantine):                  # define a function named report that takes the two lists from load_cases
    """Print the loaded/quarantined counts and the full quarantine log."""  # docstring: explains what the function does
    print(f"Rows loaded cleanly:   {len(good)}")        # how many rows made it through (89)
    print(f"Rows quarantined:      {len(quarantine)}")  # how many rows were rejected (11)
    print()                                    # print a blank line to space out the report
    print("QUARANTINE LOG — every rejected row, with the reason:")  # header for the log
    for line_num, reason, raw in quarantine:   # go through each rejected row
        print(f"  line {line_num:>3}: {reason:<55} | {raw[:20]}...")  # line number, reason, and the start of the raw row


if __name__ == "__main__":                     # only run this part when the file is run directly, not when pytest imports it
    good, quarantine = load_cases("wk06_data_raw_cases_100.csv")  # load the file into good rows and quarantined rows
    report(good, quarantine)                   # print the report
