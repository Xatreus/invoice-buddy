from datetime import date
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from invoice_buddy.database import init_db
from invoice_buddy.db_models import InvoiceDB
from invoice_buddy.monitoring import monitor_invoices


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


def test_monitor_invoices_detects_large_invoice():
    session = create_test_session()

    invoice = InvoiceDB(
        invoice_number="MONITOR-001",
        vendor="ACME Supplies",
        invoice_date=date(2026, 9, 23),
        due_date=date(2026, 10, 23),
        currency="INR",
        subtotal=Decimal("150000.00"),
        tax=Decimal("0.00"),
        total=Decimal("150000.00"),
    )

    session.add(invoice)
    session.commit()

    result = monitor_invoices(
        session,
        large_invoice_threshold=Decimal("100000.00"),
    )

    assert result["anomaly_count"] == 1
    assert result["anomalies"][0]["invoice_number"] == "MONITOR-001"
    assert result["anomalies"][0]["anomaly_type"] == "large_invoice"

    session.close()
