from sqlalchemy.orm import Session

from src.models.vehicle import Vehicle
from src.schemas.vehicle import VehicleCreate


def list_vehicles(db: Session) -> list[Vehicle]:
    return db.query(Vehicle).order_by(Vehicle.active.desc(), Vehicle.code.asc()).all()


def create_vehicle(db: Session, payload: VehicleCreate) -> Vehicle:
    vehicle = Vehicle(**payload.model_dump())
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle
