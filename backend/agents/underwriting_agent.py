def check_eligibility(salary, amount, tenure):
    # Simple EMI-based logic
    emi = amount / (tenure * 12)

    if emi > 0.4 * salary:
        return {
            "approved": False,
            "message": "Your EMI is too high compared to your salary."
        }

    return {
        "approved": True,
        "message": "Congratulations 🎉 Based on your income, you are eligible for the loan."
    }