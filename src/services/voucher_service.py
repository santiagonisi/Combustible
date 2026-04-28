from datetime import date

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from src.models.vehicle import Vehicle
from src.models.voucher import Voucher
from src.schemas.voucher import VoucherCreate


def _serial_for_month(db: Session, issue_date: date) -> str:
    first_day = issue_date.replace(day=1)
    if issue_date.month == 12:
        next_month = issue_date.replace(year=issue_date.year + 1, month=1, day=1)
    else:
        next_month = issue_date.replace(month=issue_date.month + 1, day=1)

    count = (
        db.query(func.count(Voucher.id))
        .filter(and_(Voucher.issue_date >= first_day, Voucher.issue_date < next_month))
        .scalar()
    )
    sequence = int(count or 0) + 1
    return f"VAL-{issue_date.strftime('%Y%m')}-{sequence:04d}"


def create_voucher(db: Session, payload: VoucherCreate) -> Voucher:
    vehicle = db.query(Vehicle).filter(Vehicle.id == payload.vehicle_id, Vehicle.active.is_(True)).first()
    if not vehicle:
        raise ValueError("El vehiculo seleccionado no existe o esta inactivo")

    serial = _serial_for_month(db, payload.issue_date)
    data = payload.model_dump()
    data["liters"] = float(data["liters"] or 0)
    voucher = Voucher(serial_number=serial, **data)
    db.add(voucher)
    db.commit()
    db.refresh(voucher)
    return voucher


def list_vouchers_by_month(db: Session, month: str) -> list[Voucher]:
    year, mon = [int(x) for x in month.split("-")]
    first_day = date(year=year, month=mon, day=1)
    if mon == 12:
        next_month = date(year=year + 1, month=1, day=1)
    else:
        next_month = date(year=year, month=mon + 1, day=1)

    return (
        db.query(Voucher)
        .filter(and_(Voucher.issue_date >= first_day, Voucher.issue_date < next_month))
        .order_by(Voucher.issue_date.desc(), Voucher.id.desc())
        .all()
    )
