from datetime import date
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from invoice_buddy.database import Base
from invoice_buddy.db_models import InvoiceDB
from invoice_buddy.tools.anomaly_tools import (
    detect_anomalies_tool,
)


def create_test_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    Base.metadata.create_all(engine)

    session_factory = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    return session_factory()


def test_detect_anomalies_tool():
    session = create_test_session()

    invoice = InvoiceDB(
        invoice_number="ANOM-TOOL-001",
        vendor="ACME Supplies",
        invoice_date=date(2026, 9, 22),
        due_date=date(2026, 10, 22),
        currency="INR",
        subtotal=Decimal("150000.00"),
        tax=Decimal("0.00"),
        total=Decimal("150000.00"),
    )

    session.add(invoice)
    session.commit()

    result = detect_anomalies_tool(
        session,
        large_invoice_threshold="100000.00",
    )

    assert len(result) == 1
    assert result[0]["invoice_number"] == "ANOM-TOOL-001"
    assert result[0]["vendor"] == "ACME Supplies"
    assert result[0]["anomaly_type"] == "large_invoice"

    session.close()
