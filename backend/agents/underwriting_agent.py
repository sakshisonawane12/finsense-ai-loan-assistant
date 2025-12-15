def check_eligibility():
    # Dummy underwriting logic
    credit_score = 750
    salary = 50000

    if credit_score >= 700 and salary >= 30000:
        return {
            "approved": True,
            "message": "Congratulations 🎉 You are eligible for the loan."
        }
    else:
        return {
            "approved": False,
            "message": "Sorry 😔 You are not eligible for the loan."
        }
