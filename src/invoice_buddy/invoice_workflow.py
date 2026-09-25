from decimal import Decimal
from pathlib import Path

from sqlalchemy.orm import Session

from invoice_buddy.monitoring import monitor_invoices
from invoice_buddy.pdf_import_service import import_invoice_from_pdf


def process_invoice(
    session: Session,
    file_path: str | Path,
    large_invoice_threshold: Decimal = Decimal("100000.00"),
) -> dict:
    invoice = import_invoice_from_pdf(
        session,
        file_path,
    )

    monitoring_result = monitor_invoices(
        session,
        large_invoice_threshold=large_invoice_threshold,
    )

    return {
        "invoice": invoice,
        "monitoring": monitoring_result,
    }
