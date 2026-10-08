# case_model.py
# Midterm Project: The Cold Case File
# This file holds the TOOLS: one docstringed cleaner function per field (week 5),
# and the Case class whose from_row() classmethod builds a clean Case from one raw row (week 7).
# Cleaners for CRITICAL fields raise ValueError with a reason (week 6) so the loader can quarantine the row.
# Cleaners for NON-critical fields repair what they can and leave the value blank otherwise.

import re                                            # "re" = Python's built-in regular-expression toolbox (week 5); used for case_id, beat, dates and phones
from datetime import date                            # date = the standard-library calendar type; date(2004, 2, 30) raises ValueError because Feb 30 does not exist

# ============================================================
# CONSTANTS - fixed facts the whole project agrees on
# ============================================================

TODAY = date(2026, 10, 7)                            # the cleaning standard says "future date = after today, 10/07/2026", so today is fixed, not read from the computer clock
CURRENT_YEAR = 2026                                  # used by years_unsolved, the same "2026 - year" math from weeks 2, 3 and 7
STALE_YEARS = 5                                      # an OPEN case is stale when it has been unsolved 5+ years; the rule lives in ONE place (week 3 stretch, week 7)
FIELD_COUNT = 9                                      # a healthy raw row has exactly 9 fields (case_id ... tip_notes)

MONTHS = {                                           # a dict (week 4): month NAME -> month NUMBER, so "July 1, 2022" can become month 7
    "January": 1, "February": 2, "March": 3,         # each pair is key: value
    "April": 4, "May": 5, "June": 6,                 # keys are the spellings that appear in the raw file
    "July": 7, "August": 8, "September": 9,          # a name that is NOT a key (the file has "Smarch") means an invalid date
    "October": 10, "November": 11, "December": 12,   # the last three months
}                                                    # end of the dict


# ============================================================
# CRITICAL-FIELD CLEANERS - these RAISE ValueError so the row gets quarantined
# ============================================================

def clean_case_id(text):                             # text = the raw case_id field, e.g. " CC-76856 ", "cc-19495", "CC 16288", "CC81472"
    """Normalize a case id to CC- plus 5 digits, or raise ValueError('bad case_id')."""   # docstring: one line saying what this tool does
    text = text.strip().upper()                      # .strip() removes outside spaces, .upper() turns "cc" into "CC" (week 2 string surgery)
    found = re.findall(r"^CC[- ]?(\d{5})$", text)    # regex: ^ = start of text, "CC", [- ]? = an optional dash or space, (\d{5}) = capture exactly 5 digits, $ = end of text
    if len(found) == 0:                              # an empty list means the shape did not match ("XX-46752", "CASE?", "CC-791", "CC-636017", "")
        raise ValueError("bad case_id")              # raise = deliberately throw an error; the message becomes the quarantine reason
    return f"CC-{found[0]}"                          # found[0] is the 5 captured digits; the f-string rebuilds the id in the standard form "CC-12345"


