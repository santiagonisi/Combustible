from datetime import datetime

from pydantic import BaseModel, Field


class VehicleCreate(BaseModel):
    code: str = Field(min_length=2, max_length=40)
    plate: str = Field(min_length=5, max_length=20)
    brand: str = Field(min_length=2, max_length=60)
    model: str = Field(min_length=1, max_length=60)
    fuel_type: str = Field(min_length=3, max_length=20)


class VehicleRead(BaseModel):
    id: int
    code: str
    plate: str
    brand: str
    model: str
    fuel_type: str
    active: bool
    created_at: datetime

    class Config:
        from_attributes = True
