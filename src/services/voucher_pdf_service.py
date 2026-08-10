from __future__ import annotations

from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from src.models.voucher import Voucher


def _safe_text(value: object) -> str:
    if value is None:
        return ""
    return str(value)


def build_voucher_pdf(voucher: Voucher, mode: str = "station") -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    page_width, page_height = A4

    margin_x = 18 * mm
    y = page_height - 20 * mm
    content_width = page_width - (2 * margin_x)

    is_internal = mode == "internal"
    copy_label = "COPIA DE CONTROL INTERNO" if is_internal else "COPIA PARA ESTACION DE SERVICIO"
    signature_label = "Firma Responsable Planilla" if is_internal else "Firma Encargado de Combustible"

    # Outer frame
    pdf.setLineWidth(1.2)
    frame_bottom = 34 * mm
    frame_top = y + 8 * mm
    pdf.rect(margin_x, frame_bottom, content_width, frame_top - frame_bottom)

    # Header
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawCentredString(page_width / 2, y, "VALE DE COMBUSTIBLE")
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawRightString(margin_x + content_width - 8, y, f"NRO: {_safe_text(voucher.serial_number)}")
    y -= 8 * mm
    pdf.setFont("Helvetica-Bold", 9)
    pdf.setFillColor(colors.HexColor("#374151"))
    pdf.drawString(margin_x + 8, y, copy_label)
    pdf.setFillColor(colors.black)

    # Obra and date
    y -= 8 * mm
    pdf.setFont("Helvetica", 10)
    pdf.drawString(margin_x + 8, y, f"OBRA: {_safe_text(voucher.area)}")
    pdf.drawRightString(margin_x + content_width - 8, y, f"FECHA: {_safe_text(voucher.issue_date)}")

    # Fuel table
    y -= 10 * mm
    row_h = 7 * mm
    col_1 = margin_x + 8
    col_2 = margin_x + content_width * 0.62
    col_3 = margin_x + content_width * 0.80
    table_right = margin_x + content_width - 8

    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(col_1, y, "TIPO DE COMBUSTIBLE")
    pdf.drawString(col_2, y, "CANTIDAD")
    pdf.drawString(col_3, y, "PESOS")

    y -= 3 * mm
    pdf.setLineWidth(0.8)
    pdf.line(col_1, y, table_right, y)

    fuels = ["NAFTA SUPER", "NAFTA INFINIA", "ULTRA DIESEL", "INFINIA DIESEL", "OTROS"]
    voucher_fuel = _safe_text(voucher.fuel_type).upper()
    liters_value = (
        f"{float(voucher.liters):.2f}" if voucher.liters is not None and float(voucher.liters) > 0 else "A completar"
    )

    pdf.setFont("Helvetica", 9)
    for fuel in fuels:
        y -= row_h
        if fuel == "OTROS":
            is_active = voucher_fuel not in fuels[:-1]
        else:
            is_active = voucher_fuel == fuel

        if is_active:
            pdf.setFont("Helvetica-Bold", 9)
        else:
            pdf.setFont("Helvetica", 9)

        pdf.drawString(col_1, y, fuel)
        if is_active:
            pdf.drawString(col_2, y, liters_value)
        pdf.line(col_1, y - 2, table_right, y - 2)

    # Valid-only text for station copy
    y -= 8 * mm
    if not is_internal:
        pdf.setFillColor(colors.HexColor("#b91c1c"))
        pdf.setFont("Helvetica-BoldOblique", 8.5)
        pdf.drawString(
            col_1,
            y,
            f"Valido unicamente para utilizar en estacion {_safe_text(voucher.station)}",
        )
        pdf.setFillColor(colors.black)
        y -= 7 * mm

    # Footer fields
    pdf.setFont("Helvetica", 10)
    pdf.drawString(col_1, y, f"ENTREGADO A: {_safe_text(voucher.employee_name)}")
    y -= 9 * mm

    vehicle_text = ""
    plate_text = ""
    if voucher.vehicle is not None:
        vehicle_text = f"{_safe_text(voucher.vehicle.brand)} {_safe_text(voucher.vehicle.model)}".strip()
        plate_text = _safe_text(voucher.vehicle.plate)

    pdf.drawString(col_1, y, f"VEHICULO: {vehicle_text}")
    pdf.drawRightString(table_right, y, f"PATENTE NRO: {plate_text}")

    y -= 14 * mm
    sig_x1 = margin_x + content_width * 0.58
    sig_x2 = margin_x + content_width - 8
    pdf.line(sig_x1, y, sig_x2, y)
    pdf.setFont("Helvetica-Oblique", 8.5)
    pdf.drawCentredString((sig_x1 + sig_x2) / 2, y - 10, signature_label)

    pdf.showPage()
    pdf.save()

    return buffer.getvalue()
