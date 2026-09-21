from datetime import date
from decimal import Decimal

from invoice_buddy.database import SessionLocal, init_db
from invoice_buddy.db_models import InvoiceDB
from invoice_buddy.mappers import invoice_from_db, invoice_to_db
from invoice_buddy.models import Invoice, LineItem
from invoice_buddy.repositories import create_invoice


def test_invoice_to_db():
    invoice = Invoice(
        invoice_number="MAP-001",
        vendor="Mapper Vendor",
        invoice_date=date(2026, 9, 21),
        due_date=date(2026, 10, 21),
        currency="INR",
        subtotal=Decimal("1000.00"),
        tax=Decimal("180.00"),
        total=Decimal("1180.00"),
        line_items=[
            LineItem(
                description="Laptop",
                quantity=Decimal(2),
                unit_price=Decimal("500.00"),
                amount=Decimal("1000.00"),
            )
        ],
    )

    db_invoice = invoice_to_db(invoice)

    assert isinstance(db_invoice, InvoiceDB)
    assert db_invoice.invoice_number == "MAP-001"
    assert db_invoice.vendor == "Mapper Vendor"
    assert len(db_invoice.line_items) == 1
    assert db_invoice.line_items[0].description == "Laptop"


def test_invoice_from_db():
    db_invoice = InvoiceDB(
        invoice_number="MAP-002",
        vendor="Database Vendor",
        invoice_date=date(2026, 9, 21),
        currency="INR",
        subtotal=Decimal("500.00"),
        tax=Decimal("90.00"),
        total=Decimal("590.00"),
    )

    invoice = invoice_from_db(db_invoice)

    assert isinstance(invoice, Invoice)
    assert invoice.invoice_number == "MAP-002"
    assert invoice.vendor == "Database Vendor"
    assert invoice.total == Decimal("590.00")


def test_invoice_database_round_trip():
    init_db()

    original = Invoice(
        invoice_number="ROUND-001",
        vendor="Round Trip Vendor",
        invoice_date=date(2026, 9, 21),
        due_date=date(2026, 10, 21),
        currency="INR",
        subtotal=Decimal("1500.00"),
        tax=Decimal("270.00"),
        total=Decimal("1770.00"),
        line_items=[
            LineItem(
                description="Keyboard",
                quantity=Decimal(2),
                unit_price=Decimal("500.00"),
                amount=Decimal("1000.00"),
            ),
            LineItem(
                description="Mouse",
                quantity=Decimal(1),
                unit_price=Decimal("500.00"),
                amount=Decimal("500.00"),
            ),
        ],
    )

    session = SessionLocal()

    try:
        db_invoice = invoice_to_db(original)
        created = create_invoice(session, db_invoice)

        restored = invoice_from_db(created)

        assert restored.invoice_number == original.invoice_number
        assert restored.vendor == original.vendor
        assert restored.invoice_date == original.invoice_date
        assert restored.due_date == original.due_date
        assert restored.currency == original.currency
        assert restored.subtotal == original.subtotal
        assert restored.tax == original.tax
        assert restored.total == original.total
        assert len(restored.line_items) == 2

        assert restored.line_items[0].description == "Keyboard"
        assert restored.line_items[1].description == "Mouse"

    finally:
        session.close()
