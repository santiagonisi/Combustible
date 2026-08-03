from datetime import date

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from src.models.vehicle import Vehicle
from src.models.voucher import Voucher
from src.schemas.voucher import VoucherCreate


def normalize_voucher_payload(payload: dict) -> dict:
    normalized = dict(payload)
    normalized["employee_name"] = str(normalized.get("employee_name", "")).strip()
    normalized["area"] = str(normalized.get("area", "")).strip()
    normalized["fuel_type"] = str(normalized.get("fuel_type", "")).strip()
    normalized["station"] = str(normalized.get("station", "")).strip()
    notes = str(normalized.get("notes", "") or "").strip()
    normalized["notes"] = notes

    if normalized.get("vehicle_id") is None or normalized.get("vehicle_id") == "":
        normalized["vehicle_id"] = 0
    else:
        normalized["vehicle_id"] = int(normalized["vehicle_id"])

    if normalized.get("liters") in (None, "", " "):
        normalized["liters"] = 0.0
    else:
        normalized["liters"] = float(normalized["liters"])

    return normalized


def _month_bounds(month: str) -> tuple[date, date]:
    year, mon = [int(x) for x in month.split("-")]
    first_day = date(year=year, month=mon, day=1)
    if mon == 12:
        next_month = date(year=year + 1, month=1, day=1)
    else:
        next_month = date(year=year, month=mon + 1, day=1)
    return first_day, next_month


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
    if not payload.employee_name or not payload.area or not payload.station:
        raise ValueError("Completa nombre del responsable, area y estacion")

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
    first_day, next_month = _month_bounds(month)

    return (
        db.query(Voucher)
        .filter(and_(Voucher.issue_date >= first_day, Voucher.issue_date < next_month))
        .order_by(Voucher.issue_date.desc(), Voucher.id.desc())
        .all()
    )


def list_vouchers_by_month_paginated(
    db: Session, month: str, page: int = 1, page_size: int = 10, search: str | None = None
) -> tuple[list[Voucher], int, float, int]:
    first_day, next_month = _month_bounds(month)
    base_query = db.query(Voucher).filter(and_(Voucher.issue_date >= first_day, Voucher.issue_date < next_month))

    if search:
        term = f"%{search.strip().lower()}%"
        base_query = base_query.filter(
            func.lower(Voucher.serial_number).like(term)
            | func.lower(Voucher.employee_name).like(term)
            | func.lower(Voucher.area).like(term)
            | func.lower(Voucher.station).like(term)
            | func.lower(Voucher.notes).like(term)
        )

    total_vouchers = int(base_query.with_entities(func.count(Voucher.id)).scalar() or 0)
    total_liters = float(base_query.with_entities(func.coalesce(func.sum(Voucher.liters), 0.0)).scalar() or 0.0)

    if total_vouchers == 0:
        return [], 0, round(total_liters, 2), 1

    total_pages = max(1, (total_vouchers + page_size - 1) // page_size)
    safe_page = min(max(1, page), total_pages)
    offset = (safe_page - 1) * page_size

    items = (
        base_query.order_by(Voucher.issue_date.desc(), Voucher.id.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return items, total_vouchers, round(total_liters, 2), safe_page


def delete_voucher(db: Session, voucher_id: int) -> Voucher | None:
    voucher = db.query(Voucher).filter(Voucher.id == voucher_id).first()
    if not voucher:
        return None
    db.delete(voucher)
    db.commit()
    return voucher
