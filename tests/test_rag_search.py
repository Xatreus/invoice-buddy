from unittest.mock import patch

from invoice_buddy.tools.rag_tools import (
    search_invoice_knowledge,
)


def test_rag_tool_returns_relevant_invoice_content():
    fake_results = [
        {
            "id": "INV-001-chunk-0",
            "document": ("AWS cloud hosting and compute services were billed."),
            "metadata": {
                "invoice_number": "INV-001",
                "vendor": "AWS",
                "chunk_index": 0,
            },
            "distance": 0.08,
        }
    ]

    with patch(
        "invoice_buddy.tools.rag_tools.search_invoice_text",
        return_value=fake_results,
    ):
        result = search_invoice_knowledge(
            session=None,
            query="What cloud services were billed?",
        )

    assert "AWS" in result
    assert "cloud hosting" in result
    assert "compute" in result
    assert "INV-001" in result


def test_rag_tool_handles_no_results():
    with patch(
        "invoice_buddy.tools.rag_tools.search_invoice_text",
        return_value=[],
    ):
        result = search_invoice_knowledge(
            session=None,
            query="something completely unrelated",
        )

    assert "No relevant invoice information was found." in result
    assert "UNTRUSTED DATA" in result
    assert "BEGIN UNTRUSTED INVOICE DATA" in result
    assert "END UNTRUSTED INVOICE DATA" in result
