from sqlalchemy import func
from sqlalchemy.orm import Session

from src.models.monthly_invoice import MonthlyInvoice
from src.schemas.monthly_invoice import MonthlyInvoiceCreate, MonthlyInvoiceSummary, MonthlyInvoiceUpdate


def create_monthly_invoice(db: Session, payload: MonthlyInvoiceCreate) -> MonthlyInvoice:
    invoice = MonthlyInvoice(**payload.model_dump())
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice


def update_monthly_invoice(db: Session, invoice_id: int, payload: MonthlyInvoiceUpdate) -> MonthlyInvoice:
    invoice = db.query(MonthlyInvoice).filter(MonthlyInvoice.id == invoice_id).first()
    if not invoice:
        raise ValueError("Factura mensual no encontrada")

    for field, value in payload.model_dump().items():
        setattr(invoice, field, value)

    db.commit()
    db.refresh(invoice)
    return invoice


def delete_monthly_invoice(db: Session, invoice_id: int) -> None:
    invoice = db.query(MonthlyInvoice).filter(MonthlyInvoice.id == invoice_id).first()
    if not invoice:
        raise ValueError("Factura mensual no encontrada")

    db.delete(invoice)
    db.commit()


def list_monthly_invoices(db: Session, month: str) -> list[MonthlyInvoice]:
    return (
        db.query(MonthlyInvoice)
        .filter(MonthlyInvoice.month == month)
        .order_by(MonthlyInvoice.created_at.desc(), MonthlyInvoice.id.desc())
        .all()
    )


def monthly_invoice_summary(db: Session, month: str) -> MonthlyInvoiceSummary:
    invoices = list_monthly_invoices(db, month)

    totals = (
        db.query(
            func.count(MonthlyInvoice.id),
            func.coalesce(func.sum(MonthlyInvoice.total_vouchers), 0),
            func.coalesce(func.sum(MonthlyInvoice.total_liters), 0.0),
            func.coalesce(func.sum(MonthlyInvoice.total_amount), 0.0),
        )
        .filter(MonthlyInvoice.month == month)
        .one()
    )

    return MonthlyInvoiceSummary(
        month=month,
        total_invoices=int(totals[0] or 0),
        total_vouchers=int(totals[1] or 0),
        total_liters=round(float(totals[2] or 0), 2),
        total_amount=round(float(totals[3] or 0), 2),
        invoices=invoices,
    )
