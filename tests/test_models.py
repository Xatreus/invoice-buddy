from datetime import date
from decimal import Decimal

from invoice_buddy.models import Invoice


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
