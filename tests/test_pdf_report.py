import os
import pytest
from backend.database import SessionLocal
from backend.services.kpi_service import KPIService
from backend.services.pdf_report_service import PDFReportService

def test_pdf_report_generation():
    db = SessionLocal()
    try:
        kpi_service = KPIService(db)
        pdf_service = PDFReportService()

        pdf_path = pdf_service.generate_consolidated_bi_report(
            session_id=999,
            kpi_data=kpi_service.get_executive_kpis(),
            monthly_data=kpi_service.get_monthly_metrics(),
            category_data=kpi_service.get_category_performance(),
            channel_data=kpi_service.get_channel_performance(),
            store_data=kpi_service.get_store_performance(),
            stockout_data=kpi_service.get_stockout_alerts(),
            strategy_text="Test Strategy",
            verification_text="Certified 100% Mathematically Verified"
        )

        assert os.path.exists(pdf_path)
        assert os.path.getsize(pdf_path) > 1000  # Non-empty PDF
    finally:
        db.close()
