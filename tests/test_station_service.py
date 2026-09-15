from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.db.database import Base
from src.models.station import Station
from src.models.vehicle import Vehicle
from src.schemas.station import StationCreate, StationUpdate
from src.schemas.voucher import VoucherCreate
from src.services.station_service import create_station, update_station
from src.services.voucher_service import create_voucher


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()


def test_station_can_be_created_and_deactivated(db_session):
    station = create_station(
        db_session,
        StationCreate(
            name="YPF Obra",
            cuit="30-12345678-9",
            address="Ruta 1 km 10",
            contact="1112345678",
            current_account="CC-001",
        ),
    )

    updated = update_station(
        db_session,
        station.id,
        StationUpdate(
            name=station.name,
            cuit=station.cuit,
            address=station.address,
            contact=station.contact,
            current_account=station.current_account,
            active=False,
        ),
    )

    assert updated is not None
    assert updated.active is False


def test_voucher_rejects_inactive_station(db_session):
    db_session.add(
        Vehicle(
            code="V-01",
            plate="AA123AA",
            brand="Ford",
            model="Ranger",
            fuel_type="Diesel Infinia",
            active=True,
        )
    )
    db_session.add(Station(name="YPF Obra", cuit="30-12345678-9", address="Ruta 1 km 10", active=False))
    db_session.commit()

    with pytest.raises(ValueError, match="estacion seleccionada"):
        create_voucher(
            db_session,
            VoucherCreate(
                issue_date=date(2026, 9, 15),
                employee_name="Ana Perez",
                area="Obra",
                vehicle_id=1,
                fuel_type="Diesel Infinia",
                liters=20,
                station="YPF Obra",
            ),
        )