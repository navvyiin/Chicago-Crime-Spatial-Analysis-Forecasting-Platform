from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from .config import REPORTS_DIR
import datetime

def generate_pdf_summary(features_gdf, moran, path=None):
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    if path is None:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        path = REPORTS_DIR / f"crime_summary_{ts}.pdf"

    c = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Chicago Crime Risk Summary")

    c.setFont("Helvetica", 11)
    c.drawString(50, height - 80, f"Generated: {datetime.datetime.now()}")

    # Simple stats
    crime = features_gdf["crime_count_total"]
    c.drawString(50, height - 110, f"Total crime count (selected types): {crime.sum()}")
    c.drawString(50, height - 130, f"Mean crime per cell: {crime.mean():.2f}")
    c.drawString(50, height - 150, f"Std dev crime per cell: {crime.std():.2f}")
    c.drawString(50, height - 170, f"Moran's I: {moran.I:.4f} (p={moran.p_norm:.4f})")

    c.showPage()
    c.save()
    return path