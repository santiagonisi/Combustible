from sqlalchemy.orm import Session

from src.models.station import Station
from src.schemas.station import StationCreate, StationUpdate


def _clean_payload(payload: StationCreate | StationUpdate) -> dict:
    data = payload.model_dump()
    for field in ("name", "cuit", "address", "contact", "current_account"):
        data[field] = str(data.get(field) or "").strip()
    return data


def list_stations(db: Session) -> list[Station]:
    return db.query(Station).order_by(Station.active.desc(), Station.name.asc()).all()


def create_station(db: Session, payload: StationCreate) -> Station:
    station = Station(**_clean_payload(payload))
    db.add(station)
    db.commit()
    db.refresh(station)
    return station


def update_station(db: Session, station_id: int, payload: StationUpdate) -> Station | None:
    station = db.query(Station).filter(Station.id == station_id).first()
    if not station:
        return None
    for field, value in _clean_payload(payload).items():
        setattr(station, field, value)
    db.commit()
    db.refresh(station)
    return station