from src.schemas.report import MonthlyReport
from src.schemas.voucher import VoucherRead
from src.services.voucher_service import list_vouchers_by_month


def monthly_report(db, month: str) -> MonthlyReport:
    vouchers = list_vouchers_by_month(db, month)
    total_liters = round(sum((v.liters or 0) for v in vouchers), 2)
    serialized = [VoucherRead.model_validate(v) for v in vouchers]
    return MonthlyReport(
        month=month,
        total_vouchers=len(vouchers),
        total_liters=total_liters,
        vouchers=serialized,
    )
