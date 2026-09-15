from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.schemas.station import StationCreate, StationRead, StationUpdate
from src.services.station_service import create_station, list_stations, update_station


router = APIRouter(prefix="/api/stations", tags=["stations"])


@router.get("", response_model=list[StationRead])
def get_stations(db: Session = Depends(get_db)):
    return list_stations(db)


@router.post("", response_model=StationRead)
def post_station(payload: StationCreate, db: Session = Depends(get_db)):
    try:
        return create_station(db, payload)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="El CUIT de la estacion ya esta registrado")


@router.put("/{station_id}", response_model=StationRead)
def put_station(station_id: int, payload: StationUpdate, db: Session = Depends(get_db)):
    try:
        result = update_station(db, station_id, payload)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="El CUIT de la estacion ya esta registrado")
    if result is None:
        raise HTTPException(status_code=404, detail="Estacion no encontrada")
    return result