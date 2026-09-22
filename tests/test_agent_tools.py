from datetime import date
from decimal import Decimal

from invoice_buddy.agent import execute_tool
from invoice_buddy.database import Base
from invoice_buddy.db_models import InvoiceDB
from invoice_buddy.tools.registry import registry
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


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


def test_execute_invoice_count_tool():
    session = create_test_session()

    invoice = InvoiceDB(
        invoice_number="AGENT-001",
        vendor="ACME Supplies",
        invoice_date=date(2026, 9, 22),
        due_date=date(2026, 10, 22),
        currency="INR",
        subtotal=Decimal("10000.00"),
        tax=Decimal("1800.00"),
        total=Decimal("11800.00"),
    )

    session.add(invoice)
    session.commit()

    result = execute_tool(
        session,
        "invoice_count",
        {},
    )

    assert result == 1

    session.close()
