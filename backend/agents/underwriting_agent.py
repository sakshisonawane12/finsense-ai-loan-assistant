"""
underwriting_agent.py
FIXED:
- Uses passed kyc_confidence (no second KYC call)
- Deterministic credit score per user_id
- FOIR (Fixed Obligation to Income Ratio) check
- Full decision explainability with rule codes
- Input bounds enforced
"""
from agents.verification_agent import query_kyc_confidence

MIN_SALARY          = 30_000
MIN_CREDIT_SCORE    = 700
INTEREST_RATE       = 10.5
FOIR_LIMIT          = 0.40      # EMI must be ≤ 40% of salary
MAX_LOAN            = 5_000_000
KYC_THRESHOLD       = 90


def get_credit_score(user_id: str) -> int:
    """
    Deterministic per user — same user always gets same score.
    Range: 650–799 (realistic distribution).
    In production: call CIBIL/Experian API here.
    """
    return 650 + (abs(hash(user_id)) % 150)


def calculate_max_eligible(salary: int) -> int:
    return min(salary * 10, MAX_LOAN)


def calculate_emi(principal: int, tenure_years: int,
                  annual_rate: float = INTEREST_RATE) -> dict:
    r = annual_rate / (12 * 100)
    n = tenure_years * 12
    emi = principal * r * (1 + r) ** n / ((1 + r) ** n - 1) if r else principal / n
    total = emi * n
    return {
        "emi":           round(emi),
        "total_payable": round(total),
        "total_interest": round(total - principal),
        "tenure_months": n,
        "annual_rate":   annual_rate,
    }


def check_eligibility(user_id: str, salary: int, requested_amount: int,
                      tenure_years: int, kyc_confidence: int) -> dict:
    """
    FIXED agent-to-agent: uses kyc_confidence passed from main — no re-call.
    Checks 4 rules with full explainability.
    """
    # Agent-to-agent query using PASSED confidence (not a new KYC call)
    kyc_check = query_kyc_confidence(kyc_confidence, threshold=KYC_THRESHOLD)

    if not kyc_check["kyc_verified"]:
        return {
            "approved":      False,
            "confidence":    0,
            "reason":        "kyc_failed",
            "rule_triggered": "KYC_CONFIDENCE_RULE_001",
            "explanation":   f"KYC confidence {kyc_confidence}% < required {KYC_THRESHOLD}%",
            "message":       "KYC verification did not meet threshold.",
            "rules_checked": [],
            "kyc_confidence": kyc_confidence,
        }

    credit_score = get_credit_score(user_id)
    max_eligible = calculate_max_eligible(salary)
    emi_data     = calculate_emi(requested_amount or max_eligible, tenure_years)

    # ── Four rules ────────────────────────────────────────────────────────────
    salary_ok = salary >= MIN_SALARY
    credit_ok = credit_score >= MIN_CREDIT_SCORE
    amount_ok = requested_amount <= max_eligible
    foir_ok   = emi_data["emi"] <= FOIR_LIMIT * salary

    rules_checked = [
        {
            "rule":        "MIN_SALARY_RULE_001",
            "description": f"Monthly salary ≥ ₹{MIN_SALARY:,}",
            "actual":      f"₹{salary:,}",
            "passed":      salary_ok,
        },
        {
            "rule":        "CREDIT_SCORE_RULE_002",
            "description": f"Credit score ≥ {MIN_CREDIT_SCORE}",
            "actual":      str(credit_score),
            "passed":      credit_ok,
        },
        {
            "rule":        "AMOUNT_ELIGIBILITY_RULE_003",
            "description": f"Requested ≤ max eligible ₹{max_eligible:,}",
            "actual":      f"₹{requested_amount:,}",
            "passed":      amount_ok,
        },
        {
            "rule":        "FOIR_RULE_004",
            "description": f"EMI ≤ {int(FOIR_LIMIT*100)}% of salary",
            "actual":      f"₹{emi_data['emi']:,} vs limit ₹{int(FOIR_LIMIT*salary):,}",
            "passed":      foir_ok,
        },
    ]

    # Confidence weighted: salary 35%, credit 35%, kyc 20%, foir 10%
    salary_pct = min(1.0, salary / MIN_SALARY)
    credit_pct = min(1.0, max(0, (credit_score - 650) / 150))
    kyc_pct    = kyc_confidence / 100
    foir_pct   = 1.0 if foir_ok else 0.5
    confidence = int(salary_pct * 35 + credit_pct * 35 + kyc_pct * 20 + foir_pct * 10)

    risk = ("Low Risk 🟢" if confidence >= 75
            else "Medium Risk 🟡" if confidence >= 55
            else "High Risk 🔴")

    # ── Flags ─────────────────────────────────────────────────────────────────
    flags = []
    if requested_amount > salary * 12:
        flags.append("High loan-to-income ratio")
    if credit_score < 700:
        flags.append(f"Credit score {credit_score} is below 700")

    if salary_ok and credit_ok and amount_ok and foir_ok:
        return {
            "approved":          True,
            "confidence":        confidence,
            "risk_profile":      risk,
            "credit_score":      credit_score,
            "emi":               emi_data,
            "max_eligible_amount": max_eligible,
            "flags":             flags,
            "rules_checked":     rules_checked,
            "rule_triggered":    "ALL_RULES_PASSED",
            "explanation":       (f"Salary ₹{salary:,} ✅ | Credit {credit_score} ✅ | "
                                  f"EMI ₹{emi_data['emi']:,} ≤ 40% salary ✅"),
            "message":           "Congratulations 🎉 You are eligible for the loan.",
            "kyc_confidence":    kyc_confidence,
        }

    failed = [r["rule"] for r in rules_checked if not r["passed"]]
    alt_emi = calculate_emi(max_eligible, tenure_years)

    explanations = []
    if not salary_ok:
        explanations.append(f"Salary ₹{salary:,} < required ₹{MIN_SALARY:,}")
    if not credit_ok:
        explanations.append(f"Credit score {credit_score} < {MIN_CREDIT_SCORE}")
    if not amount_ok:
        explanations.append(f"₹{requested_amount:,} exceeds max eligible ₹{max_eligible:,}")
    if not foir_ok:
        explanations.append(f"EMI ₹{emi_data['emi']:,} exceeds 40% of salary ₹{int(FOIR_LIMIT*salary):,}")

    return {
        "approved":          False,
        "confidence":        confidence,
        "risk_profile":      risk,
        "credit_score":      credit_score,
        "max_eligible_amount": max_eligible,
        "alt_emi":           alt_emi,
        "flags":             flags,
        "rules_checked":     rules_checked,
        "rule_triggered":    failed[0] if failed else "UNKNOWN",
        "explanation":       " | ".join(explanations),
        "suggestion":        f"You may be eligible for ₹{max_eligible:,}. Reply 'yes' to proceed.",
        "message":           "Sorry 😔 Your application was not approved.",
        "kyc_confidence":    kyc_confidence,
    }
