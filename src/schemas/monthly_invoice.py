from datetime import datetime

from pydantic import BaseModel, Field


class MonthlyInvoiceCreate(BaseModel):
    month: str = Field(pattern=r"^\d{4}-\d{2}$")
    station: str = Field(min_length=2, max_length=120)
    invoice_number: str = Field(min_length=2, max_length=60)
    total_vouchers: int = Field(ge=0)
    total_liters: float = Field(ge=0)
    total_amount: float = Field(ge=0)
    notes: str | None = Field(default="", max_length=300)


class MonthlyInvoiceUpdate(MonthlyInvoiceCreate):
    pass


class MonthlyInvoiceRead(BaseModel):
    id: int
    month: str
    station: str
    invoice_number: str
    total_vouchers: int
    total_liters: float
    total_amount: float
    notes: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class MonthlyInvoiceSummary(BaseModel):
    month: str
    total_invoices: int
    total_vouchers: int
    total_liters: float
    total_amount: float
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool
    invoices: list[MonthlyInvoiceRead]
