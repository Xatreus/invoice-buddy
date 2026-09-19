from decimal import Decimal

from invoice_buddy.models import LineItem


def calculate_subtotal(line_items: list[LineItem]) -> Decimal:
    return sum(
        (item.quantity * item.unit_price for item in line_items),
        Decimal("0.00"),
    )


def calculate_tax(subtotal: Decimal, tax_rate: Decimal) -> Decimal:
    return subtotal * (tax_rate / Decimal(100))


def calculate_total(subtotal: Decimal, tax: Decimal) -> Decimal:
    return subtotal + tax
