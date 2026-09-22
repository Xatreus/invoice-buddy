from invoice_buddy.llm_extraction import extract_invoice_with_llm


invoice_text = """Invoice Number: LLM-REAL-001
Vendor: ACME Supplies
Invoice Date: 2026-09-21
Due Date: 2026-10-21
Currency: INR
Subtotal: 10000.00
Tax: 1800.00
Total: 11800.00

Item: Laptop
Quantity: 2
Unit Price: 4000.00
Amount: 8000.00

Item: Keyboard
Quantity: 2
Unit Price: 1000.00
Amount: 2000.00
"""


invoice = extract_invoice_with_llm(invoice_text)

print("Invoice extracted successfully!")
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
    print(f"- {item.description}: {item.quantity} × {item.unit_price} = {item.amount}")
