from pathlib import Path

from sqlalchemy.orm import Session

from invoice_buddy.duplicate_detection import find_duplicate_invoice
from invoice_buddy.llm_extraction import extract_invoice_with_llm
from invoice_buddy.mappers import invoice_to_db
from invoice_buddy.models import Invoice
from invoice_buddy.pdf_ingestion import extract_text_from_pdf
from invoice_buddy.repositories import create_invoice


def import_invoice_from_pdf(
    session: Session,
    file_path: str | Path,
) -> Invoice:
    text = extract_text_from_pdf(file_path)

    invoice = extract_invoice_with_llm(text)

    existing = find_duplicate_invoice(
        session,
        invoice.invoice_number,
    )

    if existing is not None:
        raise ValueError(f"Invoice {invoice.invoice_number} already exists.")

    db_invoice = invoice_to_db(invoice)

    create_invoice(session, db_invoice)

    return invoice
