from invoice_buddy.rag import (
    format_search_results,
    search_invoice_text,
)


def main():
    query = input("Ask about your invoices: ").strip()

    if not query:
        raise ValueError("Query cannot be empty.")

    results = search_invoice_text(
        query=query,
        n_results=5,
    )

    print()
    print("=" * 60)
    print("RAG RESULTS")
    print("=" * 60)
    print()

    print(format_search_results(results))


if __name__ == "__main__":
    main()
