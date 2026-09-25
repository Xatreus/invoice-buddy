from datetime import date
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from invoice_buddy.database import init_db
from invoice_buddy.db_models import InvoiceDB
from invoice_buddy.invoice_workflow import process_invoice
from invoice_buddy.models import Invoice, LineItem


def create_test_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    session_factory = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    init_db(engine)

    return session_factory()


def test_process_invoice(monkeypatch):
    session = create_test_session()

    invoice = Invoice(
        invoice_number="WORKFLOW-001",
        vendor="ACME Supplies",
        invoice_date=date(2026, 9, 23),
        due_date=date(2026, 10, 23),
        currency="INR",
        subtotal=Decimal("150000.00"),
        tax=Decimal("0.00"),
        total=Decimal("150000.00"),
        line_items=[
            LineItem(
                description="Laptop",
                quantity=Decimal("1"),
                unit_price=Decimal("150000.00"),
                amount=Decimal("150000.00"),
            )
        ],
    )

    def fake_import(session, file_path):
        db_invoice = InvoiceDB(
            invoice_number=invoice.invoice_number,
            vendor=invoice.vendor,
            invoice_date=invoice.invoice_date,
            due_date=invoice.due_date,
            currency=invoice.currency,
            subtotal=invoice.subtotal,
            tax=invoice.tax,
            total=invoice.total,
        )

        session.add(db_invoice)
        session.commit()

        return invoice

    monkeypatch.setattr(
        "invoice_buddy.invoice_workflow.import_invoice_from_pdf",
        fake_import,
    )

    result = process_invoice(
        session,
        "fake.pdf",
        large_invoice_threshold=Decimal("100000.00"),
    )

    assert result["invoice"].invoice_number == "WORKFLOW-001"
    assert result["monitoring"]["anomaly_count"] == 1
    assert result["monitoring"]["anomalies"][0]["anomaly_type"] == "large_invoice"

    session.close()
