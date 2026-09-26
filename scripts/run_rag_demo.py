from pathlib import Path

from invoice_buddy.pdf_ingestion import extract_text_from_pdf
from invoice_buddy.rag import (
    format_search_results,
    index_invoice_text,
    search_invoice_text,
)


PDF_PATH = Path("data/real_invoice.pdf")


def main():
    if not PDF_PATH.exists():
        raise FileNotFoundError(f"Invoice PDF not found: {PDF_PATH}")

    print("=" * 60)
    print("INVOICE BUDDY - RAG DEMO")
    print("=" * 60)

    print()
    print("1. Extracting PDF text...")

    text = extract_text_from_pdf(PDF_PATH)

    print(f"Extracted {len(text)} characters.")

    if not text:
        raise ValueError("No text was extracted from the PDF.")

    print()
    print("2. Indexing invoice...")

    chunk_count = index_invoice_text(
        invoice_number="REAL-INVOICE",
        vendor="Unknown",
        text=text,
    )

    print(f"Indexed {chunk_count} chunks.")

    print()
    query = input("3. Ask something about the invoice: ").strip()

    if not query:
        raise ValueError("Query cannot be empty.")

    print()
    print("4. Searching vector database...")

    results = search_invoice_text(
        query=query,
        n_results=5,
    )

    print()
    print("=" * 60)
    print("SEARCH RESULTS")
    print("=" * 60)
    print()

    print(format_search_results(results))


if __name__ == "__main__":
    main()
