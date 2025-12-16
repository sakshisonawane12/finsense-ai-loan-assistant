def check_eligibility(salary: int = 0):
    # Simple, explainable underwriting rules
    MIN_SALARY = 30000
    CREDIT_SCORE = 750  # mock score

    if salary >= MIN_SALARY and CREDIT_SCORE >= 700:
        return {
            "approved": True,
            "message": "Congratulations 🎉 Based on your income and credit profile, you are eligible for the loan."
        }
    else:
        return {
            "approved": False,
            "message": "Sorry 😔 Based on the provided salary details, you are currently not eligible for this loan."
        }
