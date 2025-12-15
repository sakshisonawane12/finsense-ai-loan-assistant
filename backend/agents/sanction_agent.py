from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import date

def generate_sanction_letter(name="Customer", amount="5,00,000"):
    filename = "sanction_letter.pdf"

    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Tata Capital")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 100, f"Date: {date.today()}")

    c.drawString(50, height - 150, f"Dear {name},")

    c.drawString(
        50,
        height - 190,
        f"We are pleased to inform you that your personal loan of ₹{amount}"
        " has been approved."
    )

    c.drawString(
        50,
        height - 230,
        "Please find the sanction details above. This letter is system generated."
    )

    c.drawString(50, height - 300, "Regards,")
    c.drawString(50, height - 320, "Tata Capital Loan Team")

    c.save()

    return filename
