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


def delete_vehicle(db: Session, vehicle_id: int) -> None:
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        return None
    db.delete(vehicle)
    db.commit()
    return vehicle
