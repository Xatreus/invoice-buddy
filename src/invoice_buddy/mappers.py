from invoice_buddy.db_models import InvoiceDB, LineItemDB
from invoice_buddy.models import Invoice, LineItem


def invoice_to_db(invoice: Invoice) -> InvoiceDB:
    db_invoice = InvoiceDB(
        invoice_number=invoice.invoice_number,
        vendor=invoice.vendor,
        invoice_date=invoice.invoice_date,
        due_date=invoice.due_date,
        currency=invoice.currency,
        subtotal=invoice.subtotal,
        tax=invoice.tax,
        total=invoice.total,
    )

    for item in invoice.line_items:
        db_invoice.line_items.append(
            LineItemDB(
                description=item.description,
                quantity=item.quantity,
                unit_price=item.unit_price,
                amount=item.amount,
            )
        )

    return db_invoice


def invoice_from_db(db_invoice: InvoiceDB) -> Invoice:
    line_items = [
        LineItem(
            description=item.description,
            quantity=item.quantity,
            unit_price=item.unit_price,
            amount=item.amount,
        )
        for item in db_invoice.line_items
    ]

    return Invoice(
        invoice_number=db_invoice.invoice_number,
        vendor=db_invoice.vendor,
        invoice_date=db_invoice.invoice_date,
        due_date=db_invoice.due_date,
        currency=db_invoice.currency,
        subtotal=db_invoice.subtotal,
        tax=db_invoice.tax,
        total=db_invoice.total,
        line_items=line_items,
    )
