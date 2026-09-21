from datetime import date
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from invoice_buddy.database import init_db
from invoice_buddy.db_models import InvoiceDB
from invoice_buddy.repositories import create_invoice
from invoice_buddy.tools.analytics_tools import (
    average_invoice_value_tool,
    invoice_count_tool,
    largest_invoice_tool,
    spend_by_currency_tool,
    spend_by_vendor_tool,
    total_spend_tool,
)
from invoice_buddy.tools.invoice_tools import (
    get_invoice_by_number_tool,
    get_invoice_tool,
    search_invoices_tool,
)


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


def create_sample_invoice(session):
    invoice = InvoiceDB(
        invoice_number="TOOL-001",
        vendor="ACME",
        invoice_date=date(2026, 9, 21),
        due_date=date(2026, 10, 21),
        currency="INR",
        subtotal=Decimal("10000.00"),
        tax=Decimal("1800.00"),
        total=Decimal("11800.00"),
    )

    return create_invoice(session, invoice)


def test_get_invoice_tool():
    test_engine, session_factory = create_test_database()
    session = session_factory()

    try:
        invoice = create_sample_invoice(session)

        result = get_invoice_tool(
            session,
            invoice.id,
        )

        assert result is not None
        assert result["invoice_number"] == "TOOL-001"
        assert result["vendor"] == "ACME"
        assert result["total"] == "11800.00"

    finally:
        session.close()
        test_engine.dispose()


def test_get_invoice_by_number_tool():
    test_engine, session_factory = create_test_database()
    session = session_factory()

    try:
        create_sample_invoice(session)

        result = get_invoice_by_number_tool(
            session,
            "TOOL-001",
        )

        assert result is not None
        assert result["invoice_number"] == "TOOL-001"

    finally:
        session.close()
        test_engine.dispose()


def test_search_invoices_tool():
    test_engine, session_factory = create_test_database()
    session = session_factory()

    try:
        create_sample_invoice(session)

        result = search_invoices_tool(
            session,
            vendor="ACME",
        )

        assert len(result) == 1
        assert result[0]["invoice_number"] == "TOOL-001"

    finally:
        session.close()
        test_engine.dispose()


def test_invoice_count_tool():
    test_engine, session_factory = create_test_database()
    session = session_factory()

    try:
        create_sample_invoice(session)

        assert invoice_count_tool(session) == 1

    finally:
        session.close()
        test_engine.dispose()


def test_total_spend_tool():
    test_engine, session_factory = create_test_database()
    session = session_factory()

    try:
        create_sample_invoice(session)

        result = total_spend_tool(session)

        assert result["total_spend"] == "11800.00"

    finally:
        session.close()
        test_engine.dispose()


def test_average_invoice_value_tool():
    test_engine, session_factory = create_test_database()
    session = session_factory()

    try:
        create_sample_invoice(session)

        result = average_invoice_value_tool(session)

        assert result["average_invoice_value"] == "11800.00"

    finally:
        session.close()
        test_engine.dispose()


def test_largest_invoice_tool():
    test_engine, session_factory = create_test_database()
    session = session_factory()

    try:
        create_sample_invoice(session)

        result = largest_invoice_tool(session)

        assert result is not None
        assert result["invoice_number"] == "TOOL-001"
        assert result["total"] == "11800.00"

    finally:
        session.close()
        test_engine.dispose()


def test_spend_by_vendor_tool():
    test_engine, session_factory = create_test_database()
    session = session_factory()

    try:
        create_sample_invoice(session)

        result = spend_by_vendor_tool(session)

        assert result["ACME"] == "11800.00"

    finally:
        session.close()
        test_engine.dispose()


def test_spend_by_currency_tool():
    test_engine, session_factory = create_test_database()
    session = session_factory()

    try:
        create_sample_invoice(session)

        result = spend_by_currency_tool(session)

        assert result["INR"] == "11800.00"

    finally:
        session.close()
        test_engine.dispose()
