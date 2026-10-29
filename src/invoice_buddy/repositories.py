from sqlalchemy import select
from sqlalchemy.orm import Session

from invoice_buddy.db_models import InvoiceDB


def create_invoice(session: Session, invoice: InvoiceDB) -> InvoiceDB:
    session.add(invoice)
    session.commit()
    session.refresh(invoice)
    return invoice


def get_invoice(session: Session, invoice_id: int) -> InvoiceDB | None:
    return session.get(InvoiceDB, invoice_id)


def get_invoice_by_number(session: Session, invoice_number: str) -> InvoiceDB | None:
    return session.scalar(select(InvoiceDB).where(InvoiceDB.invoice_number == invoice_number))


def get_invoice_by_document_hash(session: Session, document_hash: str) -> InvoiceDB | None:
    return session.scalar(select(InvoiceDB).where(InvoiceDB.document_hash == document_hash))


def list_invoices(
    session: Session, *, limit: int | None = None, offset: int = 0
) -> list[InvoiceDB]:
    """List invoices in stable order; optionally apply bounded API pagination."""
    if offset < 0:
        raise ValueError("offset cannot be negative.")
    statement = select(InvoiceDB).order_by(InvoiceDB.id)
    if limit is not None:
        if limit < 1:
            raise ValueError("limit must be positive.")
        statement = statement.limit(limit)
    if offset:
        statement = statement.offset(offset)
    return list(session.scalars(statement).all())


def delete_invoice(session: Session, invoice_id: int) -> bool:
    invoice = session.get(InvoiceDB, invoice_id)
    if invoice is None:
        return False
    session.delete(invoice)
    session.commit()
    return True


def list_invoices_by_vendor(session: Session, vendor: str) -> list[InvoiceDB]:
    statement = select(InvoiceDB).where(InvoiceDB.vendor == vendor).order_by(InvoiceDB.id)
    return list(session.scalars(statement).all())


def list_invoices_by_currency(session: Session, currency: str) -> list[InvoiceDB]:
    statement = select(InvoiceDB).where(InvoiceDB.currency == currency).order_by(InvoiceDB.id)
    return list(session.scalars(statement).all())


def update_invoice(
    session: Session, invoice_id: int, **updates
) -> InvoiceDB | None:
    allowed_fields = {
        "invoice_number", "document_hash", "vendor", "invoice_date", "due_date",
        "currency", "subtotal", "tax", "total",
    }
    unknown_fields = set(updates) - allowed_fields
    if unknown_fields:
        raise ValueError(f"Unsupported invoice fields: {', '.join(sorted(unknown_fields))}")
    invoice = session.get(InvoiceDB, invoice_id)
    if invoice is None:
        return None
    for field, value in updates.items():
        setattr(invoice, field, value)
    session.commit()
    session.refresh(invoice)
    return invoice
