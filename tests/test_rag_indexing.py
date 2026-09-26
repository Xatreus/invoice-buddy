from pathlib import Path

from invoice_buddy.rag import (
    index_invoice_text,
    search_invoice_text,
)


def test_index_invoice_text(monkeypatch, tmp_path: Path):
    fake_embeddings = [
        [1.0, 0.0, 0.0],
        [0.9, 0.1, 0.0],
    ]

    monkeypatch.setattr(
        "invoice_buddy.rag.embed_texts",
        lambda texts: fake_embeddings[: len(texts)],
    )

    monkeypatch.setattr(
        "invoice_buddy.rag.add_documents",
        lambda **kwargs: None,
    )

    text = (
        "AWS provides cloud hosting services. "
        "Monthly compute usage is billed separately. "
        "Storage charges are included on the invoice."
    )

    count = index_invoice_text(
        invoice_number="INV-001",
        vendor="AWS",
        text=text,
    )

    assert count == 1


def test_search_invoice_text(monkeypatch):
    monkeypatch.setattr(
        "invoice_buddy.rag.embed_query",
        lambda query: [1.0, 0.0, 0.0],
    )

    fake_results = [
        {
            "id": "INV-001-chunk-0",
            "document": "AWS cloud hosting services",
            "metadata": {
                "invoice_number": "INV-001",
                "vendor": "AWS",
            },
            "distance": 0.1,
        }
    ]

    monkeypatch.setattr(
        "invoice_buddy.rag.search_documents",
        lambda query_embedding, n_results, where=None: fake_results,
    )

    results = search_invoice_text(
        query="cloud hosting",
        n_results=5,
    )

    assert len(results) == 1
    assert results[0]["metadata"]["vendor"] == "AWS"
