from pathlib import Path

from sqlalchemy.orm import Session

from invoice_buddy.mappers import invoice_to_db
from invoice_buddy.models import Invoice
from invoice_buddy.pdf_extraction import extract_invoice_from_text
from invoice_buddy.pdf_ingestion import extract_text_from_pdf
from invoice_buddy.repositories import create_invoice


def import_invoice_from_pdf(
    session: Session,
    file_path: str | Path,
) -> Invoice:
    text = extract_text_from_pdf(file_path)

    invoice = extract_invoice_from_text(text)

    db_invoice = invoice_to_db(invoice)

    create_invoice(session, db_invoice)

    return invoice
