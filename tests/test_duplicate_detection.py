from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from invoice_buddy.database import init_db
from invoice_buddy.db_models import InvoiceDB
from invoice_buddy.duplicate_detection import find_duplicate_invoice


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


def test_find_duplicate_invoice():
    session = create_test_session()

    invoice = InvoiceDB(
        invoice_number="DUP-001",
        vendor="ACME Supplies",
        invoice_date=date(2026, 9, 25),
        due_date=date(2026, 10, 25),
        currency="INR",
        subtotal=Decimal("10000.00"),
        tax=Decimal("1800.00"),
        total=Decimal("11800.00"),
    )

    session.add(invoice)
    session.commit()

    result = find_duplicate_invoice(
        session,
        "DUP-001",
    )

    assert result is not None
    assert result.invoice_number == "DUP-001"

    session.close()


def test_find_duplicate_invoice_returns_none():
    session = create_test_session()

    result = find_duplicate_invoice(
        session,
        "DOES-NOT-EXIST",
    )

    assert result is None

    session.close()
