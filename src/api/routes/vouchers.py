from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.schemas.voucher import VoucherCreate, VoucherRead
from src.services.voucher_service import create_voucher, delete_voucher, list_vouchers_by_month


router = APIRouter(prefix="/api/vouchers", tags=["vouchers"])


@router.get("", response_model=list[VoucherRead])
def get_vouchers(month: str = Query(..., pattern=r"^\d{4}-\d{2}$"), db: Session = Depends(get_db)):
    return list_vouchers_by_month(db, month)


@router.post("", response_model=VoucherRead)
def post_voucher(payload: VoucherCreate, db: Session = Depends(get_db)):
    try:
        return create_voucher(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.delete("/{voucher_id}", status_code=204)
def remove_voucher(voucher_id: int, db: Session = Depends(get_db)):
    result = delete_voucher(db, voucher_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Vale no encontrado")
