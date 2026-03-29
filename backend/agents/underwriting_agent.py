from typing import List

# ================= CONSTANTS =================
MIN_SALARY = 30000
INTEREST_RATE = 10.5
FOIR_LIMIT = 0.4  # EMI ≤ 40% of salary


# ================= HELPERS =================

def get_credit_score(user_id: str) -> int:
    """Deterministic credit score"""
    return 650 + (hash(user_id) % 150)


def calculate_max_eligible_amount(salary: int) -> int:
    return min(salary * 10, 5_000_000)


def calculate_emi(principal: int, tenure_years: int, annual_rate: float = INTEREST_RATE) -> dict:
    r = annual_rate / (12 * 100)
    n = tenure_years * 12

    emi = principal * r * (1 + r) ** n / ((1 + r) ** n - 1) if r else principal / n
    total_payable = emi * n

    return {
        "emi": round(emi),
        "total_payable": round(total_payable),
        "total_interest": round(total_payable - principal),
        "tenure_months": n,
        "annual_rate": annual_rate,
    }


# ================= MAIN =================

def check_eligibility(
    user_id: str,
    salary: int,
    requested_amount: int,
    tenure_years: int,
    kyc_confidence: int
) -> dict:

    # ❌ KYC fail
    if kyc_confidence < 90:
        return {
            "approved": False,
            "confidence": 0,
            "reason": "kyc_failed",
            "message": "KYC verification failed.",
            "kyc_confidence": kyc_confidence,
        }

    credit_score = get_credit_score(user_id)

    max_eligible = calculate_max_eligible_amount(salary)
    emi_data = calculate_emi(requested_amount or max_eligible, tenure_years)

    # RULES
    salary_ok = salary >= MIN_SALARY
    credit_ok = credit_score >= 700
    amount_ok = requested_amount <= max_eligible
    emi_ok = emi_data["emi"] <= FOIR_LIMIT * salary

    # CONFIDENCE
    salary_score = min(70, int((salary / MIN_SALARY) * 70))
    credit_score_val = min(30, int(((credit_score - 700) / 150) * 30)) if credit_ok else 0

    confidence = int(
        (salary_score / 70) * 40 +
        (credit_score_val / 30) * 40 +
        (kyc_confidence / 100) * 20
    )

    # RISK
    if confidence >= 75:
        risk = "Low Risk 🟢"
    elif confidence >= 55:
        risk = "Medium Risk 🟡"
    else:
        risk = "High Risk 🔴"

    # FLAGS
    flags: List[str] = []
    if salary > 500000:
        flags.append("Unusually high salary")
    if requested_amount > salary * 12:
        flags.append("High loan-to-income ratio")

    # APPROVED
    if salary_ok and credit_ok and amount_ok and emi_ok:
        return {
            "approved": True,
            "confidence": confidence,
            "risk_profile": risk,
            "credit_score": credit_score,
            "emi": emi_data,
            "max_eligible_amount": max_eligible,
            "flags": flags,
            "message": (
                f"🎉 Loan Approved!\n"
                f"• EMI ₹{emi_data['emi']} is safe\n"
                f"• Credit Score: {credit_score}\n"
                f"• Risk: {risk}"
            ),
            "kyc_confidence": kyc_confidence,
        }

    # REJECTED
    return {
        "approved": False,
        "confidence": confidence,
        "risk_profile": risk,
        "credit_score": credit_score,
        "max_eligible_amount": max_eligible,
        "flags": flags,
        "suggestion": f"Try ₹{max_eligible:,} or increase tenure.",
        "message": "❌ Loan not approved.",
        "kyc_confidence": kyc_confidence,
    }