from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.schemas.report import MonthlyReport
from src.services.report_service import monthly_report


router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/monthly", response_model=MonthlyReport)
def get_monthly_report(month: str = Query(..., pattern=r"^\d{4}-\d{2}$"), db: Session = Depends(get_db)):
    return monthly_report(db, month)
