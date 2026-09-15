from datetime import datetime

from pydantic import BaseModel, Field


class StationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    cuit: str = Field(min_length=11, max_length=13)
    address: str = Field(min_length=2, max_length=200)
    contact: str | None = Field(default="", max_length=120)
    current_account: str | None = Field(default="", max_length=120)


class StationUpdate(StationCreate):
    active: bool


class StationRead(StationCreate):
    id: int
    active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True