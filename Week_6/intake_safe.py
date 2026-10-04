import csv
data = "Week_6/wk06_data_raw_cases_100.csv"  # path to the raw case data file

with open(data, "r") as f:
    reader = csv.reader(f) #reads the csv file
    next(reader) #skips header

    def parse_row(row):
        # every valid row must have exactly 8 comma-separated fields
        if len(row) != 8:
            raise ValueError(f"Expected 8 fields in Row, got: {len(row)}")

        # unpack the row into named variables, in column order
        case_id,victim_name,sex,age,date,address,beat,status = row

        # date is required; reject the row if it's blank
        if date.strip() == "":
            raise ValueError("Missing Date")

        # clean up whitespace and fix casing before returning a structured record
        return {
            "case_id": case_id.strip(),
            "name": victim_name.strip().title(),
            "sex": sex.strip(),
            "age": int(age),  # convert age from string to integer
            "date": date.strip(),
            "address": address.strip(),
            "beat": beat.strip(),
            "status": status.strip()
        }

    def load_cases():
        good = []        # successfully parsed rows
        quarantine = []   # rows that failed validation, kept for review instead of crashing

        # start=2 because line 1 is the header that was already skipped
        for line_num, row in enumerate(reader, start=2):
            if not row:
                continue  # skip blank lines
            try:
                good.append(parse_row(row))
            except ValueError as error:
                # capture bad rows instead of stopping the whole import
                quarantine.append((line_num, str(error), row))
        return good, quarantine

    good, quarantine = load_cases()
    print(f"Rows loaded cleanly: {len(good)}")
    print(f"Rows quarantined: {len(quarantine)}")
    print("Quarantine log:")
    # report exactly which rows failed, why, and their original line number
    for line_num, reason, row in quarantine:
        print(f"  line {line_num:3}: {reason:50} | {','.join(row)}")