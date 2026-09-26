import pytest

import invoice_buddy.rag as rag


def test_search_invoice_text_returns_relevant_results(monkeypatch):
    monkeypatch.setattr(
        rag,
        "embed_query",
        lambda query: [0.1, 0.2],
    )

    monkeypatch.setattr(
        rag,
        "search_documents",
        lambda query_embedding, n_results, where=None: [
            {
                "document": "AWS hosting charge",
                "metadata": {
                    "invoice_number": "INV-001",
                    "vendor": "AWS",
                    "chunk_index": 0,
                },
                "distance": 0.2,
            }
        ],
    )

    results = rag.search_invoice_text("hosting charge")

    assert len(results) == 1
    assert results[0]["metadata"]["invoice_number"] == "INV-001"


def test_search_invoice_text_filters_irrelevant_results(monkeypatch):
    monkeypatch.setattr(
        rag,
        "embed_query",
        lambda query: [0.1, 0.2],
    )

    monkeypatch.setattr(
        rag,
        "search_documents",
        lambda query_embedding, n_results, where=None: [
            {
                "document": "Relevant invoice information",
                "metadata": {
                    "invoice_number": "INV-001",
                    "vendor": "AWS",
                    "chunk_index": 0,
                },
                "distance": 0.2,
            },
            {
                "document": "Weakly related information",
                "metadata": {
                    "invoice_number": "INV-002",
                    "vendor": "Google",
                    "chunk_index": 0,
                },
                "distance": 1.5,
            },
        ],
    )

    results = rag.search_invoice_text(
        "invoice information",
        min_distance=1.0,
    )

    assert len(results) == 1
    assert results[0]["metadata"]["invoice_number"] == "INV-001"


def test_search_invoice_text_filters_by_invoice_number(monkeypatch):
    monkeypatch.setattr(
        rag,
        "embed_query",
        lambda query: [0.1, 0.2],
    )

    def fake_search_documents(
        query_embedding,
        n_results,
        where=None,
    ):
        assert where == {
            "invoice_number": "INV-001",
        }

        return [
            {
                "document": "AWS payment terms",
                "metadata": {
                    "invoice_number": "INV-001",
                    "vendor": "AWS",
                    "chunk_index": 0,
                },
                "distance": 0.2,
            }
        ]

    monkeypatch.setattr(
        rag,
        "search_documents",
        fake_search_documents,
    )

    results = rag.search_invoice_text(
        "payment terms",
        invoice_number="INV-001",
    )

    assert len(results) == 1
    assert results[0]["metadata"]["invoice_number"] == "INV-001"


def test_search_invoice_text_returns_empty_for_no_query():
    results = rag.search_invoice_text("")

    assert results == []


def test_search_invoice_text_rejects_invalid_n_results():
    with pytest.raises(
        ValueError,
        match="n_results must be greater than zero",
    ):
        rag.search_invoice_text(
            "payment terms",
            n_results=0,
        )


def test_search_invoice_text_rejects_negative_distance():
    with pytest.raises(
        ValueError,
        match="min_distance cannot be negative",
    ):
        rag.search_invoice_text(
            "payment terms",
            min_distance=-1,
        )


def test_search_invoice_text_rejects_whitespace_query():
    results = rag.search_invoice_text("   ")

    assert results == []
