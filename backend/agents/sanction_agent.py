from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from datetime import date


def generate_sanction_letter(
    name: str = "Customer",
    amount: str = "5,00,000",
    tenure_years: int = 5,
    emi: int = 0,
    total_payable: int = 0,
    annual_rate: float = 10.5,
    ref_id: str = "",
) -> str:
    filename = "sanction_letter.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    w, h = A4

    # Header bar
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
    if ref_id:
        c.drawString(40, h - 125, f"Reference ID: {ref_id}")

    # Greeting
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 12)
    c.drawString(40, h - 160, f"Dear {name},")
    c.setFont("Helvetica", 11)
    c.drawString(40, h - 185,
        "We are pleased to inform you that your personal loan application has been")
    c.drawString(40, h - 200, "approved. Please find the sanction details below.")

    # Loan details box
    c.setFillColorRGB(0.95, 0.97, 1.0)
    c.setStrokeColorRGB(0.07, 0.22, 0.54)
    c.roundRect(40, h - 360, w - 80, 140, 8, fill=1, stroke=1)

    c.setFillColorRGB(0.07, 0.22, 0.54)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(55, h - 240, "Loan Sanction Details")

    details = [
        ("Loan Amount", f"Rs. {amount}"),
        ("Loan Tenure", f"{tenure_years} Years ({tenure_years * 12} Months)"),
        ("Annual Interest Rate", f"{annual_rate}% (Reducing Balance)"),
        ("Monthly EMI", f"Rs. {emi:,}" if emi else "—"),
        ("Total Payable", f"Rs. {total_payable:,}" if total_payable else "—"),
    ]

    c.setFont("Helvetica", 11)
    y = h - 265
    for label, value in details:
        c.setFillColorRGB(0.4, 0.4, 0.4)
        c.drawString(55, y, label)
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(260, y, value)
        c.setFont("Helvetica", 11)
        y -= 18

    # Terms
    c.setFillColorRGB(0.3, 0.3, 0.3)
    c.setFont("Helvetica", 10)
    c.drawString(40, h - 390, "Terms & Conditions:")
    terms = [
        "1. This sanction is valid for 30 days from the date of issue.",
        "2. Disbursement is subject to submission of required documents.",
        "3. EMI is calculated on reducing balance method.",
        "4. Prepayment charges may apply as per bank policy.",
    ]
    y = h - 408
    for t in terms:
        c.drawString(40, y, t)
        y -= 15

    # Footer
    c.setFillColorRGB(0.07, 0.22, 0.54)
    c.rect(0, 0, w, 50, fill=1, stroke=0)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica", 9)
    c.drawString(40, 30, "FinSense AI Loan Team  |  This is a system-generated letter.")
    c.drawString(40, 18, "EY Techathon 2025  |  Powered by Multi-Agent AI")

    c.save()
    return filename
