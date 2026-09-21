from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from invoice_buddy.db_models import InvoiceDB


def invoice_count(session: Session) -> int:
    statement = select(func.count(InvoiceDB.id))

    return session.scalar(statement) or 0


def total_spend(session: Session) -> Decimal:
    statement = select(func.coalesce(func.sum(InvoiceDB.total), 0))

    result = session.scalar(statement)

    return Decimal(str(result))


def average_invoice_value(session: Session) -> Decimal:
    statement = select(func.avg(InvoiceDB.total))
    result = session.scalar(statement)

    if result is None:
        return Decimal("0.00")

    return Decimal(str(result)).quantize(Decimal("0.01"))


def largest_invoice(session: Session) -> InvoiceDB | None:
    statement = select(InvoiceDB).order_by(InvoiceDB.total.desc()).limit(1)

    return session.scalar(statement)


def spend_by_vendor(
    session: Session,
) -> dict[str, Decimal]:
    statement = (
        select(
            InvoiceDB.vendor,
            func.sum(InvoiceDB.total),
        )
        .group_by(InvoiceDB.vendor)
        .order_by(func.sum(InvoiceDB.total).desc())
    )

    results = session.execute(statement).all()

    return {vendor: Decimal(str(total)) for vendor, total in results}


def spend_by_currency(
    session: Session,
) -> dict[str, Decimal]:
    statement = (
        select(
            InvoiceDB.currency,
            func.sum(InvoiceDB.total),
        )
        .group_by(InvoiceDB.currency)
        .order_by(InvoiceDB.currency)
    )

    results = session.execute(statement).all()

    return {currency: Decimal(str(total)) for currency, total in results}


def invoices_between_dates(
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


def overdue_invoices(
    session: Session,
    as_of: date,
) -> list[InvoiceDB]:
    statement = (
        select(InvoiceDB)
        .where(
            InvoiceDB.due_date.is_not(None),
            InvoiceDB.due_date < as_of,
        )
        .order_by(InvoiceDB.due_date, InvoiceDB.id)
    )

    return list(session.scalars(statement).all())


def vendor_invoice_history(
    session: Session,
    vendor: str,
) -> list[InvoiceDB]:
    statement = (
        select(InvoiceDB)
        .where(InvoiceDB.vendor == vendor)
        .order_by(
            InvoiceDB.invoice_date,
            InvoiceDB.id,
        )
    )

    return list(session.scalars(statement).all())
