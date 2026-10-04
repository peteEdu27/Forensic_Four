import re
tips = "Week_5/wk05_data_tipline.txt"

# Reuse the `tips` name for the file's text content once it's loaded.
with open(tips) as file:
    tips = file.read()

def extract_phones():
    """Return all phone numbers found in the tips text (e.g. (555) 123-4567, 555-123-4567)."""
    numbers = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', tips)
    return numbers

def extract_case_refs():
    """Return all case reference codes found in the tips text (format: CC-12345)."""
    case_refs = re.findall(r'CC-\d{5}', tips)
    return case_refs

def extract_beats():
    """Return all patrol beat numbers mentioned in the tips text (e.g. "Beat 042")."""
    beats = re.findall(r'[Bb]eat (\d{3})', tips)
    return beats

def extract_iso_dates():
    """Return all ISO-format dates (YYYY-MM-DD) found in the tips text."""
    iso_dates = re.findall(r'\b\d{4}-\d{2}-\d{2}\b', tips)
    return iso_dates

def extract_us_dates():
    """Return all US-format dates (M/D/YYYY) found in the tips text."""
    us_dates = re.findall(r'\b\d{1,2}/\d{1,2}/\d{4}\b', tips)
    return us_dates

def summarize_tip():
    """Print counts/lists of every pattern type (phones, case refs, beats, dates) found in the tips text."""
    summary_dict = {
        "Phones": extract_phones(),
        "Case References": extract_case_refs(),
        "Beats": extract_beats(),
        "ISO Dates": extract_iso_dates(),
        "US Dates": extract_us_dates()
    }
    for key, value in summary_dict.items():
        print(f"\n{key}: {value}")

total_tips = len(tips.strip().split('\n'))
callback_count = len(extract_phones())
no_callback_count = total_tips - callback_count

print("\nTips processed:       ", total_tips)
print("Tips with a callback: ", callback_count)
print("Tips with NO callback:", no_callback_count)
summarize_tip()