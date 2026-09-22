import re
from datetime import date
from decimal import Decimal

from invoice_buddy.models import Invoice, LineItem


def extract_field(text: str, field_name: str) -> str:
    pattern = rf"^{re.escape(field_name)}:\s*(.+)$"

    match = re.search(
        pattern,
        text,
        flags=re.MULTILINE,
    )

    if match is None:
        raise ValueError(f"Missing required field: {field_name}")

    return match.group(1).strip()


def extract_invoice_from_text(text: str) -> Invoice:
    invoice_number = extract_field(
        text,
        "Invoice Number",
    )

    vendor = extract_field(
        text,
        "Vendor",
    )

    invoice_date = date.fromisoformat(extract_field(text, "Invoice Date"))

    due_date_text = extract_field(
        text,
        "Due Date",
    )

    due_date = date.fromisoformat(due_date_text)

    currency = extract_field(
        text,
        "Currency",
    )

    subtotal = Decimal(extract_field(text, "Subtotal"))

    tax = Decimal(extract_field(text, "Tax"))

    total = Decimal(extract_field(text, "Total"))

    line_items = extract_line_items(text)

    return Invoice(
        invoice_number=invoice_number,
        vendor=vendor,
        invoice_date=invoice_date,
        due_date=due_date,
        currency=currency,
        subtotal=subtotal,
        tax=tax,
        total=total,
        line_items=line_items,
    )


def extract_line_items(text: str) -> list[LineItem]:
    pattern = (
        r"^Item:\s*(?P<description>.+)\n"
        r"Quantity:\s*(?P<quantity>\d+(?:\.\d+)?)\n"
        r"Unit Price:\s*(?P<unit_price>\d+(?:\.\d+)?)\n"
        r"Amount:\s*(?P<amount>\d+(?:\.\d+)?)$"
    )

    matches = re.finditer(
        pattern,
        text,
        flags=re.MULTILINE,
    )

    return [
        LineItem(
            description=match.group("description").strip(),
            quantity=Decimal(match.group("quantity")),
            unit_price=Decimal(match.group("unit_price")),
            amount=Decimal(match.group("amount")),
        )
        for match in matches
    ]
