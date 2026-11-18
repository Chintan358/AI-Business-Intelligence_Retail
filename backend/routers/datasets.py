import os
import shutil
import pandas as pd
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models import User, UploadedDataset, Customer, Product, Transaction
from backend.services.ingestion_service import seed_database_from_excel
from backend.dependencies import get_current_user, RoleChecker
from backend.config import settings

router = APIRouter(prefix="/datasets", tags=["Datasets"])

@router.post("/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin", "manager"]))
):
    # Validate extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".xlsx", ".xls", ".csv"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Please upload an Excel (.xlsx, .xls) or CSV file."
        )

    # Save to uploads directory
    saved_filename = f"{datetime_stamp()}_{file.filename}"
    file_path = os.path.join(settings.UPLOADS_DIR, saved_filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(file_path)

    try:
        if ext in [".xlsx", ".xls"]:
            # Validate sheets
            xl = pd.ExcelFile(file_path)
            sheets = xl.sheet_names
            required = ["Customers", "Products", "Transactions"]
            missing = [r for r in required if r not in sheets]
            if missing:
                raise HTTPException(
                    status_code=400,
                    detail=f"Workbook missing required sheets: {missing}. Found: {sheets}"
                )

            # Ingest dataset
            result = seed_database_from_excel(db, excel_path=file_path)
            total_recs = result.get("transactions", 0) + result.get("items", 0)

            dataset_rec = UploadedDataset(
                user_id=current_user.id,
                filename=file.filename,
                file_size_bytes=file_size,
                total_records=total_recs,
                sheet_details=result,
                status="Completed"
            )
            db.add(dataset_rec)
            db.commit()
            db.refresh(dataset_rec)

            return {
                "message": "Dataset uploaded and processed successfully into PostgreSQL.",
                "dataset_id": dataset_rec.id,
                "ingestion_result": result
            }
        else:
            # Single CSV upload
            df = pd.read_csv(file_path)
            dataset_rec = UploadedDataset(
                user_id=current_user.id,
                filename=file.filename,
                file_size_bytes=file_size,
                total_records=len(df),
                sheet_details={"CSV": len(df)},
                status="Completed"
            )
            db.add(dataset_rec)
            db.commit()
            return {
                "message": f"CSV dataset uploaded with {len(df)} records.",
                "dataset_id": dataset_rec.id
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing dataset: {str(e)}")

def datetime_stamp():
    import datetime
    return datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")

@router.get("/history")
def get_dataset_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(UploadedDataset).order_by(UploadedDataset.created_at.desc()).all()

@router.get("/preview")
def get_dataset_preview(
    table: str = "transactions",
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Preview up to 50 records of any core table
    valid_tables = {
        "customers": "SELECT * FROM customers LIMIT :lim",
        "products": "SELECT * FROM products LIMIT :lim",
        "transactions": "SELECT * FROM transactions LIMIT :lim",
        "transaction_items": "SELECT * FROM transaction_items LIMIT :lim",
        "inventory_movements": "SELECT * FROM inventory_movements LIMIT :lim",
        "expenses": "SELECT * FROM expenses LIMIT :lim"
    }
    if table.lower() not in valid_tables:
        raise HTTPException(status_code=400, detail=f"Invalid table name. Allowed: {list(valid_tables.keys())}")

    from sqlalchemy import text
    query = text(valid_tables[table.lower()])
    rows = db.execute(query, {"lim": limit}).mappings().all()
    return {
        "table": table,
        "count": len(rows),
        "data": [dict(r) for r in rows]
    }
