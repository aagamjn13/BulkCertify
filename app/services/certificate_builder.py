import os
import logging
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from app.core.config import settings

logger = logging.getLogger(__name__)

# Resolve the path to the background template image
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BG_IMAGE_PATH = os.path.join(BASE_DIR, "assets", "certificate_bg.jpg")

def generate_certificate_pdf(name: str, filename: str) -> str:
    """Generates a professional PDF certificate using ReportLab with a custom background."""
    filepath = os.path.join(settings.CERTIFICATES_DIR, filename)
    try:
        if name.lower() == "fail_me":
            raise ValueError("Deliberate generation failure for testing")

        # Set page size to Landscape Letter (11 x 8.5 inches)
        page_size = landscape(letter)
        c = canvas.Canvas(filepath, pagesize=page_size)
        width, height = page_size
        
        # Draw the beautiful background image covering the whole page
        if os.path.exists(BG_IMAGE_PATH):
            c.drawImage(BG_IMAGE_PATH, 0, 0, width=width, height=height)
        else:
            # Fallback if image is somehow missing
            c.setStrokeColor(HexColor("#2C3E50"))
            c.setLineWidth(10)
            c.rect(0.5*inch, 0.5*inch, width - 1*inch, height - 1*inch)

        # Draw "Certificate of Completion"
        c.setFillColor(HexColor("#0f3156"))
        c.setFont("Helvetica-Bold", 46)
        c.drawCentredString(width / 2.0, height - 160, "Certificate of Completion")
        
        # Subtitle
        c.setFont("Helvetica", 12)
        c.setFillColor(HexColor("#34495e"))
        c.drawCentredString(width / 2.0, height - 200, "THIS IS TO CERTIFY THAT")

        # Recipient Name (Elegant font)
        c.setFont("Times-BoldItalic", 56)
        c.setFillColor(HexColor("#111827"))
        c.drawCentredString(width / 2.0, height - 290, name)
        
        # Underline for the name
        c.setStrokeColor(HexColor("#0f3156"))
        c.setLineWidth(1.5)
        c.line(width / 2.0 - 180, height - 310, width / 2.0 + 180, height - 310)
        
        # Completion Text
        c.setFont("Helvetica", 12)
        c.setFillColor(HexColor("#34495e"))
        c.drawCentredString(width / 2.0, height - 350, "HAS SUCCESSFULLY COMPLETED")

        # Course Name
        c.setFont("Helvetica-Bold", 24)
        c.setFillColor(HexColor("#0f3156"))
        c.drawCentredString(width / 2.0, height - 410, "THE COURSE NAME")

        # Footer Lines (Date & Signature)
        c.setStrokeColor(HexColor("#34495e"))
        c.setLineWidth(1)
        
        # Date Line
        c.line(width / 2.0 - 280, 110, width / 2.0 - 120, 110)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(width / 2.0 - 200, 95, "DATE OF COMPLETION")
        
        # Signature Line
        c.line(width / 2.0 + 120, 110, width / 2.0 + 280, 110)
        c.drawCentredString(width / 2.0 + 200, 95, "SIGNATURE")

        c.save()
        return filepath
    except Exception as e:
        logger.error(f"Failed to generate PDF for {name}: {e}")
        if os.path.exists(filepath):
            os.remove(filepath)
        raise e
