# src/models.py - Week 7: Case Objects (moved into src/ in Week 8)
# The Case class: wraps one raw 9-field case row, cleans every field through
# its own validator, and exposes derived properties (year, decade,
# years_unsolved, is_stale) used by later weeks' reports.
#
# Row shape (9 columns):
#   [0]case_id [1]victim_name [2]sex [3]age [4]incident_date
#   [5]address (unused) [6]beat [7]status [8]tip_notes

import re
from datetime import datetime, date

TODAY = date.today()                      # fixed "current date" used for staleness/future checks


def clean_case_id(raw):
    """Normalize a raw case id to 'CC-#####', or raise if it can't be."""
    raw = raw.strip().upper().replace(" ", "").replace("-", "")
    if re.fullmatch(r"CC\d{5}", raw):
        return "CC-" + raw[2:]
    else:
        raise ValueError("bad case_id")


def clean_name(raw):
    """Collapse whitespace in a raw victim name and title-case it."""
    return " ".join(raw.split()).title()


def clean_sex(raw):
    """Normalize a raw sex string to 'M', 'F', or 'U' for anything else."""
    raw = raw.strip().upper()
    if raw in ["M", "MALE"]:
        return "M"
    elif raw in ["F", "FEMALE"]:
        return "F"
    else:
        return "U"


def clean_age(raw):
    """Return a plausible age (0-110) as an int, or None if out of range/blank."""
    raw = raw.strip()
    if raw.isdigit() and int(raw) <= 110:
        return int(raw)
    else:
        return None


def clean_beat(raw):
    """Extract a 3-digit police beat number from a raw string, or None."""
    match = re.search(r"\d{3}", raw)
    if match:
        return match.group()
    else:
        return None


def clean_status(raw):
    """Normalize a raw status to 'OPEN' or 'CLOSED', or raise if unmapped."""
    raw = raw.strip().upper()
    if raw in ["OPEN", "OPN"]:
        return "OPEN"
    elif raw in ["CLOSED", "CLSD", "CLEARED"]:
        return "CLOSED"
    else:
        raise ValueError("unknown status")


def clean_date(raw):
    """Parse a raw date string (3 accepted formats) into a date object, or raise."""
    raw = raw.strip()
    if raw == "" or raw.upper() in ["N/A", "UNKNOWN"]:
        raise ValueError("missing date")

    formats = ["%Y-%m-%d", "%m/%d/%Y", "%B %d, %Y"]
    for format in formats:
        try:
            result = datetime.strptime(raw, format).date()
        except ValueError:
            continue
        if result > TODAY:
            raise ValueError("future date")
        else:
            return result
    raise ValueError("invalid date")


def extract_callback_phone(tip_notes):
    """Find the first phone number in free-text tip notes, or '' if none."""
    match = re.search(r"\(?(\d{3})\)?[ .-](\d{3})[.-](\d{4})", tip_notes)
    if match:
        return "-".join(match.groups())
    else:
        return ""


class Case:
    """Represents one cleaned, validated case record."""

    def __init__(self, row):
        if len(row) != 9:
            raise ValueError("wrong field count")

        self.case_id = clean_case_id(row[0])
        self.victim_name = clean_name(row[1])
        self.sex = clean_sex(row[2])
        self.age = clean_age(row[3])
        self.incident_date = clean_date(row[4])
        self.beat = clean_beat(row[6])          # field 5, address, is unused
        self.status = clean_status(row[7])
        self.callback_phone = extract_callback_phone(row[8])

    @classmethod
    def from_row(cls, row):
        return cls(row)

    @property
    def year(self):
        return self.incident_date.year

    @property
    def decade(self):
        return (self.year // 10) * 10

    @property
    def years_unsolved(self):
        return TODAY.year - self.year

    @property
    def is_stale(self):
        return self.status == "OPEN" and self.years_unsolved >= 5
