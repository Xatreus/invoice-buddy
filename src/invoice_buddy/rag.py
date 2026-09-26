from invoice_buddy.embeddings import embed_query, embed_texts
from invoice_buddy.vector_store import (
    add_documents,
    search_documents,
)


DEFAULT_CHUNK_SIZE = 180
DEFAULT_CHUNK_OVERLAP = 40
DEFAULT_MAX_DISTANCE = 1.0


def chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if chunk_overlap < 0:
        raise ValueError("chunk_overlap cannot be negative.")

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size.")

    words = text.split()

    if not words:
        return []

    chunks = []
    start = 0
    step = chunk_size - chunk_overlap

    while start < len(words):
        end = min(start + chunk_size, len(words))

        chunk = " ".join(words[start:end]).strip()

        if chunk:
            chunks.append(chunk)

        if end == len(words):
            break

        start += step

    return chunks


def index_invoice_text(
    invoice_number: str,
    vendor: str,
    text: str,
) -> int:
    chunks = chunk_text(text)

    if not chunks:
        return 0

    embeddings = embed_texts(chunks)

    ids = [f"{invoice_number}-chunk-{index}" for index in range(len(chunks))]

    metadatas = [
        {
            "invoice_number": invoice_number,
            "vendor": vendor,
            "chunk_index": index,
        }
        for index in range(len(chunks))
    ]

    add_documents(
        documents=chunks,
        embeddings=embeddings,
        ids=ids,
        metadatas=metadatas,
    )

    return len(chunks)


def search_invoice_text(
    query: str,
    n_results: int = 5,
    min_distance: float = DEFAULT_MAX_DISTANCE,
    invoice_number: str | None = None,
) -> list[dict]:
    if n_results <= 0:
        raise ValueError("n_results must be greater than zero.")

    if min_distance < 0:
        raise ValueError("min_distance cannot be negative.")

    query = query.strip()

    if not query:
        return []

    query_embedding = embed_query(query)

    results = search_documents(
        query_embedding=query_embedding,
        n_results=n_results,
        where=(
            {"invoice_number": invoice_number} if invoice_number is not None else None
        ),
    )

    return [result for result in results if result["distance"] <= min_distance]


def format_search_results(
    results: list[dict],
) -> str:
    if not results:
        return "No relevant invoice information was found."

    sections = []

    for index, result in enumerate(results, start=1):
        metadata = result["metadata"]

        invoice_number = metadata.get(
            "invoice_number",
            "Unknown",
        )

        vendor = metadata.get(
            "vendor",
            "Unknown",
        )

        chunk_index = metadata.get(
            "chunk_index",
            "Unknown",
        )

        sections.append(
            "\n".join(
                [
                    f"Result {index}",
                    f"Source invoice: {invoice_number}",
                    f"Vendor: {vendor}",
                    f"Document chunk: {chunk_index}",
                    f"Relevance distance: {result['distance']:.4f}",
                    f"Content: {result['document']}",
                ]
            )
        )

    return "\n\n".join(sections)
