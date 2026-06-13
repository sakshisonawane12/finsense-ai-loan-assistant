"""
sanction_agent.py
FIXED: unique PDF filename per user+ref_id — prevents race condition
where two concurrent users overwrite each other's PDF.
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import date

SANCTIONS_DIR = "sanctions"


def generate_sanction_letter(
    name: str = "Customer",
    amount: str = "5,00,000",
    tenure_years: int = 5,
    emi: int = 0,
    total_payable: int = 0,
    annual_rate: float = 10.5,
    ref_id: str = "",
    credit_score: int = 0,
    risk_profile: str = "N/A",
    confidence: int = 0,
) -> str:
    os.makedirs(SANCTIONS_DIR, exist_ok=True)
    # Unique filename per user — no race condition
    safe_ref = ref_id.replace("-", "_") if ref_id else "unknown"
    filename = os.path.join(SANCTIONS_DIR, f"sanction_{safe_ref}.pdf")

    c = canvas.Canvas(filename, pagesize=A4)
    w, h = A4

    # Header
    c.setFillColorRGB(0.07, 0.22, 0.54)
    c.rect(0, h - 80, w, 80, fill=1, stroke=0)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(40, h - 45, "FinSense AI")
    c.setFont("Helvetica", 11)
    c.drawString(40, h - 65, "Personal Loan Sanction Letter")

    # Ref + Date
    c.setFillColorRGB(0.3, 0.3, 0.3)
    c.setFont("Helvetica", 10)
    c.drawString(40, h - 110, f"Date: {date.today().strftime('%d %B %Y')}")
    c.drawString(40, h - 125, f"Reference ID: {ref_id}")

    # Greeting
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 12)
    c.drawString(40, h - 160, f"Dear {name},")
    c.setFont("Helvetica", 11)
    c.drawString(40, h - 180, "Your personal loan application has been approved.")

    # Loan details box
    c.setFillColorRGB(0.95, 0.97, 1.0)
    c.setStrokeColorRGB(0.07, 0.22, 0.54)
    c.roundRect(40, h - 380, w - 80, 175, 8, fill=1, stroke=1)

    c.setFillColorRGB(0.07, 0.22, 0.54)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(55, h - 230, "Loan Sanction Details")

    details = [
        ("Loan Amount",          f"Rs. {amount}"),
        ("Loan Tenure",          f"{tenure_years} Years ({tenure_years * 12} Months)"),
        ("Annual Interest Rate", f"{annual_rate}% (Reducing Balance)"),
        ("Monthly EMI",          f"Rs. {emi:,}" if emi else "—"),
        ("Total Payable",        f"Rs. {total_payable:,}" if total_payable else "—"),
        ("Total Interest",       f"Rs. {total_payable - int(amount.replace(',','')) if emi else '—'}"),
    ]

    c.setFont("Helvetica", 11)
    y = h - 255
    for label, value in details:
        c.setFillColorRGB(0.4, 0.4, 0.4)
        c.drawString(55, y, label)
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(260, y, value)
        c.setFont("Helvetica", 11)
        y -= 18

    # AI Decision insights
    c.setFillColorRGB(0.07, 0.22, 0.54)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, h - 400, "AI Decision Insights")
    c.setFont("Helvetica", 11)
    c.setFillColorRGB(0.2, 0.2, 0.2)
    c.drawString(40, h - 420, f"Risk Profile: {risk_profile}")
    c.drawString(40, h - 438, f"Credit Score: {credit_score}")
    c.drawString(40, h - 456, f"Underwriting Confidence: {confidence}%")

    # Terms
    c.setFont("Helvetica-Bold", 11)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(40, h - 490, "Terms & Conditions")
    c.setFont("Helvetica", 10)
    c.setFillColorRGB(0.3, 0.3, 0.3)
    for i, t in enumerate([
        "1. This sanction is valid for 30 days from the date of issue.",
        "2. Disbursement is subject to submission of required documents.",
        "3. EMI calculated on reducing balance method.",
        "4. Prepayment charges may apply as per policy.",
    ]):
        c.drawString(40, h - 510 - i * 16, t)

    # Footer
    c.setFillColorRGB(0.07, 0.22, 0.54)
    c.rect(0, 0, w, 50, fill=1, stroke=0)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica", 9)
    c.drawString(40, 30, "FinSense AI Loan Team  |  System-generated letter.")
    c.drawString(40, 18, "EY Techathon 2025  |  Powered by Multi-Agent AI")

    c.save()
    return filename
