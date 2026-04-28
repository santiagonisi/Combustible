from pydantic import BaseModel

from src.schemas.voucher import VoucherRead


class MonthlyReport(BaseModel):
    month: str
    total_vouchers: int
    total_liters: float
    vouchers: list[VoucherRead]
