from pydantic import BaseModel

from src.schemas.voucher import VoucherRead


class MonthlyReport(BaseModel):
    month: str
    total_vouchers: int
    total_liters: float
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool
    vouchers: list[VoucherRead]
