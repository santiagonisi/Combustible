from sqlalchemy import and_, func

from src.models.voucher import Voucher
from src.schemas.report import MonthlyReport, StationBreakdownItem, StationBreakdownReport
from src.schemas.voucher import VoucherRead
from src.services.voucher_service import _month_bounds
from src.services.voucher_service import list_vouchers_by_month_paginated


def monthly_report(db, month: str, page: int = 1, page_size: int = 10, search: str | None = None) -> MonthlyReport:
    vouchers, total_vouchers, total_liters, safe_page = list_vouchers_by_month_paginated(
        db,
        month,
        page,
        page_size,
        search=search,
    )
    serialized = [VoucherRead.model_validate(v) for v in vouchers]
    total_pages = max(1, (total_vouchers + page_size - 1) // page_size)

    return MonthlyReport(
        month=month,
        total_vouchers=total_vouchers,
        total_liters=total_liters,
        page=safe_page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=safe_page < total_pages,
        has_prev=safe_page > 1,
        vouchers=serialized,
    )


def station_breakdown_report(db, month: str) -> StationBreakdownReport:
    first_day, next_month = _month_bounds(month)

    rows = (
        db.query(
            Voucher.station.label("station"),
            func.count(Voucher.id).label("total_vouchers"),
            func.coalesce(func.sum(Voucher.liters), 0.0).label("total_liters"),
        )
        .filter(and_(Voucher.issue_date >= first_day, Voucher.issue_date < next_month))
        .group_by(Voucher.station)
        .order_by(func.count(Voucher.id).desc(), func.coalesce(func.sum(Voucher.liters), 0.0).desc())
        .all()
    )

    total_vouchers = sum(int(row.total_vouchers or 0) for row in rows)
    total_liters = float(sum(float(row.total_liters or 0.0) for row in rows))

    stations: list[StationBreakdownItem] = []
    for row in rows:
        station_vouchers = int(row.total_vouchers or 0)
        station_liters = float(row.total_liters or 0.0)
        avg_liters = station_liters / station_vouchers if station_vouchers else 0.0
        share_percent = (station_liters / total_liters * 100.0) if total_liters > 0 else 0.0
        stations.append(
            StationBreakdownItem(
                station=str(row.station),
                total_vouchers=station_vouchers,
                total_liters=round(station_liters, 2),
                avg_liters_per_voucher=round(avg_liters, 2),
                share_percent=round(share_percent, 2),
            )
        )

    return StationBreakdownReport(
        month=month,
        total_vouchers=total_vouchers,
        total_liters=round(total_liters, 2),
        stations=stations,
    )
