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


class StationBreakdownItem(BaseModel):
    station: str
    total_vouchers: int
    total_liters: float
    avg_liters_per_voucher: float
    share_percent: float


class StationBreakdownReport(BaseModel):
    month: str
    total_vouchers: int
    total_liters: float
    stations: list[StationBreakdownItem]
