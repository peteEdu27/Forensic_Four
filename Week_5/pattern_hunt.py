import re  # regex module used for all pattern extraction

tip = "Week_5/wk05_data_tipline.txt"  # path to the raw tipline text file

# Reuse the `tips` name for the file's tip content once it's loaded.
with open(tip) as file:  # open the tipline file for reading
    tip = file.read()  # replace the path string with the file's full text content

def extract_phones(tip):
    """Return all phone numbers found in the given tip (e.g. (555) 123-4567, 555-123-4567)."""
    numbers = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', tip)  # match optional area code parens, 3 digits, separator, 3 digits, separator, 4 digits
    return numbers  # list of matched phone number strings

def extract_case_refs(tip):
    """Return all case reference codes found in the given tip (format: CC-12345)."""
    case_refs = re.findall(r'CC-\d{5}', tip)  # match literal "CC-" followed by exactly 5 digits
    return case_refs  # list of matched case reference codes

def extract_beats(tip):
    """Return all patrol beat numbers mentioned in the given tip (e.g. "Beat 042")."""
    beats = re.findall(r'[Bb]eat (\d{3})', tip)  # match "Beat"/"beat" followed by a captured 3-digit number
    return beats  # list of matched beat numbers

def extract_iso_dates(tip):
    """Return all ISO-format dates (YYYY-MM-DD) found in the given tip."""
    iso_dates = re.findall(r'\b\d{4}-\d{2}-\d{2}\b', tip)  # match a word-bounded YYYY-MM-DD date
    return iso_dates  # list of matched ISO dates

def extract_us_dates(tip):
    """Return all US-format dates (M/D/YYYY) found in the given tip."""
    us_dates = re.findall(r'\b\d{1,2}/\d{1,2}/\d{4}\b', tip)  # match a word-bounded M/D/YYYY date, allowing 1 or 2 digit month/day
    return us_dates  # list of matched US dates

def summarize_tip():
    """Print counts/lists of every pattern type (phones, case refs, beats, dates) found per tip line."""
    for index, line in enumerate(tip.strip().split('\n'), start = 1):  # iterate over each non-empty tip line with its index
        print(f"Tip {index}: Phones={extract_phones(line)} Case References={extract_case_refs(line)} Beats={extract_beats(line)} ISO Dates={extract_iso_dates(line)} US Dates={extract_us_dates(line)}")  # print each line's index and the lists of extracted patterns

total_tips = len(tip.strip().split('\n'))  # count total number of tip lines
callback_count = len(extract_phones(tip))  # count total phone numbers found across all tips
no_callback_count = total_tips - callback_count  # tips without a callback number

summarize_tip()  # print the per-line breakdown
print("\nTips processed:       ", total_tips)  # print total tip count
print("Tips with a callback: ", callback_count)  # print count of tips with a phone number
print("Tips with NO callback:", no_callback_count)  # print count of tips missing a phone number