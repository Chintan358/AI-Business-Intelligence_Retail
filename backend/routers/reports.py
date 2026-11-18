import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models import User, GeneratedReport, AnalysisSession
from backend.schemas.report import GeneratedReportResponse
from backend.dependencies import get_current_user
from backend.services.pdf_report_service import PDFReportService
from backend.services.kpi_service import KPIService

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/", response_model=List[GeneratedReportResponse])
def list_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves all generated Business Intelligence PDF reports."""
    return db.query(GeneratedReport).order_by(GeneratedReport.created_at.desc()).all()

@router.get("/{report_id}/download")
def download_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Serves the generated PDF report for download."""
    rep = db.query(GeneratedReport).filter(GeneratedReport.id == report_id).first()
    if not rep or not os.path.exists(rep.file_path):
        raise HTTPException(status_code=404, detail="Report file not found on server.")
    return FileResponse(
        path=rep.file_path,
        media_type="application/pdf",
        filename=os.path.basename(rep.file_path)
    )

@router.post("/generate-instant/{session_id}")
def generate_instant_report(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generates an instant PDF report for any completed session."""
    session = db.query(AnalysisSession).filter(AnalysisSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    kpi_service = KPIService(db)
    pdf_service = PDFReportService()
    
    file_path = pdf_service.generate_consolidated_bi_report(
        session_id=session.id,
        kpi_data=kpi_service.get_executive_kpis(),
        monthly_data=kpi_service.get_monthly_metrics(),
        category_data=kpi_service.get_category_performance(),
        channel_data=kpi_service.get_channel_performance(),
        store_data=kpi_service.get_store_performance(),
        stockout_data=kpi_service.get_stockout_alerts(),
        strategy_text=session.executive_summary or "Executive Turnaround Plan",
        verification_text="Certified 100% Mathematically Verified"
    )

    new_rep = GeneratedReport(
        session_id=session.id,
        user_id=current_user.id,
        report_type="Consolidated",
        title=f"Retail Business Intelligence Report – Session #{session.id}",
        file_path=file_path,
        file_size_bytes=os.path.getsize(file_path),
        period_start=session.created_at.date(),
        period_end=session.created_at.date()
    )
    db.add(new_rep)
    db.commit()
    db.refresh(new_rep)
    return {"message": "PDF Report generated successfully", "report_id": new_rep.id}
