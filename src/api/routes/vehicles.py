from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.schemas.vehicle import VehicleCreate, VehicleRead
from src.services.vehicle_service import create_vehicle, delete_vehicle, list_vehicles


router = APIRouter(prefix="/api/vehicles", tags=["vehicles"])


@router.get("", response_model=list[VehicleRead])
def get_vehicles(db: Session = Depends(get_db)):
    return list_vehicles(db)


@router.post("", response_model=VehicleRead)
def post_vehicle(payload: VehicleCreate, db: Session = Depends(get_db)):
    try:
        return create_vehicle(db, payload)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Codigo o placa ya registrado")


@router.delete("/{vehicle_id}", status_code=204)
def remove_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    result = delete_vehicle(db, vehicle_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Vehiculo no encontrado")
