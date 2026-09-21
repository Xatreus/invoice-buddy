from datetime import date
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from invoice_buddy.analytics import (
    average_invoice_value,
    invoice_count,
    invoices_between_dates,
    largest_invoice,
    overdue_invoices,
    spend_by_currency,
    spend_by_vendor,
    total_spend,
    vendor_invoice_history,
)
from invoice_buddy.database import init_db
from invoice_buddy.db_models import InvoiceDB
from invoice_buddy.repositories import create_invoice


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


def test_invoice_count():
    test_engine, session_factory = create_test_database()
    session = session_factory()

    try:
        invoice_one = InvoiceDB(
            invoice_number="COUNT-001",
            vendor="Vendor A",
            invoice_date=date(2026, 9, 21),
            currency="INR",
            subtotal=Decimal("1000.00"),
            tax=Decimal("180.00"),
            total=Decimal("1180.00"),
        )

        invoice_two = InvoiceDB(
            invoice_number="COUNT-002",
            vendor="Vendor B",
            invoice_date=date(2026, 9, 21),
            currency="INR",
            subtotal=Decimal("2000.00"),
            tax=Decimal("360.00"),
            total=Decimal("2360.00"),
        )

        create_invoice(session, invoice_one)
        create_invoice(session, invoice_two)

        assert invoice_count(session) == 2

    finally:
        session.close()
        test_engine.dispose()


def test_total_spend():
    test_engine, session_factory = create_test_database()
    session = session_factory()

    try:
        invoice_one = InvoiceDB(
            invoice_number="SPEND-001",
            vendor="Vendor A",
            invoice_date=date(2026, 9, 21),
            currency="INR",
            subtotal=Decimal("1000.00"),
            tax=Decimal("180.00"),
            total=Decimal("1180.00"),
        )

        invoice_two = InvoiceDB(
            invoice_number="SPEND-002",
            vendor="Vendor B",
            invoice_date=date(2026, 9, 21),
            currency="INR",
            subtotal=Decimal("2000.00"),
            tax=Decimal("360.00"),
            total=Decimal("2360.00"),
        )

        create_invoice(session, invoice_one)
        create_invoice(session, invoice_two)

        assert total_spend(session) == Decimal("3540.00")

    finally:
        session.close()
        test_engine.dispose()


def test_average_invoice_value():
    test_engine, session_factory = create_test_database()
    session = session_factory()

    try:
        invoice_one = InvoiceDB(
            invoice_number="AVG-001",
            vendor="Vendor A",
            invoice_date=date(2026, 9, 21),
            currency="INR",
            subtotal=Decimal("1000.00"),
            tax=Decimal("180.00"),
            total=Decimal("1180.00"),
        )

        invoice_two = InvoiceDB(
            invoice_number="AVG-002",
            vendor="Vendor B",
            invoice_date=date(2026, 9, 21),
            currency="INR",
            subtotal=Decimal("2000.00"),
            tax=Decimal("360.00"),
            total=Decimal("2360.00"),
        )

        create_invoice(session, invoice_one)
        create_invoice(session, invoice_two)

        assert average_invoice_value(session) == Decimal("1770.00")

    finally:
        session.close()
        test_engine.dispose()


def test_average_invoice_value_with_no_invoices():
    test_engine, session_factory = create_test_database()
    session = session_factory()

    try:
        assert average_invoice_value(session) == Decimal("0.00")

    finally:
        session.close()
        test_engine.dispose()


def test_largest_invoice():
    test_engine, session_factory = create_test_database()
    session = session_factory()

    try:
        smaller = InvoiceDB(
            invoice_number="LARGE-001",
            vendor="Vendor A",
            invoice_date=date(2026, 9, 21),
            currency="INR",
            subtotal=Decimal("1000.00"),
            tax=Decimal("180.00"),
            total=Decimal("1180.00"),
        )

        larger = InvoiceDB(
            invoice_number="LARGE-002",
            vendor="Vendor B",
            invoice_date=date(2026, 9, 21),
            currency="INR",
            subtotal=Decimal("5000.00"),
            tax=Decimal("900.00"),
            total=Decimal("5900.00"),
        )

        create_invoice(session, smaller)
        create_invoice(session, larger)

        result = largest_invoice(session)

        assert result is not None
        assert result.invoice_number == "LARGE-002"
        assert result.total == Decimal("5900.00")

    finally:
        session.close()
        test_engine.dispose()


def test_invoice_count_with_no_invoices():
    test_engine, session_factory = create_test_database()
    session = session_factory()

    try:
        assert invoice_count(session) == 0

    finally:
        session.close()
        test_engine.dispose()


def test_total_spend_with_no_invoices():
    test_engine, session_factory = create_test_database()
    session = session_factory()

    try:
        assert total_spend(session) == Decimal(0)

    finally:
        session.close()
        test_engine.dispose()


def test_spend_by_vendor():
    test_engine, session_factory = create_test_database()
    session = session_factory()

    try:
        invoice_one = InvoiceDB(
            invoice_number="VENDOR-SPEND-001",
            vendor="ACME",
            invoice_date=date(2026, 9, 1),
            currency="INR",
            subtotal=Decimal("1000.00"),
            tax=Decimal("180.00"),
            total=Decimal("1180.00"),
        )

        invoice_two = InvoiceDB(
            invoice_number="VENDOR-SPEND-002",
            vendor="ACME",
            invoice_date=date(2026, 9, 2),
            currency="INR",
            subtotal=Decimal("2000.00"),
            tax=Decimal("360.00"),
            total=Decimal("2360.00"),
        )

        invoice_three = InvoiceDB(
            invoice_number="VENDOR-SPEND-003",
            vendor="OTHER",
            invoice_date=date(2026, 9, 3),
            currency="INR",
            subtotal=Decimal("500.00"),
            tax=Decimal("90.00"),
            total=Decimal("590.00"),
        )

        create_invoice(session, invoice_one)
        create_invoice(session, invoice_two)
        create_invoice(session, invoice_three)

        result = spend_by_vendor(session)

        assert result["ACME"] == Decimal("3540.00")
        assert result["OTHER"] == Decimal("590.00")

    finally:
        session.close()
        test_engine.dispose()


