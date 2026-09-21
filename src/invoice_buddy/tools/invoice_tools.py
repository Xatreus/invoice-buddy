from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from invoice_buddy.queries import (
    search_invoices,
    search_invoices_by_date,
    search_invoices_by_vendor_text,
)
from invoice_buddy.repositories import (
    get_invoice,
    get_invoice_by_number,
)


def get_invoice_tool(
    session: Session,
    invoice_id: int,
) -> dict | None:
    invoice = get_invoice(session, invoice_id)

    if invoice is None:
        return None

    return {
        "id": invoice.id,
        "invoice_number": invoice.invoice_number,
        "vendor": invoice.vendor,
        "invoice_date": invoice.invoice_date.isoformat(),
        "due_date": (invoice.due_date.isoformat() if invoice.due_date else None),
        "currency": invoice.currency,
        "subtotal": str(invoice.subtotal),
        "tax": str(invoice.tax),
        "total": str(invoice.total),
    }


def get_invoice_by_number_tool(
    session: Session,
    invoice_number: str,
) -> dict | None:
    invoice = get_invoice_by_number(
        session,
        invoice_number,
    )

    if invoice is None:
        return None

    return {
        "id": invoice.id,
        "invoice_number": invoice.invoice_number,
        "vendor": invoice.vendor,
        "invoice_date": invoice.invoice_date.isoformat(),
        "due_date": (invoice.due_date.isoformat() if invoice.due_date else None),
        "currency": invoice.currency,
        "subtotal": str(invoice.subtotal),
        "tax": str(invoice.tax),
        "total": str(invoice.total),
    }


def search_invoices_tool(
    session: Session,
    vendor: str | None = None,
    currency: str | None = None,
    min_total: Decimal | None = None,
    max_total: Decimal | None = None,
) -> list[dict]:
    invoices = search_invoices(
        session,
        vendor=vendor,
        currency=currency,
        min_total=min_total,
        max_total=max_total,
    )

    return [
        {
            "id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "vendor": invoice.vendor,
            "invoice_date": invoice.invoice_date.isoformat(),
            "currency": invoice.currency,
            "total": str(invoice.total),
        }
        for invoice in invoices
    ]


def search_invoices_by_date_tool(
    session: Session,
    start_date: date,
    end_date: date,
) -> list[dict]:
    invoices = search_invoices_by_date(
        session,
        start_date,
        end_date,
    )

    return [
        {
            "id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "vendor": invoice.vendor,
            "invoice_date": invoice.invoice_date.isoformat(),
            "currency": invoice.currency,
            "total": str(invoice.total),
        }
        for invoice in invoices
    ]


def search_invoices_by_vendor_text_tool(
    session: Session,
    vendor_text: str,
) -> list[dict]:
    invoices = search_invoices_by_vendor_text(
        session,
        vendor_text,
    )

    return [
        {
            "id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "vendor": invoice.vendor,
            "invoice_date": invoice.invoice_date.isoformat(),
            "currency": invoice.currency,
            "total": str(invoice.total),
        }
        for invoice in invoices
    ]
