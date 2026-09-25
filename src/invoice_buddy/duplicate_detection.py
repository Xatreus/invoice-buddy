from sqlalchemy import select
from sqlalchemy.orm import Session

from invoice_buddy.db_models import InvoiceDB


def find_duplicate_invoice(
    session: Session,
    invoice_number: str,
) -> InvoiceDB | None:
    statement = select(InvoiceDB).where(InvoiceDB.invoice_number == invoice_number)

    return session.scalar(statement)
