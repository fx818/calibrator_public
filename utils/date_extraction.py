import re
from datetime import datetime

date_patterns = [
    # 12/05/2025 or 12-05-2025
    r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})",

    # 12 May 2025, 12May2025, 12May2025 (with/without space)
    r"(\d{1,2})\s*([A-Za-z]+)\s*(\d{4})"
]

def extract_date(text: str) -> str | None:
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            try:
                if len(match.groups()) == 3:
                    day, month, year = match.groups()

                    # If month is number
                    if month.isdigit():
                        date_obj = datetime.strptime(f"{day}-{month}-{year}", "%d-%m-%Y")
                    else:
                        date_obj = datetime.strptime(f"{day}-{month}-{year}", "%d-%B-%Y")
            except ValueError:
                try:
                    # Try abbreviated month (e.g. May, Jan)
                    date_obj = datetime.strptime(f"{day}-{month}-{year}", "%d-%b-%Y")
                except:
                    continue
            return date_obj.strftime("%Y-%m-%d")
    return None


# # 🔹 Test cases
# tests = [
#     "12 May2025",
#     "12May2025",
#     "12January 2025",
#     "12/05/2025",
#     "12-05-2025"
# ]

# for t in tests:
#     print(t, "->", extract_date(t))
