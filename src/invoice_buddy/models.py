from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class LineItem(BaseModel):
    description: str
    quantity: Decimal
    unit_price: Decimal
    amount: Decimal


class Invoice(BaseModel):
    invoice_number: str
    vendor: str
    invoice_date: date
    due_date: date | None = None
    currency: str
    subtotal: Decimal
    tax: Decimal
    total: Decimal
    line_items: list[LineItem]


from invoice_buddy.models import Invoice

invoice = Invoice(
    invoice_number="INV-001",
    vendor="Acme Supplies",
    invoice_date="2026-09-17",
    currency="INR",
    subtotal="10000.00",
    tax="1800.00",
    total="11800.00",
    line_items=[],
)


print(type(invoice.invoice_date))
print(type(invoice.total))
