from datetime import date
from decimal import Decimal

import pytest

from invoice_buddy.pdf_extraction import (
    extract_field,
    extract_invoice_from_text,
    extract_line_items,
)

INVOICE_TEXT = """Invoice Number: PDF-001
Vendor: ACME Supplies
Invoice Date: 2026-09-21
Due Date: 2026-10-21
Currency: INR
Subtotal: 10000.00
Tax: 1800.00
Total: 11800.00
Item: Laptop
Quantity: 2
Unit Price: 4000.00
Amount: 8000.00
Item: Keyboard
Quantity: 2
Unit Price: 1000.00
Amount: 2000.00
"""


def test_extract_field():
    result = extract_field(
        INVOICE_TEXT,
        "Vendor",
    )

    assert result == "ACME Supplies"


def test_extract_field_missing():
    with pytest.raises(ValueError, match="Missing required field"):
        extract_field(
            INVOICE_TEXT,
            "Customer",
        )


def test_extract_line_items():
    items = extract_line_items(INVOICE_TEXT)

    assert len(items) == 2

    assert items[0].description == "Laptop"
    assert items[0].quantity == Decimal(2)
    assert items[0].unit_price == Decimal("4000.00")
    assert items[0].amount == Decimal("8000.00")

    assert items[1].description == "Keyboard"
    assert items[1].amount == Decimal("2000.00")


def test_extract_invoice_from_text():
    invoice = extract_invoice_from_text(INVOICE_TEXT)

    assert invoice.invoice_number == "PDF-001"
    assert invoice.vendor == "ACME Supplies"
    assert invoice.invoice_date == date(2026, 9, 21)
    assert invoice.due_date == date(2026, 10, 21)
    assert invoice.currency == "INR"

    assert invoice.subtotal == Decimal("10000.00")
    assert invoice.tax == Decimal("1800.00")
    assert invoice.total == Decimal("11800.00")

    assert len(invoice.line_items) == 2


def test_invalid_total_is_rejected():
    invalid_text = INVOICE_TEXT.replace(
        "Total: 11800.00",
        "Total: 12000.00",
    )

    with pytest.raises(
        ValueError,
        match="total must equal subtotal plus tax",
    ):
        extract_invoice_from_text(invalid_text)


def test_invalid_line_item_amount_is_rejected():
    invalid_text = INVOICE_TEXT.replace(
        "Amount: 8000.00",
        "Amount: 9000.00",
    )

    with pytest.raises(
        ValueError,
        match="line item amount must equal quantity multiplied by unit price",
    ):
        extract_invoice_from_text(invalid_text)


def test_invalid_date_is_rejected():
    invalid_text = INVOICE_TEXT.replace(
        "Invoice Date: 2026-09-21",
        "Invoice Date: not-a-date",
    )

    with pytest.raises(
        ValueError,
    ):
        extract_invoice_from_text(invalid_text)
