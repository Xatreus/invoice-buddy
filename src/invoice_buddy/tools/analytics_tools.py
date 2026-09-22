from datetime import date

from sqlalchemy.orm import Session

from invoice_buddy.analytics import (
    average_invoice_value,
    invoice_count,
    invoices_between_dates,
    largest_invoice,
    overdue_invoices,
    spend_by_currency,
    spend_by_vendor,
    total_spend,
    vendor_invoice_history,
)


def invoice_count_tool(session: Session) -> int:
    return invoice_count(session)


def total_spend_tool(
    session: Session,
) -> dict[str, str]:
    return {
        "total_spend": str(total_spend(session)),
    }


def average_invoice_value_tool(
    session: Session,
) -> dict[str, str]:
    return {
        "average_invoice_value": str(average_invoice_value(session)),
    }


def largest_invoice_tool(
    session: Session,
) -> dict | None:
    invoice = largest_invoice(session)

    if invoice is None:
        return None

    return {
        "invoice_number": invoice.invoice_number,
        "vendor": invoice.vendor,
        "currency": invoice.currency,
        "total": str(invoice.total),
    }


def spend_by_vendor_tool(
    session: Session,
) -> dict[str, str]:
    result = spend_by_vendor(session)

    return {vendor: str(total) for vendor, total in result.items()}


def spend_by_currency_tool(
    session: Session,
) -> dict[str, str]:
    result = spend_by_currency(session)

    return {currency: str(total) for currency, total in result.items()}


def invoices_between_dates_tool(
    session: Session,
    start_date: date,
    end_date: date,
) -> list[dict]:
    invoices = invoices_between_dates(
        session,
        start_date,
        end_date,
    )

    return [
        {
            "invoice_number": invoice.invoice_number,
            "vendor": invoice.vendor,
            "invoice_date": invoice.invoice_date.isoformat(),
            "currency": invoice.currency,
            "total": str(invoice.total),
        }
        for invoice in invoices
    ]


def overdue_invoices_tool(
    session: Session,
    as_of: date,
) -> list[dict]:
    invoices = overdue_invoices(
        session,
        as_of,
    )

    return [
        {
            "invoice_number": invoice.invoice_number,
            "vendor": invoice.vendor,
            "due_date": invoice.due_date.isoformat(),
            "currency": invoice.currency,
            "total": str(invoice.total),
        }
        for invoice in invoices
    ]


def vendor_invoice_history_tool(
    session: Session,
    vendor: str,
) -> list[dict]:
    invoices = vendor_invoice_history(
        session,
        vendor,
    )

    return [
        {
            "invoice_number": invoice.invoice_number,
            "vendor": invoice.vendor,
            "invoice_date": invoice.invoice_date.isoformat(),
            "currency": invoice.currency,
            "total": str(invoice.total),
        }
        for invoice in invoices
    ]
