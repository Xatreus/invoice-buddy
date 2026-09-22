import fitz

document = fitz.open()

page = document.new_page()

page.insert_text(
    (72, 72),
    """INVOICE

Invoice Number: REAL-PDF-001
Vendor: Global Tech Solutions
Invoice Date: 2026-09-22
Due Date: 2026-10-22
Currency: INR
Subtotal: 25000.00
Tax: 4500.00
Total: 29500.00

Item: Monitor
Quantity: 2
Unit Price: 7500.00
Amount: 15000.00

Item: Keyboard
Quantity: 5
Unit Price: 2000.00
Amount: 10000.00
""",
)

document.save("data/real_invoice.pdf")
document.close()

print("Created data/real_invoice.pdf")