def test_spend_by_currency():
    test_engine, session_factory = create_test_database()
    session = session_factory()

    try:
        invoice_one = InvoiceDB(
            invoice_number="CURRENCY-SPEND-001",
            vendor="Vendor A",
            invoice_date=date(2026, 9, 1),
            currency="INR",
            subtotal=Decimal("1000.00"),
            tax=Decimal("180.00"),
            total=Decimal("1180.00"),
        )

        invoice_two = InvoiceDB(
            invoice_number="CURRENCY-SPEND-002",
            vendor="Vendor B",
            invoice_date=date(2026, 9, 2),
            currency="USD",
            subtotal=Decimal("200.00"),
            tax=Decimal("36.00"),
            total=Decimal("236.00"),
        )

        create_invoice(session, invoice_one)
        create_invoice(session, invoice_two)

        result = spend_by_currency(session)

        assert result["INR"] == Decimal("1180.00")
        assert result["USD"] == Decimal("236.00")

    finally:
        session.close()
        test_engine.dispose()


def test_invoices_between_dates():
    test_engine, session_factory = create_test_database()
    session = session_factory()

    try:
        invoice_one = InvoiceDB(
            invoice_number="DATE-001",
            vendor="Vendor A",
            invoice_date=date(2026, 9, 5),
            currency="INR",
            subtotal=Decimal("100.00"),
            tax=Decimal("18.00"),
            total=Decimal("118.00"),
        )

        invoice_two = InvoiceDB(
            invoice_number="DATE-002",
            vendor="Vendor B",
            invoice_date=date(2026, 9, 15),
            currency="INR",
            subtotal=Decimal("200.00"),
            tax=Decimal("36.00"),
            total=Decimal("236.00"),
        )

        invoice_three = InvoiceDB(
            invoice_number="DATE-003",
            vendor="Vendor C",
            invoice_date=date(2026, 10, 1),
            currency="INR",
            subtotal=Decimal("300.00"),
            tax=Decimal("54.00"),
            total=Decimal("354.00"),
        )

        create_invoice(session, invoice_one)
        create_invoice(session, invoice_two)
        create_invoice(session, invoice_three)

        result = invoices_between_dates(
            session,
            date(2026, 9, 1),
            date(2026, 9, 30),
        )

        assert len(result) == 2
        assert result[0].invoice_number == "DATE-001"
        assert result[1].invoice_number == "DATE-002"

    finally:
        session.close()
        test_engine.dispose()


def test_overdue_invoices():
    test_engine, session_factory = create_test_database()
    session = session_factory()

    try:
        overdue = InvoiceDB(
            invoice_number="OVERDUE-001",
            vendor="Vendor A",
            invoice_date=date(2026, 8, 1),
            due_date=date(2026, 9, 10),
            currency="INR",
            subtotal=Decimal("1000.00"),
            tax=Decimal("180.00"),
            total=Decimal("1180.00"),
        )

        current = InvoiceDB(
            invoice_number="OVERDUE-002",
            vendor="Vendor B",
            invoice_date=date(2026, 9, 1),
            due_date=date(2026, 9, 30),
            currency="INR",
            subtotal=Decimal("2000.00"),
            tax=Decimal("360.00"),
            total=Decimal("2360.00"),
        )

        create_invoice(session, overdue)
        create_invoice(session, current)

        result = overdue_invoices(
            session,
            date(2026, 9, 22),
        )

        assert len(result) == 1
        assert result[0].invoice_number == "OVERDUE-001"

    finally:
        session.close()
        test_engine.dispose()


def test_vendor_invoice_history():
    test_engine, session_factory = create_test_database()
    session = session_factory()

    try:
        invoice_one = InvoiceDB(
            invoice_number="HISTORY-001",
            vendor="ACME",
            invoice_date=date(2026, 9, 1),
            currency="INR",
            subtotal=Decimal("1000.00"),
            tax=Decimal("180.00"),
            total=Decimal("1180.00"),
        )

        invoice_two = InvoiceDB(
            invoice_number="HISTORY-002",
            vendor="ACME",
            invoice_date=date(2026, 9, 10),
            currency="INR",
            subtotal=Decimal("2000.00"),
            tax=Decimal("360.00"),
            total=Decimal("2360.00"),
        )

        invoice_three = InvoiceDB(
            invoice_number="HISTORY-003",
            vendor="OTHER",
            invoice_date=date(2026, 9, 5),
            currency="INR",
            subtotal=Decimal("500.00"),
            tax=Decimal("90.00"),
            total=Decimal("590.00"),
        )

        create_invoice(session, invoice_one)
        create_invoice(session, invoice_two)
        create_invoice(session, invoice_three)

        result = vendor_invoice_history(
            session,
            "ACME",
        )

        assert len(result) == 2
        assert result[0].invoice_number == "HISTORY-001"
        assert result[1].invoice_number == "HISTORY-002"

    finally:
        session.close()
        test_engine.dispose()
