from invoice_buddy.database import SessionLocal, init_db
from invoice_buddy.pdf_import_service import import_invoice_from_pdf


init_db()

with SessionLocal() as session:
    invoice = import_invoice_from_pdf(
        session,
        "data/real_invoice.pdf",
    )

    print()
    print("===================================")
    print("REAL PDF IMPORT SUCCESSFUL")
    print("===================================")
    print()
    print(f"Invoice number: {invoice.invoice_number}")
    print(f"Vendor: {invoice.vendor}")
    print(f"Date: {invoice.invoice_date}")
    print(f"Due date: {invoice.due_date}")
    print(f"Currency: {invoice.currency}")
    print(f"Subtotal: {invoice.subtotal}")
    print(f"Tax: {invoice.tax}")
    print(f"Total: {invoice.total}")
    print()
    print("Line items:")

    for item in invoice.line_items:
        print(
            f"- {item.description}: {item.quantity} × {item.unit_price} = {item.amount}"
        )
