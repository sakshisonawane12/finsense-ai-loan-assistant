import re


def extract_number(text: str) -> int:
    """Extract the first integer from a string."""
    digits = "".join(c for c in text if c.isdigit())
    return int(digits) if digits else 0


def is_valid_amount(text: str) -> bool:
    text = text.lower()
    return any(word in text for word in ["lakh", "lac", " l", "000"]) or extract_number(text) >= 10000


def extract_amount(text: str) -> int:
    """Parse loan amount to integer rupees."""
    text = text.lower()
    num = extract_number(text)
    if "lakh" in text or "lac" in text or " l" in text:
        return num * 100_000
    return num


def is_valid_salary(text: str) -> bool:
    return extract_number(text) >= 10000


def extract_salary(text: str) -> int:
    return extract_number(text)


def is_valid_tenure(text: str) -> bool:
    years = extract_number(text)
    return 1 <= years <= 30


def extract_tenure(text: str) -> int:
    return extract_number(text)
