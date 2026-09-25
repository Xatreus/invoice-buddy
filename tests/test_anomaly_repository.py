from datetime import date
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from invoice_buddy.anomaly_repository import (
    create_anomaly_if_missing,
    list_unresolved_anomalies,
    resolve_anomaly,
)
from invoice_buddy.database import init_db
from invoice_buddy.db_models import InvoiceDB


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


def create_invoice(session):
    invoice = InvoiceDB(
        invoice_number="ANOM-REPO-001",
        vendor="ACME Supplies",
        invoice_date=date(2026, 9, 25),
        due_date=date(2026, 10, 25),
        currency="INR",
        subtotal=Decimal("150000.00"),
        tax=Decimal("0.00"),
        total=Decimal("150000.00"),
    )

    session.add(invoice)
    session.commit()

    return invoice


def test_create_anomaly():
    session = create_test_session()

    invoice = create_invoice(session)

    anomaly = create_anomaly_if_missing(
        session,
        invoice.id,
        "large_invoice",
        "warning",
        "Invoice is unusually large.",
    )

    assert anomaly.id is not None
    assert anomaly.invoice_id == invoice.id
    assert anomaly.anomaly_type == "large_invoice"
    assert anomaly.resolved is False

    session.close()


def test_duplicate_anomaly_is_not_created():
    session = create_test_session()

    invoice = create_invoice(session)

    first = create_anomaly_if_missing(
        session,
        invoice.id,
        "large_invoice",
        "warning",
        "Invoice is unusually large.",
    )

    second = create_anomaly_if_missing(
        session,
        invoice.id,
        "large_invoice",
        "warning",
        "Invoice is unusually large.",
    )

    assert first.id == second.id
    assert len(list_unresolved_anomalies(session)) == 1

    session.close()


def test_resolve_anomaly():
    session = create_test_session()

    invoice = create_invoice(session)

    anomaly = create_anomaly_if_missing(
        session,
        invoice.id,
        "large_invoice",
        "warning",
        "Invoice is unusually large.",
    )

    resolved = resolve_anomaly(
        session,
        anomaly.id,
    )

    assert resolved is not None
    assert resolved.resolved is True
    assert list_unresolved_anomalies(session) == []

    session.close()
