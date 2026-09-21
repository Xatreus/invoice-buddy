from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from invoice_buddy.db_models import InvoiceDB


def search_invoices(
    session: Session,
    vendor: str | None = None,
    currency: str | None = None,
    min_total: Decimal | None = None,
    max_total: Decimal | None = None,
) -> list[InvoiceDB]:
    statement = select(InvoiceDB)

    if vendor is not None:
        statement = statement.where(InvoiceDB.vendor == vendor)

    if currency is not None:
        statement = statement.where(InvoiceDB.currency == currency)

    if min_total is not None:
        statement = statement.where(InvoiceDB.total >= min_total)

    if max_total is not None:
        statement = statement.where(InvoiceDB.total <= max_total)

    statement = statement.order_by(InvoiceDB.id)

    return list(session.scalars(statement).all())


def search_invoices_by_date(
    session: Session,
    start_date: date,
    end_date: date,
) -> list[InvoiceDB]:
    statement = (
        select(InvoiceDB)
        .where(
            InvoiceDB.invoice_date >= start_date,
            InvoiceDB.invoice_date <= end_date,
        )
        .order_by(InvoiceDB.invoice_date, InvoiceDB.id)
    )

    return list(session.scalars(statement).all())


def search_invoices_by_vendor_text(
    session: Session,
    vendor_text: str,
) -> list[InvoiceDB]:
    statement = (
        select(InvoiceDB)
        .where(InvoiceDB.vendor.ilike(f"%{vendor_text}%"))
        .order_by(InvoiceDB.id)
    )

    return list(session.scalars(statement).all())
