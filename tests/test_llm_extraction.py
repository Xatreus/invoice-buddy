from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from invoice_buddy.llm_extraction import (
    LLMInvoice,
    LLMLineItem,
    extract_invoice_with_llm,
)
from invoice_buddy.models import Invoice


def create_sample_llm_invoice() -> LLMInvoice:
    return LLMInvoice(
        invoice_number="LLM-001",
        vendor="ACME Supplies",
        invoice_date="2026-09-21",
        due_date="2026-10-21",
        currency="INR",
        subtotal="10000.00",
        tax="1800.00",
        total="11800.00",
        line_items=[
            LLMLineItem(
                description="Laptop",
                quantity="2",
                unit_price="4000.00",
                amount="8000.00",
            ),
            LLMLineItem(
                description="Keyboard",
                quantity="2",
                unit_price="1000.00",
                amount="2000.00",
            ),
        ],
    )


def test_extract_invoice_with_llm(monkeypatch):
    expected_llm_invoice = create_sample_llm_invoice()

    fake_response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content=expected_llm_invoice.model_dump_json())
            )
        ]
    )

    class FakeCompletions:
        def create(self, **kwargs):
            assert kwargs["model"] == "openai/gpt-oss-20b"
            assert kwargs["temperature"] == 0
            assert kwargs["response_format"] == {"type": "json_object"}
            assert len(kwargs["messages"]) == 2

            return fake_response

    class FakeOpenAI:
        def __init__(self, api_key, base_url):
            assert api_key == "test-api-key"
            assert base_url == "https://integrate.api.nvidia.com/v1"

            self.chat = SimpleNamespace(completions=FakeCompletions())

    monkeypatch.setenv("NVIDIA_API_KEY", "test-api-key")

    monkeypatch.setattr(
        "invoice_buddy.llm_extraction.OpenAI",
        FakeOpenAI,
    )

    result = extract_invoice_with_llm(
        "Invoice Number: LLM-001\nVendor: ACME Supplies",
    )

    assert isinstance(result, Invoice)
    assert result.invoice_number == "LLM-001"
    assert result.vendor == "ACME Supplies"
    assert result.invoice_date == date(2026, 9, 21)
    assert result.total == Decimal("11800.00")
    assert len(result.line_items) == 2
