def is_valid_amount(text: str) -> bool:
    # accepts numbers like 5 lakh, 500000, 2L
    text = text.lower()
    return any(word in text for word in ["lakh", "lac", "l", "000"])

def is_valid_salary(text: str) -> bool:
    # salary should be a number >= 10000
    digits = "".join(c for c in text if c.isdigit())
    if not digits:
        return False
    return int(digits) >= 10000
def is_valid_tenure(text: str) -> bool:
    digits = "".join(c for c in text if c.isdigit())
    if not digits:
        return False
    years = int(digits)
    return 1 <= years <= 30
