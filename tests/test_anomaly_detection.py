from datetime import date
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from invoice_buddy.anomaly_detection import (
    detect_invoice_anomalies,
)
from invoice_buddy.database import Base
from invoice_buddy.db_models import InvoiceDB


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


def create_invoice(
    number: str,
    vendor: str,
    total: str,
) -> InvoiceDB:
    subtotal = (Decimal(total) / Decimal("1.18")).quantize(Decimal("0.01"))

    tax = Decimal(total) - subtotal

    return InvoiceDB(
        invoice_number=number,
        vendor=vendor,
        invoice_date=date(2026, 9, 22),
        due_date=date(2026, 10, 22),
        currency="INR",
        subtotal=subtotal,
        tax=tax,
        total=Decimal(total),
    )


def test_detect_large_invoice():
    session = create_test_session()

    invoice = create_invoice(
        "ANOM-001",
        "ACME Supplies",
        "150000.00",
    )

    session.add(invoice)
    session.commit()

    anomalies = detect_invoice_anomalies(
        session,
        invoice,
    )

    assert len(anomalies) == 1
    assert anomalies[0].anomaly_type == "large_invoice"

    session.close()


def test_detect_vendor_outlier():
    session = create_test_session()

    normal_invoice = create_invoice(
        "NORMAL-001",
        "ACME Supplies",
        "10000.00",
    )

    second_normal_invoice = create_invoice(
        "NORMAL-002",
        "ACME Supplies",
        "12000.00",
    )

    unusual_invoice = create_invoice(
        "ANOM-002",
        "ACME Supplies",
        "50000.00",
    )

    session.add_all(
        [
            normal_invoice,
            second_normal_invoice,
            unusual_invoice,
        ]
    )
    session.commit()

    anomalies = detect_invoice_anomalies(
        session,
        unusual_invoice,
    )

    anomaly_types = {anomaly.anomaly_type for anomaly in anomalies}

    assert "vendor_outlier" in anomaly_types

    session.close()


def test_normal_invoice_has_no_anomalies():
    session = create_test_session()

    invoice = create_invoice(
        "NORMAL-003",
        "ACME Supplies",
        "10000.00",
    )

    session.add(invoice)
    session.commit()

    anomalies = detect_invoice_anomalies(
        session,
        invoice,
    )

    assert anomalies == []

    session.close()
