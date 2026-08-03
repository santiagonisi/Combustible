from datetime import date

from src.services.voucher_service import normalize_voucher_payload


def test_normalize_voucher_payload_converts_blank_liters_to_zero():
    payload = {
        "issue_date": date(2024, 1, 15),
        "employee_name": "  Ana Perez ",
        "area": "  Mantenimiento ",
        "vehicle_id": "5",
        "fuel_type": " Nafta Super ",
        "liters": "",
        "station": "  YPF ",
        "notes": "   ",
    }

    normalized = normalize_voucher_payload(payload)

    assert normalized["employee_name"] == "Ana Perez"
    assert normalized["area"] == "Mantenimiento"
    assert normalized["vehicle_id"] == 5
    assert normalized["fuel_type"] == "Nafta Super"
    assert normalized["liters"] == 0.0
    assert normalized["station"] == "YPF"
    assert normalized["notes"] == ""


def test_normalize_voucher_payload_preserves_provided_liters():
    payload = {
        "issue_date": date(2024, 1, 15),
        "employee_name": "Luis",
        "area": "Logistica",
        "vehicle_id": 2,
        "fuel_type": "Diesel",
        "liters": "45.5",
        "station": "Shell",
        "notes": "Sin observaciones",
    }

    normalized = normalize_voucher_payload(payload)

    assert normalized["liters"] == 45.5
    assert normalized["notes"] == "Sin observaciones"
