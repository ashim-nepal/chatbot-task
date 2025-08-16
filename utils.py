import re # All the required inputs
import validators
from dateutil import parser
from datetime import datetime, timedelta

def validate_email(email: str) -> bool: # To validate email
    try:
        return bool(validators.email(email))
    except Exception:
        return False

def validate_phone(phone: str) -> bool: # To validate phone number
    return re.fullmatch(r"\+?\d{10,15}", phone.strip()) is not None

def extract_date_from_text(text: str): # Function to extract date from text
    text = (text or "").strip()
    if not text:
        return None
    try:
        dt = parser.parse(text, fuzzy=True, dayfirst=False) # To parse date using dateutil parser
        return dt.strftime("%Y-%m-%d")
    except Exception:
        pass

    # MApping week days into integer to calculate difference in days
    days_map = {
        "sunday": 0, "monday": 1, "tuesday": 2, "wednesday": 3,
        "thursday": 4, "friday": 5, "saturday": 6 
    }
    low = text.lower()
    today = datetime.today()
    for name, idx in days_map.items():
        if name in low:
            diff = (idx - today.weekday() + 7) % 7
            if "next" in low or diff == 0:
                diff = 7 if diff == 0 else diff
            return (today + timedelta(days=diff)).strftime("%Y-%m-%d") # Return calculated day according to that day
    return None


# BY ASHIM NEPAL