from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.schemas.monthly_invoice import (
    MonthlyInvoiceCreate,
    MonthlyInvoiceRead,
    MonthlyInvoiceSummary,
    MonthlyInvoiceUpdate,
)
from src.services.monthly_invoice_service import (
    create_monthly_invoice,
    delete_monthly_invoice,
    monthly_invoice_summary,
    update_monthly_invoice,
)


router = APIRouter(prefix="/api/monthly-invoices", tags=["monthly-invoices"])


@router.get("", response_model=MonthlyInvoiceSummary)
def get_monthly_invoices(month: str = Query(..., pattern=r"^\d{4}-\d{2}$"), db: Session = Depends(get_db)):
    return monthly_invoice_summary(db, month)


@router.post("", response_model=MonthlyInvoiceRead)
def post_monthly_invoice(payload: MonthlyInvoiceCreate, db: Session = Depends(get_db)):
    return create_monthly_invoice(db, payload)


@router.put("/{invoice_id}", response_model=MonthlyInvoiceRead)
def put_monthly_invoice(invoice_id: int, payload: MonthlyInvoiceUpdate, db: Session = Depends(get_db)):
    try:
        return update_monthly_invoice(db, invoice_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.delete("/{invoice_id}")
def delete_monthly_invoice_by_id(invoice_id: int, db: Session = Depends(get_db)):
    try:
        delete_monthly_invoice(db, invoice_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return {"ok": True}
