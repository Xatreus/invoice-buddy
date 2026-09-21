import json
from decimal import Decimal
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from invoice_buddy.database import init_db
from invoice_buddy.import_service import import_invoice_from_json
from invoice_buddy.ingestion import load_invoice_from_json
from invoice_buddy.repositories import get_invoice_by_number


def test_load_invoice_from_json():
    file_path = Path("data/sample_invoice.json")

    invoice = load_invoice_from_json(file_path)

    assert invoice.invoice_number == "INV-1001"
    assert invoice.vendor == "ACME Supplies"
    assert invoice.currency == "INR"
    assert invoice.subtotal == Decimal("10000.00")
    assert invoice.tax == Decimal("1800.00")
    assert invoice.total == Decimal("11800.00")
    assert len(invoice.line_items) == 2


def test_load_invoice_from_json_loads_line_items():
    file_path = Path("data/sample_invoice.json")

    invoice = load_invoice_from_json(file_path)

    assert invoice.line_items[0].description == "Laptop"
    assert invoice.line_items[0].quantity == Decimal(2)
    assert invoice.line_items[0].unit_price == Decimal("4000.00")
    assert invoice.line_items[0].amount == Decimal("8000.00")


def test_load_invoice_from_json_rejects_invalid_total(tmp_path):
    data = {
        "invoice_number": "INVALID-001",
        "vendor": "Bad Vendor",
        "invoice_date": "2026-09-21",
        "currency": "INR",
        "subtotal": "1000.00",
        "tax": "180.00",
        "total": "999.00",
        "line_items": [],
    }

    file_path = tmp_path / "invalid_invoice.json"

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(data, file)

    with pytest.raises(ValueError):
        load_invoice_from_json(file_path)


def test_import_invoice_from_json(tmp_path):
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    session_factory = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
    )

    init_db(test_engine)

    session = session_factory()

    try:
        source = Path("data/sample_invoice.json")

        invoice = import_invoice_from_json(
            session,
            source,
        )

        stored = get_invoice_by_number(
            session,
            "INV-1001",
        )

        assert invoice.invoice_number == "INV-1001"
        assert stored is not None
        assert stored.vendor == "ACME Supplies"
        assert stored.total == Decimal("11800.00")
        assert len(stored.line_items) == 2

    finally:
        session.close()
        test_engine.dispose()
