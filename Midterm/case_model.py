import re                                 # regex module for pattern matching
from datetime import datetime, date       # datetime for parsing, date for TODAY and comparisons

TODAY = date.today()                      # fixed "current date" used for staleness/future checks

def clean_case_id(raw):
    """Normalize a raw case id to 'CC-#####', or raise if it can't be."""
    raw = raw.strip().upper().replace(" ", "").replace("-", "")            # strip whitespace, upper-case, remove spaces/dashes
    if re.fullmatch(r"CC\d{5}", raw):                                      # must be exactly "CC" + 5 digits
        return "CC-" + raw[2:]                                             # re-insert the dash and return "CC-#####"
    else:
        raise ValueError("bad case_id")                                    # anything else is rejected

def clean_name(raw):
    """Collapse whitespace in a raw victim name and title-case it."""
    return " ".join(raw.split()).title()                                   # collapse whitespace, then title-case it

def clean_sex(raw):
    """Normalize a raw sex string to 'M', 'F', or 'U' for anything else."""
    raw = raw.strip().upper()                                              # strip whitespace, upper-case
    if raw in ["M", "MALE"]:                                               # accept "M" or "MALE"
        return "M"                                                         # normalized male code
    elif raw in ["F", "FEMALE"]:                                           # accept "F" or "FEMALE"
        return "F"                                                         # normalized female code
    else:
        return "U"                                                         # anything else is "unknown"

def clean_age(raw):
    """Return a plausible age (0-110) as an int, or None if out of range/blank."""
    raw = raw.strip()                                                      # strip whitespace
    if raw.isdigit() and int(raw) <= 110:                                  # only accept digits within a plausible age range
        return int(raw)                                                    # return as an int
    else:
        return None                                                        # otherwise age is unknown/blank

def clean_beat(raw):
    """Extract a 3-digit police beat number from a raw string, or None."""
    match = re.search(r"\d{3}", raw)                                       # look for any 3 consecutive digits
    if match:                                                              # if found
        return match.group()                                               # return the matched digits as a string
    else:
        return None                                                        # otherwise beat is unknown

def clean_status(raw):
    """Normalize a raw status to 'OPEN' or 'CLOSED', or raise if unmapped."""
    raw = raw.strip().upper()                                              # strip whitespace, upper-case
    if raw in ["OPEN", "OPN"]:                                             # accept "OPEN" or "OPN"
        return "OPEN"                                                      # normalized open status
    elif raw in ["CLOSED", "CLSD", "CLEARED"]:                             # accept "CLOSED", "CLSD", or "CLEARED"
        return "CLOSED"                                                    # normalized closed status
    else:
        raise ValueError("unknown status")                                 # anything else is rejected

def clean_date(raw):
    """Parse a raw date string (3 accepted formats) into a date object, or raise."""
    raw = raw.strip()                                                      # strip whitespace
    if raw == "" or raw.upper() in ["N/A", "UNKNOWN"]:                     # treat blank/placeholder values as missing
        raise ValueError("missing date")                                   # reject missing dates

    formats = ["%Y-%m-%d", "%m/%d/%Y", "%B %d, %Y"]                        # accepted date formats, tried in order
    for format in formats:                                                 # try each format until one parses
        try:
            result = datetime.strptime(raw, format).date()                 # attempt to parse with this format
        except ValueError:                                                 # this format didn't match
            continue                                                       # move on and try the next format
        if result > TODAY:                                                 # dates in the future are invalid
            raise ValueError("future date")                                # reject future dates
        else:
            return result                                                  # successfully parsed date
    raise ValueError("invalid date")                                       # no format matched at all

def extract_callback_phone(tip_notes):
    """Find the first phone number in free-text tip notes, or '' if none."""
    match = re.search(r"\(?(\d{3})\)?[ .-](\d{3})[.-](\d{4})", tip_notes)  # look for area code + exchange + number
    if match:                                                              # if a phone number pattern was found
        return "-".join(match.groups())                                    # join the three groups with dashes
    else:
        return ""                                                          # otherwise no callback phone found

class Case:                                            # represents one cleaned, validated case record
    def __init__(self, row):                           # build a Case from a raw CSV row
        if len(row) != 9:                              # every valid row must have exactly 9 fields
            raise ValueError("wrong field count")      # reject malformed rows

        self.case_id = clean_case_id(row[0])                          # field 0: case id
        self.victim_name = clean_name(row[1])                         # field 1: victim name
        self.sex = clean_sex(row[2])                                  # field 2: sex
        self.age = clean_age(row[3])                                  # field 3: age
        self.incident_date = clean_date(row[4])                       # field 4: incident date
        self.beat = clean_beat(row[6])                                # field 6: beat (field 5, address, is unused)
        self.status = clean_status(row[7])                            # field 7: case status
        self.callback_phone = extract_callback_phone(row[8])          # field 8: tip notes, mined for a phone number

    @classmethod                  # method belongs to the class, Case
    def from_row(cls, row):       # build a Case from a raw CSV row
        return cls(row)           # return Case(row) and it leads to the __init__ cleaning up fields

    @property
    def year(self):                        # the year the incident occurred
        return self.incident_date.year     # pulled straight from incident_date

    @property
    def decade(self):                      # the decade the incident occurred in
        return (self.year // 10) * 10      # floor the year down to the nearest decade

    @property
    def years_unsolved(self):              # how many years since the incident
        return TODAY.year - self.year      # difference between TODAY's year and incident year

    @property
    def is_stale(self):                                              # whether this case counts as "stale"
        return self.status == "OPEN" and self.years_unsolved >= 5    # open and unsolved for 5+ years