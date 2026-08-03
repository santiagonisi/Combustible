from pathlib import Path

from openpyxl import Workbook


def export_vouchers_to_excel(vouchers: list[dict], output_path: str | Path | None = None) -> Path:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Vouchers"

    headers = [
        "Nro Vale",
        "Fecha",
        "Responsable",
        "Area",
        "Vehiculo",
        "Combustible",
        "Litros",
        "Estacion",
        "Observaciones",
    ]
    sheet.append(headers)

    for voucher in vouchers:
        sheet.append(
            [
                voucher.get("serial_number", ""),
                voucher.get("issue_date", ""),
                voucher.get("employee_name", ""),
                voucher.get("area", ""),
                voucher.get("vehicle_id", ""),
                voucher.get("fuel_type", ""),
                voucher.get("liters", ""),
                voucher.get("station", ""),
                voucher.get("notes", ""),
            ]
        )

    output = Path(output_path or "exports/vales.xlsx")
    output.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(output)
    return output
