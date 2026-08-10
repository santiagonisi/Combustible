from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.schemas.report import MonthlyReport, StationBreakdownReport
from src.services.report_service import monthly_report, station_breakdown_report


router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/monthly", response_model=MonthlyReport)
def get_monthly_report(
    month: str = Query(..., pattern=r"^\d{4}-\d{2}$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: str | None = Query(None),
    db: Session = Depends(get_db),
):
    return monthly_report(db, month, page, page_size, search=search)


@router.get("/stations", response_model=StationBreakdownReport)
def get_station_breakdown(
    month: str = Query(..., pattern=r"^\d{4}-\d{2}$"),
    db: Session = Depends(get_db),
):
    return station_breakdown_report(db, month)
