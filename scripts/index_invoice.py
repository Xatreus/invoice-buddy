import sys
from pathlib import Path

from invoice_buddy.pdf_ingestion import extract_text_from_pdf
from invoice_buddy.rag import index_invoice_text


def main():
    if len(sys.argv) < 4:
        print(
            "Usage:\n"
            "python scripts/index_invoice.py "
            "<pdf_path> <invoice_number> <vendor>"
        )
        raise SystemExit(1)

    pdf_path = Path(sys.argv[1])
    invoice_number = sys.argv[2]
    vendor = sys.argv[3]

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    print("Extracting PDF text...")

    text = extract_text_from_pdf(pdf_path)

    if not text:
        raise ValueError("No text could be extracted from the PDF.")

    print(f"Extracted {len(text)} characters.")

    print("Creating RAG index...")

    chunk_count = index_invoice_text(
        invoice_number=invoice_number,
        vendor=vendor,
        text=text,
    )

    print()
    print("RAG indexing complete.")
    print(f"Invoice: {invoice_number}")
    print(f"Vendor: {vendor}")
    print(f"Chunks indexed: {chunk_count}")


if __name__ == "__main__":
    main()
