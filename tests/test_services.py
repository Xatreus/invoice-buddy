from decimal import Decimal

from invoice_buddy.models import LineItem
from invoice_buddy.services import (
    calculate_subtotal,
    calculate_tax,
    calculate_total,
    round_money,
)


def test_calculate_subtotal_with_one_line_item():
    line_items = [
        LineItem(
            description="Laptop",
            quantity=Decimal(2),
            unit_price=Decimal("50000.00"),
            amount=Decimal("100000.00"),
        )
    ]

    result = calculate_subtotal(line_items)

    assert result == Decimal("100000.00")


def test_calculate_subtotal_with_multiple_line_items():
    line_items = [
        LineItem(
            description="Laptop",
            quantity=Decimal(2),
            unit_price=Decimal("50000.00"),
            amount=Decimal("100000.00"),
        ),
        LineItem(
            description="Mouse",
            quantity=Decimal(2),
            unit_price=Decimal("1000.00"),
            amount=Decimal("2000.00"),
        ),
    ]

    result = calculate_subtotal(line_items)

    assert result == Decimal("102000.00")


def test_calculate_subtotal_with_no_line_items():
    line_items = []

    result = calculate_subtotal(line_items)

    assert result == Decimal("0.00")


def test_calculate_tax():
    subtotal = Decimal("1000.00")
    tax_rate = Decimal(18)

    result = calculate_tax(subtotal, tax_rate)

    assert result == Decimal("180.00")


def test_calculate_tax_with_zero_rate():
    subtotal = Decimal("1000.00")
    tax_rate = Decimal(0)

    result = calculate_tax(subtotal, tax_rate)

    assert result == Decimal("0.00")


def test_calculate_total():
    subtotal = Decimal("1000.00")
    tax = Decimal("180.00")

    result = calculate_total(subtotal, tax)

    assert result == Decimal("1180.00")


def test_round_money():
    value = Decimal("179.9982")

    result = round_money(value)

    assert result == Decimal("180.00")


def test_round_money_rounds_half_up():
    value = Decimal("10.125")

    result = round_money(value)

    assert result == Decimal("10.13")


def test_calculate_tax_rounds_to_two_decimal_places():
    subtotal = Decimal("999.99")
    tax_rate = Decimal(18)

    result = calculate_tax(subtotal, tax_rate)

    assert result == Decimal("180.00")
