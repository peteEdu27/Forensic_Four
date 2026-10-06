# pattern_hunt.py
# Squad Lab: Operation Tip Line (Week 5)
# Mission: mine 24 free-text tips for phones, dates, case refs, and beats,
# then count the leads that die without a callback.
# Uses only: functions (def / docstring / return) and regular expressions (re.findall).

import re                                            # "re" is Python's built-in regular-expression toolbox; we need it for re.findall()

# ============================================================
# STEP 1: The extractors - ONE function, ONE pattern, ONE job
# ============================================================

def extract_phones(text):                            # "def" = define a reusable tool called extract_phones; "text" is the parameter (the input it receives)
    """Find every phone number, with or without parentheses around the area code."""   # docstring: a one-line description of what the function does
    return re.findall(r"\(?\d{3}\)?[ -]\d{3}-\d{4}", text)   # hunt text for the phone SHAPE and hand back a list of matches (see the breakdown below)
    # r"..."      -> the r means "raw string" so Python leaves the backslashes alone for regex to use
    # \(?         -> \( is a literal "(" and the ? makes it optional  (matches "(214" or "214")
    # \d{3}       -> exactly three digits (the area code)
    # \)?         -> an optional literal ")"
    # [ -]        -> exactly one character that is either a space or a dash (so "(214) 555" and "214-555" both work)
    # \d{3}-\d{4} -> three digits, a literal dash, four digits (the rest of the number)


def extract_case_refs(text):                         # second tool: finds case reference numbers
    """Find every case reference like CC-14589."""   # docstring
    return re.findall(r"CC-\d{5}", text)             # literal "CC-" followed by exactly five digits; returns a list of every match


def extract_beats(text):                             # third tool: finds beat numbers
    """Find every beat number mentioned, like 'beat 341' or 'Beat 341'."""   # docstring
    return re.findall(r"[Bb]eat (\d{3})", text)      # [Bb] = capital or lowercase b, then "eat ", then (\d{3}) = the parentheses CAPTURE just the 3 digits, so the list holds "341" not "beat 341"


def extract_iso_dates(text):                         # fourth tool: dates written year-first, like 2019-02-19
    """Find every ISO-style date like 2019-02-19."""   # docstring
    return re.findall(r"\d{4}-\d{2}-\d{2}", text)    # four digits, dash, two digits, dash, two digits


def extract_us_dates(text):                          # fifth tool: dates written month-first with slashes, like 4/7/2019
    """Find every US-style date like 4/7/2019 or 12/31/2020."""   # docstring
    return re.findall(r"\d{1,2}/\d{1,2}/\d{4}", text)   # \d{1,2} = one OR two digits (so "4" and "12" both work), slashes are plain characters, then a four-digit year


# ============================================================
# STEP 2: summarize_tip() calls the extractors and formats ONE line per tip
# ============================================================

def summarize_tip(number, tip):                      # takes the tip's position number and the tip's text
    """Build a one-line summary of everything found in a single tip."""   # docstring
    phones = extract_phones(tip)                     # run the phone tool on this tip; result is a list (empty list [] if none)
    refs = extract_case_refs(tip)                    # run the case-ref tool on this tip
    beats = extract_beats(tip)                       # run the beat tool on this tip
    iso_dates = extract_iso_dates(tip)               # run the ISO-date tool on this tip
    us_dates = extract_us_dates(tip)                 # run the US-date tool on this tip
    dates = iso_dates + us_dates                     # + on two lists glues them into one combined list of every numeric date found
    return f"TIP {number}: phone={phones} case={refs} beat={beats} date={dates}"   # f-string fills the {blanks} with our lists and returns the finished line as text


# ============================================================
# STEP 3: Read the tip file into a list, one tip per line
# ============================================================

tips = []                                            # empty list that will hold every tip from the file

with open("wk05_data_tipline.txt") as f:             # open the file and nickname it "f"; "with" closes it automatically when the block ends
    for line in f:                                   # read the file one line at a time
        tips.append(line.strip())                    # .strip() removes the invisible "\n" at the end of the line; .append() adds the clean tip to the list

# ============================================================
# STEP 4: Summarize every tip and count the callbacks
# ============================================================

with_callback = 0                                    # counter for tips that have at least 1 phone number (a way to call back); starts at 0
no_callback = 0                                      # counter for tips with no phone number (the lead dies); starts at 0

for i, tip in enumerate(tips, start=1):              # enumerate hands us a counter AND the tip each pass; start=1 so we number tips 1, 2, 3... instead of 0, 1, 2...
    print(summarize_tip(i, tip))                     # build the one-line summary for this tip and print it

    if len(extract_phones(tip)) >= 1:                # len() counts how many phones were found; 1 or more = someone left a callback number
        with_callback += 1                           # += 1 means "add 1 to the counter"
    else:                                            # otherwise the phone list was empty
        no_callback += 1                             # count it as a lead with no callback

# ============================================================
# STEP 5: Print the final report
# ============================================================

print()                                              # print() with nothing inside gives a blank line to separate the tips from the report
print("Tips processed:      ", len(tips))             # len(tips) = how many tips we read (24)
print("Tips with a callback:", with_callback)        # how many had a phone (15)
print("Tips with NO callback:", no_callback, "<- these leads die without follow-up")   # how many had none (9), plus the reminder text
