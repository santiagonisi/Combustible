from src.schemas.report import MonthlyReport
from src.schemas.voucher import VoucherRead
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
