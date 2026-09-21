from pathlib import Path

from sqlalchemy.orm import Session

from invoice_buddy.ingestion import load_invoice_from_json
from invoice_buddy.mappers import invoice_to_db
from invoice_buddy.models import Invoice
from invoice_buddy.repositories import create_invoice


def import_invoice_from_json(
    session: Session,
    file_path: str | Path,
) -> Invoice:
    invoice = load_invoice_from_json(file_path)

    db_invoice = invoice_to_db(invoice)

    create_invoice(session, db_invoice)

    return invoice
