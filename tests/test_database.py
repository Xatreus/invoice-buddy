from datetime import date
from decimal import Decimal

from sqlalchemy import inspect, text

from invoice_buddy.database import SessionLocal, engine, init_db
from invoice_buddy.db_models import InvoiceDB, LineItemDB
from invoice_buddy.repositories import (
    create_invoice,
    delete_invoice,
    get_invoice,
    get_invoice_by_number,
    list_invoices,
)


def test_database_connection():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))

    assert result.scalar() == 1


def test_init_db_creates_tables():
    init_db()

    inspector = inspect(engine)
    tables = inspector.get_table_names()

    assert "invoices" in tables
    assert "line_items" in tables


def test_create_invoice():
    init_db()

    session = SessionLocal()

    try:
        invoice = InvoiceDB(
            invoice_number="TEST-001",
            vendor="Test Vendor",
            invoice_date=date(2026, 9, 21),
            due_date=date(2026, 10, 21),
            currency="INR",
            subtotal=Decimal("1000.00"),
            tax=Decimal("180.00"),
            total=Decimal("1180.00"),
        )

        invoice.line_items.append(
            LineItemDB(
                description="Test Item",
                quantity=Decimal("2"),
                unit_price=Decimal("500.00"),
                amount=Decimal("1000.00"),
            )
        )

        created = create_invoice(session, invoice)

        assert created.id is not None
        assert created.invoice_number == "TEST-001"
        assert len(created.line_items) == 1

    finally:
        session.close()


def test_get_invoice():
    init_db()

    session = SessionLocal()

    try:
        invoice = InvoiceDB(
            invoice_number="TEST-002",
            vendor="Another Vendor",
            invoice_date=date(2026, 9, 21),
            currency="INR",
            subtotal=Decimal("500.00"),
            tax=Decimal("90.00"),
            total=Decimal("590.00"),
        )

        invoice.line_items.append(
            LineItemDB(
                description="Another Item",
                quantity=Decimal("1"),
                unit_price=Decimal("500.00"),
                amount=Decimal("500.00"),
            )
        )

        created = create_invoice(session, invoice)

        result = get_invoice(session, created.id)

        assert result is not None
        assert result.invoice_number == "TEST-002"
        assert result.vendor == "Another Vendor"
        assert len(result.line_items) == 1

    finally:
        session.close()


def test_get_invoice_by_number():
    init_db()

    session = SessionLocal()

    try:
        invoice = InvoiceDB(
            invoice_number="INV-100",
            vendor="ACME Corp",
            invoice_date=date(2026, 9, 21),
            currency="INR",
            subtotal=Decimal("2000.00"),
            tax=Decimal("360.00"),
            total=Decimal("2360.00"),
        )

        created = create_invoice(session, invoice)

        result = get_invoice_by_number(
            session,
            created.invoice_number,
        )

        assert result is not None
        assert result.id == created.id
        assert result.vendor == "ACME Corp"

    finally:
        session.close()


def test_list_invoices():
    init_db()

    session = SessionLocal()

    try:
        invoice_one = InvoiceDB(
            invoice_number="LIST-001",
            vendor="Vendor A",
            invoice_date=date(2026, 9, 21),
            currency="INR",
            subtotal=Decimal("100.00"),
            tax=Decimal("18.00"),
            total=Decimal("118.00"),
        )

        invoice_two = InvoiceDB(
            invoice_number="LIST-002",
            vendor="Vendor B",
            invoice_date=date(2026, 9, 21),
            currency="INR",
            subtotal=Decimal("200.00"),
            tax=Decimal("36.00"),
            total=Decimal("236.00"),
        )

        create_invoice(session, invoice_one)
        create_invoice(session, invoice_two)

        invoices = list_invoices(session)

        invoice_numbers = {invoice.invoice_number for invoice in invoices}

        assert "LIST-001" in invoice_numbers
        assert "LIST-002" in invoice_numbers

    finally:
        session.close()


def test_delete_invoice():
    init_db()

    session = SessionLocal()

    try:
        invoice = InvoiceDB(
            invoice_number="DELETE-001",
            vendor="Delete Vendor",
            invoice_date=date(2026, 9, 21),
            currency="INR",
            subtotal=Decimal("100.00"),
            tax=Decimal("18.00"),
            total=Decimal("118.00"),
        )

        created = create_invoice(session, invoice)

        deleted = delete_invoice(
            session,
            created.id,
        )

        assert deleted is True
        assert get_invoice(session, created.id) is None

    finally:
        session.close()


def test_delete_nonexistent_invoice():
    init_db()

    session = SessionLocal()

    try:
        deleted = delete_invoice(session, 999999)

        assert deleted is False

    finally:
        session.close()
