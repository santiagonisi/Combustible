from datetime import date, datetime

from pydantic import BaseModel, Field


class VoucherCreate(BaseModel):
    issue_date: date
    employee_name: str = Field(min_length=2, max_length=100)
    area: str = Field(min_length=2, max_length=100)
    vehicle_id: int
    fuel_type: str = Field(min_length=3, max_length=20)
    liters: float = Field(gt=0)
    station: str = Field(min_length=2, max_length=120)
    notes: str | None = Field(default="", max_length=300)


class VoucherRead(BaseModel):
    id: int
    serial_number: str
    issue_date: date
    employee_name: str
    area: str
    vehicle_id: int
    fuel_type: str
    liters: float
    station: str
    notes: str | None
    created_at: datetime

    class Config:
        from_attributes = True
