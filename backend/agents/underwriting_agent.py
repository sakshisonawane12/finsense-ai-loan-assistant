from agents.verification_agent import query_kyc_confidence

MIN_SALARY = 30000
CREDIT_SCORE = 750
INTEREST_RATE = 10.5
KYC_CONFIDENCE_THRESHOLD = 90


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


def check_eligibility(salary: int = 0, requested_amount: int = 0, tenure_years: int = 5) -> dict:
    # Agent-to-agent: query VerificationAgent
    kyc_check = query_kyc_confidence(threshold=KYC_CONFIDENCE_THRESHOLD)

    if not kyc_check["kyc_verified"]:
        return {
            "approved": False, "confidence": 0, "reason": "kyc_failed",
            "rule_triggered": "KYC_CONFIDENCE_RULE_001",
            "explanation": f"KYC confidence {kyc_check['confidence']}% below required {KYC_CONFIDENCE_THRESHOLD}%",
            "message": "KYC verification did not pass. Please retry.",
            "agent": "UnderwritingAgent", "kyc_confidence": kyc_check["confidence"],
        }

    max_eligible = calculate_max_eligible_amount(salary)
    salary_ok = salary >= MIN_SALARY
    credit_ok = CREDIT_SCORE >= 700
    amount_ok = requested_amount <= max_eligible if requested_amount > 0 else True

    salary_score = min(70, int((salary / MIN_SALARY) * 70))
    credit_score_val = min(30, int(((CREDIT_SCORE - 700) / 150) * 30)) if credit_ok else 0
    confidence = min(99, salary_score + credit_score_val)

    rules_checked = [
        {"rule": "MIN_SALARY_RULE_001", "description": f"Monthly salary ≥ ₹{MIN_SALARY:,}",
         "actual": f"₹{salary:,}", "passed": salary_ok},
        {"rule": "CREDIT_SCORE_RULE_002", "description": "Credit score ≥ 700",
         "actual": str(CREDIT_SCORE), "passed": credit_ok},
        {"rule": "AMOUNT_ELIGIBILITY_RULE_003",
         "description": f"Requested ≤ max eligible ₹{max_eligible:,}",
         "actual": f"₹{requested_amount:,}" if requested_amount else "N/A", "passed": amount_ok},
    ]

    if salary_ok and credit_ok:
        emi_data = calculate_emi(requested_amount or max_eligible, tenure_years)
        return {
            "approved": True, "confidence": confidence, "reason": "eligible",
            "rule_triggered": "ALL_RULES_PASSED",
            "explanation": f"Salary ₹{salary:,} ≥ ₹{MIN_SALARY:,} ✅ | Credit score {CREDIT_SCORE} ≥ 700 ✅",
            "rules_checked": rules_checked, "emi": emi_data,
            "max_eligible_amount": max_eligible,
            "message": "Congratulations 🎉 Based on your income and credit profile, you are eligible for the loan.",
            "agent": "UnderwritingAgent", "kyc_confidence": kyc_check["confidence"],
        }

    failed = [r["rule"] for r in rules_checked if not r["passed"]]
    alt_emi = calculate_emi(max_eligible, tenure_years) if max_eligible > 0 else {}
    suggestion = (
        f"Based on your salary ₹{salary:,}, you may be eligible for up to ₹{max_eligible:,}. "
        "Reply 'yes' to proceed."
    ) if salary < MIN_SALARY else ""

    return {
        "approved": False, "confidence": max(10, confidence),
        "reason": "low_salary" if not salary_ok else "low_credit",
        "rule_triggered": failed[0] if failed else "UNKNOWN",
        "explanation": f"Salary ₹{salary:,} < required ₹{MIN_SALARY:,}" if not salary_ok else f"Credit score {CREDIT_SCORE} < 700",
        "rules_checked": rules_checked, "max_eligible_amount": max_eligible,
        "suggestion": suggestion, "alt_emi": alt_emi,
        "message": f"Sorry 😔 Not eligible for requested amount. {suggestion}".strip(),
        "agent": "UnderwritingAgent", "kyc_confidence": kyc_check["confidence"],
    }
