from datetime import date
from decimal import Decimal

import fitz
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from invoice_buddy.database import init_db
from invoice_buddy.pdf_import_service import import_invoice_from_pdf
from invoice_buddy.repositories import get_invoice_by_number


def create_test_database():
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    test_session_factory = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
    )

    init_db(test_engine)

    return test_engine, test_session_factory


def create_invoice_pdf(file_path):
    document = fitz.open()

    page = document.new_page()

    page.insert_text(
        (72, 72),
        "Invoice Number: PDF-IMPORT-001\n"
        "Vendor: ACME Supplies\n"
        "Invoice Date: 2026-09-21\n"
        "Due Date: 2026-10-21\n"
        "Currency: INR\n"
        "Subtotal: 10000.00\n"
        "Tax: 1800.00\n"
        "Total: 11800.00\n"
        "Item: Laptop\n"
        "Quantity: 2\n"
        "Unit Price: 4000.00\n"
        "Amount: 8000.00\n"
        "Item: Keyboard\n"
        "Quantity: 2\n"
        "Unit Price: 1000.00\n"
        "Amount: 2000.00",
    )

    document.save(file_path)
    document.close()


def test_import_invoice_from_pdf(tmp_path):
    _, session_factory = create_test_database()

    pdf_path = tmp_path / "invoice.pdf"

    create_invoice_pdf(pdf_path)

    with session_factory() as session:
        invoice = import_invoice_from_pdf(
            session,
            pdf_path,
        )

        assert invoice.invoice_number == "PDF-IMPORT-001"
        assert invoice.vendor == "ACME Supplies"
        assert invoice.invoice_date == date(2026, 9, 21)
        assert invoice.due_date == date(2026, 10, 21)
        assert invoice.currency == "INR"
        assert invoice.subtotal == Decimal("10000.00")
        assert invoice.tax == Decimal("1800.00")
        assert invoice.total == Decimal("11800.00")

        stored_invoice = get_invoice_by_number(
            session,
            "PDF-IMPORT-001",
        )

        assert stored_invoice is not None
        assert stored_invoice.vendor == "ACME Supplies"
        assert stored_invoice.total == Decimal("11800.00")
        assert len(stored_invoice.line_items) == 2
