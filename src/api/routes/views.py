from datetime import date
from types import SimpleNamespace

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload

from src.db.database import get_db
from src.models.voucher import Voucher


templates = Jinja2Templates(directory="src/web/templates")
router = APIRouter(tags=["views"])


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/print-preview", response_class=HTMLResponse)
def print_voucher_preview(request: Request):
    preview_voucher = SimpleNamespace(
        id=0,
        serial_number="I-2468",
        issue_date=date.today(),
        employee_name="Nombre y apellido",
        area="Obra de ejemplo",
        vehicle_id=0,
        fuel_type="ULTRA DIESEL",
        liters=120.0,
        station="GNC DE LA COSTA S.R.L.",
        notes="",
        vehicle=SimpleNamespace(
            brand="Mercedes-Benz",
            model="Atego 1726",
            plate="AA123BB",
        ),
    )
    return templates.TemplateResponse(
        "print_voucher.html",
        {
            "request": request,
            "voucher": preview_voucher,
        },
    )


@router.get("/print/{voucher_id}", response_class=HTMLResponse)
def print_voucher(voucher_id: int, request: Request, db: Session = Depends(get_db)):
    voucher = (
        db.query(Voucher)
        .options(joinedload(Voucher.vehicle))
        .filter(Voucher.id == voucher_id)
        .first()
    )
    if not voucher:
        raise HTTPException(status_code=404, detail="Vale no encontrado")
    return templates.TemplateResponse(
        "print_voucher.html",
        {
            "request": request,
            "voucher": voucher,
        },
    )
