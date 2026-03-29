# agents/sanction_agent.py

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime


def generate_sanction_letter(
    name: str,
    amount: str,
    tenure_years: int,
    emi: int,
    total_payable: int,
    annual_rate: float,
    ref_id: str,
    risk_profile: str = "N/A",
    credit_score: int = 0,
    confidence: int = 0,
):
    """
    Generates professional sanction letter PDF with explainability
    """

    file_path = "sanction_letter.pdf"

    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter

    # ================= HEADER =================
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 50, "FinSense AI Loan Sanction Letter")

    c.setFont("Helvetica", 10)
    c.drawString(50, height - 70, f"Reference ID: {ref_id}")
    c.drawString(400, height - 70, f"Date: {datetime.now().strftime('%d %b %Y')}")

    # ================= CUSTOMER =================
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 110, "Applicant Details")

    c.setFont("Helvetica", 11)
    c.drawString(50, height - 130, f"Name: {name}")

    # ================= LOAN DETAILS =================
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 170, "Loan Details")

    c.setFont("Helvetica", 11)
    c.drawString(50, height - 190, f"Loan Amount: ₹{amount}")
    c.drawString(50, height - 210, f"Tenure: {tenure_years} years")
    c.drawString(50, height - 230, f"Interest Rate: {annual_rate}% p.a.")

    # ================= EMI =================
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 270, "Repayment Summary")

    c.setFont("Helvetica", 11)
    c.drawString(50, height - 290, f"Monthly EMI: ₹{emi}")
    c.drawString(50, height - 310, f"Total Payable: ₹{total_payable}")

    # ================= AI DECISION =================
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 350, "AI Decision Insights")

    c.setFont("Helvetica", 11)
    c.drawString(50, height - 370, f"Risk Profile: {risk_profile}")
    c.drawString(50, height - 390, f"Credit Score: {credit_score}")
    c.drawString(50, height - 410, f"Confidence Score: {confidence}%")

    # ================= TERMS =================
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 450, "Terms & Conditions")

    c.setFont("Helvetica", 10)
    c.drawString(50, height - 470, "• Loan subject to final verification.")
    c.drawString(50, height - 485, "• Timely EMI payments required.")
    c.drawString(50, height - 500, "• FinSense reserves the right to revoke approval.")

    # ================= FOOTER =================
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(50, 50, "This is an AI-generated sanction letter.")

    c.save()

    return file_path