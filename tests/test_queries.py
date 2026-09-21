from datetime import date
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from invoice_buddy.database import init_db
from invoice_buddy.db_models import InvoiceDB
from invoice_buddy.queries import (
    search_invoices,
    search_invoices_by_date,
    search_invoices_by_vendor_text,
)
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


def create_sample_invoices(session):
    invoices = [
        InvoiceDB(
            invoice_number="QUERY-001",
            vendor="ACME",
            invoice_date=date(2026, 9, 1),
            currency="INR",
            subtotal=Decimal("10000.00"),
            tax=Decimal("1800.00"),
            total=Decimal("11800.00"),
        ),
        InvoiceDB(
            invoice_number="QUERY-002",
            vendor="ACME",
            invoice_date=date(2026, 9, 10),
            currency="USD",
            subtotal=Decimal("2000.00"),
            tax=Decimal("360.00"),
            total=Decimal("2360.00"),
        ),
        InvoiceDB(
            invoice_number="QUERY-003",
            vendor="Microsoft",
            invoice_date=date(2026, 9, 20),
            currency="INR",
            subtotal=Decimal("50000.00"),
            tax=Decimal("9000.00"),
            total=Decimal("59000.00"),
        ),
    ]

    for invoice in invoices:
        create_invoice(session, invoice)


def test_search_invoices_by_vendor():
    test_engine, session_factory = create_test_database()
    session = session_factory()

    try:
        create_sample_invoices(session)

        results = search_invoices(
            session,
            vendor="ACME",
        )

        assert len(results) == 2
        assert results[0].invoice_number == "QUERY-001"
        assert results[1].invoice_number == "QUERY-002"

    finally:
        session.close()
        test_engine.dispose()


def test_search_invoices_by_currency():
    test_engine, session_factory = create_test_database()
    session = session_factory()

    try:
        create_sample_invoices(session)

        results = search_invoices(
            session,
            currency="INR",
        )

        assert len(results) == 2
        assert results[0].invoice_number == "QUERY-001"
        assert results[1].invoice_number == "QUERY-003"

    finally:
        session.close()
        test_engine.dispose()


def test_search_invoices_by_minimum_total():
    test_engine, session_factory = create_test_database()
    session = session_factory()

    try:
        create_sample_invoices(session)

        results = search_invoices(
            session,
            min_total=Decimal("50000.00"),
        )

        assert len(results) == 1
        assert results[0].invoice_number == "QUERY-003"

    finally:
        session.close()
        test_engine.dispose()


def test_search_invoices_by_maximum_total():
    test_engine, session_factory = create_test_database()
    session = session_factory()

    try:
        create_sample_invoices(session)

        results = search_invoices(
            session,
            max_total=Decimal("10000.00"),
        )

        assert len(results) == 1
        assert results[0].invoice_number == "QUERY-002"

    finally:
        session.close()
        test_engine.dispose()


def test_search_invoices_with_multiple_filters():
    test_engine, session_factory = create_test_database()
    session = session_factory()

    try:
        create_sample_invoices(session)

        results = search_invoices(
            session,
            vendor="ACME",
            currency="INR",
            min_total=Decimal("10000.00"),
        )

        assert len(results) == 1
        assert results[0].invoice_number == "QUERY-001"

    finally:
        session.close()
        test_engine.dispose()


def test_search_invoices_with_no_filters():
    test_engine, session_factory = create_test_database()
    session = session_factory()

    try:
        create_sample_invoices(session)

        results = search_invoices(session)

        assert len(results) == 3

    finally:
        session.close()
        test_engine.dispose()


def test_search_invoices_by_date():
    test_engine, session_factory = create_test_database()
    session = session_factory()

    try:
        create_sample_invoices(session)

        results = search_invoices_by_date(
            session,
            date(2026, 9, 5),
            date(2026, 9, 15),
        )

        assert len(results) == 1
        assert results[0].invoice_number == "QUERY-002"

    finally:
        session.close()
        test_engine.dispose()


def test_search_invoices_by_vendor_text():
    test_engine, session_factory = create_test_database()
    session = session_factory()

    try:
        invoice = InvoiceDB(
            invoice_number="TEXT-001",
            vendor="Microsoft Corporation",
            invoice_date=date(2026, 9, 21),
            currency="INR",
            subtotal=Decimal("1000.00"),
            tax=Decimal("180.00"),
            total=Decimal("1180.00"),
        )

        create_invoice(session, invoice)

        results = search_invoices_by_vendor_text(
            session,
            "Microsoft",
        )

        assert len(results) == 1
        assert results[0].vendor == "Microsoft Corporation"

    finally:
        session.close()
        test_engine.dispose()
