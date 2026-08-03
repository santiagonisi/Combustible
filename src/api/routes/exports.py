from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.services.export_service import export_vouchers_to_excel
from src.services.report_service import monthly_report
from src.services.voucher_service import list_vouchers_by_month_paginated

router = APIRouter(prefix="/api/export", tags=["export"])


@router.post("/vouchers")
def export_vouchers(payload: dict, db: Session = Depends(get_db)):
    month = payload.get("month")
    search = payload.get("search") or None
    filename = payload.get("filename") or "vales.xlsx"

    if not month:
        raise HTTPException(status_code=400, detail="Mes requerido")

    vouchers, _, _, _ = list_vouchers_by_month_paginated(db, month, page=1, page_size=1000, search=search)
    export_path = export_vouchers_to_excel(
        [
            {
                "serial_number": voucher.serial_number,
                "issue_date": voucher.issue_date,
                "employee_name": voucher.employee_name,
                "area": voucher.area,
                "vehicle_id": voucher.vehicle_id,
                "fuel_type": voucher.fuel_type,
                "liters": voucher.liters,
                "station": voucher.station,
                "notes": voucher.notes or "",
            }
            for voucher in vouchers
        ],
        filename,
    )

    return FileResponse(export_path, filename=filename, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
