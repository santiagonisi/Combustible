from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload

from src.db.database import get_db
from src.models.voucher import Voucher
from src.services.voucher_pdf_service import build_voucher_pdf


templates = Jinja2Templates(directory="src/web/templates")
router = APIRouter(tags=["views"])


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/favicon.ico", include_in_schema=False)
def favicon():
    return RedirectResponse(url="/static/img/logo.png")




@router.get("/print/{voucher_id}", response_class=HTMLResponse)
def print_voucher(
    voucher_id: int,
    request: Request,
    mode: str = Query(default="station", pattern="^(station|internal)$"),
    format: str = Query(default="html", pattern="^(html|pdf)$"),
    download: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    voucher = (
        db.query(Voucher)
        .options(joinedload(Voucher.vehicle))
        .filter(Voucher.id == voucher_id)
        .first()
    )
    if not voucher:
        raise HTTPException(status_code=404, detail="Vale no encontrado")
    if format == "pdf":
        pdf_content = build_voucher_pdf(voucher, mode=mode)
        disposition_type = "attachment" if download else "inline"
        suffix = "control_interno" if mode == "internal" else "estacion"
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'{disposition_type}; filename="{voucher.serial_number}_{suffix}.pdf"'
            },
        )

    response = templates.TemplateResponse(
        "print_voucher.html",
        {
            "request": request,
            "voucher": voucher,
            "mode": mode,
        },
    )
    if download:
        suffix = "control_interno" if mode == "internal" else "estacion"
        response.headers["Content-Disposition"] = (
            f'attachment; filename="{voucher.serial_number}_{suffix}.html"'
        )
    return response
