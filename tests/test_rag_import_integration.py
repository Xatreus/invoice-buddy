from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock, patch

from invoice_buddy.models import Invoice, LineItem
from invoice_buddy.pdf_import_service import (
    import_invoice_from_pdf,
)


def create_test_invoice() -> Invoice:
    return Invoice(
        invoice_number="INV-RAG-001",
        vendor="AWS",
        invoice_date=date(2026, 9, 26),
        due_date=date(2026, 10, 10),
        currency="USD",
        subtotal=Decimal("100.00"),
        tax=Decimal("18.00"),
        total=Decimal("118.00"),
        line_items=[
            LineItem(
                description="Cloud hosting",
                quantity=Decimal("1"),
                unit_price=Decimal("100.00"),
                amount=Decimal("100.00"),
            )
        ],
    )


def test_import_invoice_indexes_text():
    session = MagicMock()
    invoice = create_test_invoice()

    with (
        patch(
            "invoice_buddy.pdf_import_service.extract_text_from_pdf",
            return_value="AWS cloud hosting services",
        ),
        patch(
            "invoice_buddy.pdf_import_service.extract_invoice_with_llm",
            return_value=invoice,
        ),
        patch(
            "invoice_buddy.pdf_import_service.find_duplicate_invoice",
            return_value=None,
        ),
        patch(
            "invoice_buddy.pdf_import_service.invoice_to_db",
            return_value=MagicMock(),
        ),
        patch(
            "invoice_buddy.pdf_import_service.create_invoice",
        ) as mock_create,
        patch(
            "invoice_buddy.pdf_import_service.index_invoice_text",
        ) as mock_index,
    ):
        result = import_invoice_from_pdf(
            session,
            "invoice.pdf",
        )

    assert result == invoice

    mock_create.assert_called_once()

    mock_index.assert_called_once_with(
        invoice_number="INV-RAG-001",
        vendor="AWS",
        text="AWS cloud hosting services",
    )


def test_duplicate_invoice_is_not_indexed():
    session = MagicMock()

    existing_invoice = MagicMock()

    invoice = create_test_invoice()

    with (
        patch(
            "invoice_buddy.pdf_import_service.extract_text_from_pdf",
            return_value="AWS cloud hosting services",
        ),
        patch(
            "invoice_buddy.pdf_import_service.extract_invoice_with_llm",
            return_value=invoice,
        ),
        patch(
            "invoice_buddy.pdf_import_service.find_duplicate_invoice",
            return_value=existing_invoice,
        ),
        patch(
            "invoice_buddy.pdf_import_service.index_invoice_text",
        ) as mock_index,
    ):
        try:
            import_invoice_from_pdf(
                session,
                "invoice.pdf",
            )
        except ValueError as exc:
            assert str(exc) == ("Invoice INV-RAG-001 already exists.")
        else:
            raise AssertionError("Expected duplicate invoice error.")

    mock_index.assert_not_called()