def parse_date(text):                                # text = the raw incident_date field
    """Turn one of the 3 allowed date formats into a date, or raise ValueError with the reason."""   # docstring
    text = text.strip()                              # remove stray spaces; a field of only spaces becomes "" here
    if text.upper() in ["", "N/A", "UNKNOWN"]:       # .upper() makes "unknown" and "UNKNOWN" the same; "in" checks membership in the list (week 3)
        raise ValueError("missing date")             # blank, N/A or unknown = missing date, per the cleaning standard

    iso = re.findall(r"^(\d{4})-(\d{2})-(\d{2})$", text)          # format 1, YYYY-MM-DD like 2018-03-22; three () groups capture year, month, day
    us = re.findall(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", text)       # format 2, M/D/YYYY like 6/7/2000 or 06/24/2014; \d{1,2} = one or two digits
    named = re.findall(r"^([A-Za-z]+) (\d{1,2}), (\d{4})$", text) # format 3, "July 1, 2022"; [A-Za-z]+ = one or more letters (the month name)

    if len(iso) > 0:                                 # did the ISO pattern match? (findall hands back a list; with groups, each match is a tuple)
        year_text, month_text, day_text = iso[0]     # iso[0] is a tuple like ("2018", "03", "22"); unpack it into three named variables
    elif len(us) > 0:                                # otherwise, did the US pattern match? (elif is only asked if the "if" above was False)
        month_text, day_text, year_text = us[0]      # US order is month / day / year, so unpack in that order
    elif len(named) > 0:                             # otherwise, did the month-name pattern match?
        month_name, day_text, year_text = named[0]   # unpack ("July", "1", "2022")
        if month_name not in MONTHS:                 # "Smarch" is not a key in the MONTHS dict
            raise ValueError("invalid date")         # an unknown month name is not one of the 3 formats
        month_text = str(MONTHS[month_name])         # look the name up in the dict (7), then str() so every branch ends with text for int() below
    else:                                            # none of the three patterns matched (e.g. "13/45/199x")
        raise ValueError("invalid date")             # not one of the 3 formats = invalid date

    try:                                             # TRY the risky thing (week 6)...
        incident = date(int(year_text), int(month_text), int(day_text))   # int() converts the text to numbers; date() refuses impossible dates such as Feb 30 or month 13
    except ValueError:                               # ...date() raises ValueError for an impossible date; catch exactly that error
        raise ValueError("invalid date")             # re-raise with OUR reason so the quarantine log says "invalid date", not Python's wording

    if incident > TODAY:                             # dates compare like numbers: later dates are "greater"
        raise ValueError("future date")              # an incident after 10/07/2026 cannot have happened yet
    return incident                                  # hand back a real date object; the caller turns it into YYYY-MM-DD text


def clean_status(text):                              # text = the raw status field, e.g. "OPEN", " OPEN ", "opn", "Closed", "CLSD", "CLEARED"
    """Map a status to OPEN or CLOSED, or raise ValueError('unknown status')."""   # docstring
    text = text.strip().upper()                      # " Open " -> "OPEN"; standardize before comparing, because "open" == "OPEN" is False (week 3)
    if text in ["OPEN", "OPN"]:                      # the two spellings the standard maps to OPEN
        return "OPEN"                                # hand back the standard value
    elif text in ["CLOSED", "CLSD", "CLEARED"]:      # the three spellings the standard maps to CLOSED
        return "CLOSED"                              # hand back the standard value
    raise ValueError("unknown status")               # anything else ("PENDING?", "??", "UNK", blank) cannot be mapped, so quarantine the row


# ============================================================
# NON-CRITICAL CLEANERS - these REPAIR the value and never raise
# ============================================================

def clean_name(text):                                # text = the raw victim_name, e.g. "  JORDAN, C " or "GARNER,  K"
    """Strip, collapse repeated spaces, and Title Case a victim name."""   # docstring
    words = text.split()                             # .split() with no argument splits on ANY run of spaces and drops the outside ones: "GARNER,  K" -> ["GARNER,", "K"]
    return " ".join(words).title()                   # " ".join glues the pieces back with exactly ONE space between them; .title() -> "Garner, K"


def clean_sex(text):                                 # text = the raw sex field, e.g. "M", " M", "m", "Male", "MALE", "female", "F ", "unk", ""
    """Map sex to M or F; anything else becomes U."""   # docstring
    text = text.strip().upper()                      # " m" -> "M", "female" -> "FEMALE"
    if text in ["M", "MALE"]:                        # both spellings mean male
        return "M"                                   # standard value
    elif text in ["F", "FEMALE"]:                    # both spellings mean female
        return "F"                                   # standard value
    return "U"                                       # "U", "UNK", blank, anything else -> U for unknown


def clean_age(text):                                 # text = the raw age field, e.g. "36", " 37 ", "unknown", "N/A", "?", "999", "-1"
    """Return the age as a whole number 0-110, or None (written as blank) when it is not usable."""   # docstring
    try:                                             # int() is risky on dirty text (week 6)
        age = int(text)                              # int() ignores outside spaces (" 37 " -> 37) but raises ValueError on "unknown", "N/A", "?"
    except ValueError:                               # catch ONLY ValueError, never a bare except
        return None                                  # not a whole number -> leave the age blank; the row is still kept
    if age < 0 or age > 110:                         # "or" combines two conditions (week 3); -1 and 999 are impossible ages
        return None                                  # out of range -> leave blank
    return age                                       # a usable whole-number age


def clean_beat(text):                                # text = the raw beat field, e.g. "157", " 157 ", "beat 631", "Beat 418", "B-150", ""
    """Pull the 3-digit beat number out of the field, or return '' (blank)."""   # docstring
    found = re.findall(r"\d{3}", text)               # \d{3} = exactly three digits in a row, wherever they sit in the text
    if len(found) == 0:                              # no three digits anywhere (blank field)
        return ""                                    # leave the beat blank; the row is still kept
    return found[0]                                  # the first 3-digit group, e.g. "631"


def clean_phone(text):                               # text = the raw tip_notes, e.g. "cb: (214) 555-4240" or "Caller left callback 214.555.3072"
    """Return the first phone number in the tip notes as 214-555-1234, or '' if there is none."""   # docstring
    phones = re.findall(r"\(?\d{3}\)?[ .-]\d{3}[.-]\d{4}", text)   # the week 5 phone pattern, widened to also accept dots: (214) 555-4240, 214-555-1234, 214.555.3072
    if len(phones) == 0:                             # no phone shape in the notes
        return ""                                    # callback_phone stays blank
    first = phones[0]                                # the standard says use the FIRST phone number
    first = first.replace("(", "").replace(")", "")  # .replace(a, b) swaps text (week 2): drop the parentheses -> "214 555-4240"
    first = first.replace(" ", "-").replace(".", "-")   # spaces and dots become dashes -> "214-555-4240"
    return first                                     # always in the 214-555-1234 shape


# ============================================================
# THE CASE CLASS - data with behavior (week 7)
# ============================================================

class Case:                                          # a class is a blueprint; each Case object is one cleaned homicide record
    """One cleaned case record, plus the questions we ask of it."""   # docstring for the class

    def __init__(self, case_id, victim_name, sex, age, incident_date, year, beat, status, callback_phone):   # __init__ runs at creation, like the booking process
        self.case_id = case_id                       # self = "this particular case"; store the cleaned id on it
        self.victim_name = victim_name               # cleaned "Last, I" name
        self.sex = sex                               # M, F or U
        self.age = age                               # a whole number 0-110, or None for blank
        self.incident_date = incident_date           # text in YYYY-MM-DD form
        self.year = year                             # the 4-digit year as an int, so we can do math on it
        self.beat = beat                             # 3-digit beat text, or "" for blank
        self.status = status                         # OPEN or CLOSED
        self.callback_phone = callback_phone         # 214-555-1234 form, or "" for none

    @classmethod                                     # a classmethod receives the CLASS (cls) instead of one object, so it can build new objects
    def from_row(cls, row):                          # row = the list of 9 raw text fields from csv.reader
        """Build a clean Case from one raw CSV row, or raise ValueError with the quarantine reason."""   # docstring
        if len(row) != FIELD_COUNT:                  # rule 1: the row must have exactly 9 fields (truncated rows have 5-7)
            raise ValueError("wrong field count")    # quarantine reason
        case_id = clean_case_id(row[0])              # rule 2: may raise "bad case_id"
        incident = parse_date(row[4])                # rules 3-5: may raise "missing date", "invalid date" or "future date"
        status = clean_status(row[7])                # rule 6: may raise "unknown status"
        return cls(case_id,                          # every critical check passed, so build the Case; cls(...) is the same as Case(...)
                   clean_name(row[1]),               # victim_name: repaired, never rejected
                   clean_sex(row[2]),                # sex: repaired to M/F/U
                   clean_age(row[3]),                # age: whole number or None
                   str(incident),                    # str() of a date gives "YYYY-MM-DD", exactly the required format
                   incident.year,                    # .year pulls the year number out of the date, e.g. 2018
                   clean_beat(row[6]),               # beat: 3 digits or ""
                   status,                           # already cleaned above
                   clean_phone(row[8]))              # callback_phone from the tip_notes; row[5] (address) is skipped on purpose: the standard says drop it

    @property                                        # @property lets us write c.years_unsolved with no () - it reads like a fact
    def years_unsolved(self):                        # how long since the incident
        """Years between the incident year and 2026."""   # docstring
        return CURRENT_YEAR - self.year              # same math as week 2: 2026 - 2018 = 8

    @property                                        # another property
    def is_stale(self):                              # the 5-year rule, living in ONE place
        """True when the case is OPEN and has been unsolved 5+ years."""   # docstring
        return self.status == "OPEN" and self.years_unsolved >= STALE_YEARS   # both conditions must be True (week 3 "and")

    def summary(self):                               # a normal method: c.summary() returns one readable line about the case
        """One readable line about this case for the report."""   # docstring
        beat = self.beat                             # start with the stored beat
        if beat == "":                               # a blank beat would leave a gap in the report line
            beat = "---"                             # show --- instead, so the reader knows it is unknown
        return f"{self.case_id}  {self.victim_name:<14}{self.incident_date}  beat {beat}  {self.years_unsolved} yrs unsolved"   # :<14 pads the name to 14 characters so the columns line up (week 2)

    def to_row(self):                                # turns the Case back into a list of fields for csv.writer
        """Return the Case as a list in the exact cases_clean.csv column order."""   # docstring
        age = self.age                               # start with the stored age
        if age is None:                              # None means the age was not usable
            age = ""                                 # write it as a blank field, as the required format shows ("F,,2019-11-02")
        return [self.case_id, self.victim_name, self.sex, age, self.incident_date,   # columns 1-5
                self.year, self.beat, self.status, self.callback_phone]              # columns 6-9
