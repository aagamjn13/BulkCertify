import os
import logging
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from app.core.config import settings

logger = logging.getLogger(__name__)

def generate_certificate_pdf(name: str, filename: str) -> str:
    """Generates a professional PDF certificate using ReportLab."""
    filepath = os.path.join(settings.CERTIFICATES_DIR, filename)
    try:
        if name.lower() == "fail_me":
            raise ValueError("Deliberate generation failure for testing")

        c = canvas.Canvas(filepath, pagesize=letter)
        width, height = letter
        
        c.setStrokeColor(HexColor("#2C3E50"))
        c.setLineWidth(10)
        c.rect(0.5*inch, 0.5*inch, width - 1*inch, height - 1*inch)
        
        c.setStrokeColor(HexColor("#E74C3C"))
        c.setLineWidth(2)
        c.rect(0.6*inch, 0.6*inch, width - 1.2*inch, height - 1.2*inch)

        c.setFillColor(HexColor("#2C3E50"))
        c.setFont("Helvetica-Bold", 42)
        c.drawCentredString(width / 2.0, height - 3*inch, "CERTIFICATE")
        
        c.setFont("Helvetica", 16)
        c.setFillColor(HexColor("#7F8C8D"))
        c.drawCentredString(width / 2.0, height - 3.5*inch, "OF COMPLETION")

        c.setFont("Helvetica", 20)
        c.setFillColor(HexColor("#34495E"))
        c.drawCentredString(width / 2.0, height - 5*inch, "This is proudly presented to:")
        
        c.setFont("Helvetica-Bold", 36)
        c.setFillColor(HexColor("#E74C3C"))
        c.drawCentredString(width / 2.0, height - 6.5*inch, name)
        
        c.setFont("Helvetica", 12)
        c.setFillColor(HexColor("#95A5A6"))
        c.drawCentredString(width / 2.0, 1.5*inch, "Issued automatically by BulkCertify")

        c.save()
        return filepath
    except Exception as e:
        logger.error(f"Failed to generate PDF for {name}: {e}")
        if os.path.exists(filepath):
            os.remove(filepath)
        raise e
