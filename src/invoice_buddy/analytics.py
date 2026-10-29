from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from invoice_buddy.db_models import InvoiceDB


def _require_single_currency(session: Session) -> str | None:
    """Return the sole currency or fail closed when a mixed-currency total is ambiguous."""
    currencies = list(session.scalars(select(InvoiceDB.currency).distinct().limit(2)))
    if len(currencies) > 1:
        raise ValueError(
            "This metric cannot combine multiple currencies. Use spend_by_currency() "
            "or filter the records to a single currency before comparing amounts."
        )
    return currencies[0] if currencies else None


def invoice_count(session: Session) -> int:
    return session.scalar(select(func.count(InvoiceDB.id))) or 0


def total_spend(session: Session) -> Decimal:
    _require_single_currency(session)
    result = session.scalar(select(func.coalesce(func.sum(InvoiceDB.total), 0)))
    return Decimal(str(result))


def average_invoice_value(session: Session) -> Decimal:
    _require_single_currency(session)
    result = session.scalar(select(func.avg(InvoiceDB.total)))
    if result is None:
        return Decimal("0.00")
    return Decimal(str(result)).quantize(Decimal("0.01"))


def largest_invoice(session: Session) -> InvoiceDB | None:
    _require_single_currency(session)
    return session.scalar(select(InvoiceDB).order_by(InvoiceDB.total.desc()).limit(1))


def spend_by_vendor(session: Session) -> dict[str, Decimal]:
    _require_single_currency(session)
    statement = (
        select(InvoiceDB.vendor, func.sum(InvoiceDB.total))
        .group_by(InvoiceDB.vendor)
        .order_by(func.sum(InvoiceDB.total).desc())
    )
    return {
        vendor: Decimal(str(total))
        for vendor, total in session.execute(statement).all()
    }


def spend_by_currency(session: Session) -> dict[str, Decimal]:
    statement = (
        select(InvoiceDB.currency, func.sum(InvoiceDB.total))
        .group_by(InvoiceDB.currency)
        .order_by(InvoiceDB.currency)
    )
    return {
        currency: Decimal(str(total))
        for currency, total in session.execute(statement).all()
    }


def invoices_between_dates(
    session: Session, start_date: date, end_date: date
) -> list[InvoiceDB]:
    if start_date > end_date:
        raise ValueError("start_date must be on or before end_date.")
    statement = (
        select(InvoiceDB)
        .where(InvoiceDB.invoice_date >= start_date, InvoiceDB.invoice_date <= end_date)
        .order_by(InvoiceDB.invoice_date, InvoiceDB.id)
    )
    return list(session.scalars(statement).all())


def overdue_invoices(session: Session, as_of: date) -> list[InvoiceDB]:
    statement = (
        select(InvoiceDB)
        .where(InvoiceDB.due_date.is_not(None), InvoiceDB.due_date < as_of)
        .order_by(InvoiceDB.due_date, InvoiceDB.id)
    )
    return list(session.scalars(statement).all())


def vendor_invoice_history(session: Session, vendor: str) -> list[InvoiceDB]:
    statement = (
        select(InvoiceDB)
        .where(InvoiceDB.vendor == vendor)
        .order_by(InvoiceDB.invoice_date, InvoiceDB.id)
    )
    return list(session.scalars(statement).all())
