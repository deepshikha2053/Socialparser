import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

def generate_pdf(data):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setFont("Helvetica", 12)

    pdf.drawString(100, 750, "Forensic Investigation Report")
    y_position = 730

    for key, value in data.items():
        pdf.drawString(100, y_position, f"{key}: {value}")
        y_position -= 20

    pdf.save()
    buffer.seek(0)
    return buffer

def parse_json_file(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)
