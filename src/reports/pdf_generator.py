# src/reports/pdf_generator.py

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def markdown_to_pdf(markdown_text: str, output_path: str = "report.pdf") -> str:
    styles = getSampleStyleSheet()
    elements = []

    for line in markdown_text.split("\n"):
        if line.strip().startswith("#"):
            elements.append(Paragraph(f"<b>{line}</b>", styles["Heading2"]))
        else:
            elements.append(Paragraph(line, styles["Normal"]))
        elements.append(Spacer(1, 10))

    doc = SimpleDocTemplate(output_path, pagesize=A4)
    doc.build(elements)

    return output_path