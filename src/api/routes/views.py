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
