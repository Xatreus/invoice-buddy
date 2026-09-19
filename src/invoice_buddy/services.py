from decimal import ROUND_HALF_UP, Decimal

from invoice_buddy.models import LineItem


def round_money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_subtotal(line_items: list[LineItem]) -> Decimal:
    subtotal = sum(
        (item.quantity * item.unit_price for item in line_items),
        Decimal("0.00"),
    )

    return round_money(subtotal)


def calculate_tax(subtotal: Decimal, tax_rate: Decimal) -> Decimal:
    tax = subtotal * (tax_rate / Decimal(100))

    return round_money(tax)


def calculate_total(subtotal: Decimal, tax: Decimal) -> Decimal:
    return round_money(subtotal + tax)
