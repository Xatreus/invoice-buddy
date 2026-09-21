from sqlalchemy import select
from sqlalchemy.orm import Session

from invoice_buddy.db_models import InvoiceDB


def create_invoice(
    session: Session,
    invoice: InvoiceDB,
) -> InvoiceDB:
    session.add(invoice)
    session.commit()
    session.refresh(invoice)

    return invoice


def get_invoice(
    session: Session,
    invoice_id: int,
) -> InvoiceDB | None:
    return session.get(InvoiceDB, invoice_id)


def get_invoice_by_number(
    session: Session,
    invoice_number: str,
) -> InvoiceDB | None:
    statement = select(InvoiceDB).where(InvoiceDB.invoice_number == invoice_number)

    return session.scalar(statement)


def list_invoices(
    session: Session,
) -> list[InvoiceDB]:
    statement = select(InvoiceDB).order_by(InvoiceDB.id)

    return list(session.scalars(statement).all())


def delete_invoice(
    session: Session,
    invoice_id: int,
) -> bool:
    invoice = session.get(InvoiceDB, invoice_id)

    if invoice is None:
        return False

    session.delete(invoice)
    session.commit()

    return True


def list_invoices_by_vendor(
    session: Session,
    vendor: str,
) -> list[InvoiceDB]:
    statement = (
        select(InvoiceDB).where(InvoiceDB.vendor == vendor).order_by(InvoiceDB.id)
    )

    return list(session.scalars(statement).all())


def list_invoices_by_currency(
    session: Session,
    currency: str,
) -> list[InvoiceDB]:
    statement = (
        select(InvoiceDB).where(InvoiceDB.currency == currency).order_by(InvoiceDB.id)
    )

    return list(session.scalars(statement).all())


def update_invoice(
    session: Session,
    invoice_id: int,
    **updates,
) -> InvoiceDB | None:
    invoice = session.get(InvoiceDB, invoice_id)

    if invoice is None:
        return None

    for field, value in updates.items():
        setattr(invoice, field, value)

    session.commit()
    session.refresh(invoice)

    return invoice
