import re

# ================= HELPERS =================

def extract_number(text: str) -> int:
    """Extract first integer from string"""
    digits = "".join(c for c in text if c.isdigit())
    return int(digits) if digits else 0


# ================= AMOUNT =================

def is_valid_amount(text: str) -> bool:
    """Validate loan amount between ₹10k and ₹50L"""
    amt = extract_amount(text)
    return 10000 <= amt <= 5_000_000


def extract_amount(text: str) -> int:
    """Parse loan amount like '5 lakh' or '500000'"""
    text = text.lower()
    num = extract_number(text)

    if "lakh" in text or "lac" in text or " l" in text:
        return num * 100_000

    if "crore" in text:
        return num * 10_000_000

    return num


# ================= SALARY =================

def is_valid_salary(text: str) -> bool:
    """Validate salary between ₹10k and ₹10L"""
    sal = extract_salary(text)
    return 10000 <= sal <= 1_000_000


def extract_salary(text: str) -> int:
    return extract_number(text)


# ================= TENURE =================

def is_valid_tenure(text: str) -> bool:
    """Validate tenure between 1 and 30 years"""
    t = extract_tenure(text)
    return 1 <= t <= 30


def extract_tenure(text: str) -> int:
    return extract_number(text)