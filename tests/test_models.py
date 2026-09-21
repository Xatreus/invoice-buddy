from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from invoice_buddy.models import Invoice, LineItem


def test_invoice_creation():
    invoice = Invoice(
        invoice_number="INV-001",
        vendor="Acme Supplies",
        invoice_date=date(2026, 9, 17),
        due_date=date(2026, 10, 17),
        currency="INR",
        subtotal=Decimal("10000.00"),
        tax=Decimal("1800.00"),
        total=Decimal("11800.00"),
        line_items=[],
    )

    assert invoice.invoice_number == "INV-001"
    assert invoice.vendor == "Acme Supplies"
    assert invoice.total == Decimal("11800.00")


def test_line_item_rejects_zero_quantity():
    with pytest.raises(ValidationError):
        LineItem(
            description="Laptop",
            quantity=Decimal(0),
            unit_price=Decimal(50000),
            amount=Decimal(0),
        )


def test_line_item_rejects_negative_unit_price():
    with pytest.raises(ValidationError):
        LineItem(
            description="Laptop",
            quantity=Decimal(1),
            unit_price=Decimal(-50000),
            amount=Decimal(0),
        )


def test_line_item_rejects_negative_amount():
    with pytest.raises(ValidationError):
        LineItem(
            description="Laptop",
            quantity=Decimal(1),
            unit_price=Decimal(50000),
            amount=Decimal(-50000),
        )


def test_invoice_rejects_negative_subtotal():
    with pytest.raises(ValidationError):
        Invoice(
            invoice_number="INV-002",
            vendor="Bad Vendor",
            invoice_date=date(2026, 9, 17),
            currency="INR",
            subtotal=Decimal("-500.00"),
            tax=Decimal("0.00"),
            total=Decimal("0.00"),
            line_items=[],
        )


def test_invoice_rejects_negative_tax():
    with pytest.raises(ValidationError):
        Invoice(
            invoice_number="INV-003",
            vendor="Bad Vendor",
            invoice_date=date(2026, 9, 17),
            currency="INR",
            subtotal=Decimal("1000.00"),
            tax=Decimal("-100.00"),
            total=Decimal("900.00"),
            line_items=[],
        )


def test_invoice_rejects_negative_total():
    with pytest.raises(ValidationError):
        Invoice(
            invoice_number="INV-004",
            vendor="Bad Vendor",
            invoice_date=date(2026, 9, 17),
            currency="INR",
            subtotal=Decimal("1000.00"),
            tax=Decimal("100.00"),
            total=Decimal("-1100.00"),
            line_items=[],
        )


def test_invoice_rejects_incorrect_total():
    with pytest.raises(ValidationError):
        Invoice(
            invoice_number="INV-005",
            vendor="Bad Vendor",
            invoice_date=date(2026, 9, 17),
            currency="INR",
            subtotal=Decimal("10000.00"),
            tax=Decimal("1800.00"),
            total=Decimal("50000.00"),
            line_items=[],
        )
