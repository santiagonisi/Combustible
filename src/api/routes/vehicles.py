from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.schemas.vehicle import VehicleCreate, VehicleRead
from src.services.vehicle_service import create_vehicle, list_vehicles


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
