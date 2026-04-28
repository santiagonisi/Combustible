from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.database import Base


class MonthlyInvoice(Base):
    __tablename__ = "monthly_invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    month: Mapped[str] = mapped_column(String(7), nullable=False, index=True)
    station: Mapped[str] = mapped_column(String(120), nullable=False)
    invoice_number: Mapped[str] = mapped_column(String(60), nullable=False)
    total_vouchers: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_liters: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    notes: Mapped[str] = mapped_column(String(300), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
