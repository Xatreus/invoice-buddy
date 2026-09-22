from pathlib import Path

import fitz

from invoice_buddy.pdf_ingestion import extract_text_from_pdf


def create_test_pdf(file_path: Path) -> None:
    document = fitz.open()

    page = document.new_page()

    page.insert_text(
        (72, 72),
        "Invoice Number: PDF-001\nVendor: ACME Supplies\nTotal: 11800.00",
    )

    document.save(file_path)
    document.close()


def test_extract_text_from_pdf(tmp_path):
    pdf_path = tmp_path / "invoice.pdf"

    create_test_pdf(pdf_path)

    result = extract_text_from_pdf(pdf_path)

    assert "Invoice Number: PDF-001" in result
    assert "Vendor: ACME Supplies" in result
    assert "Total: 11800.00" in result


def test_extract_text_from_multi_page_pdf(tmp_path):
    pdf_path = tmp_path / "multi_page_invoice.pdf"

    document = fitz.open()

    page_one = document.new_page()
    page_one.insert_text(
        (72, 72),
        "Invoice Number: PDF-002",
    )

    page_two = document.new_page()
    page_two.insert_text(
        (72, 72),
        "Total: 25000.00",
    )

    document.save(pdf_path)
    document.close()

    result = extract_text_from_pdf(pdf_path)

    assert "Invoice Number: PDF-002" in result
    assert "Total: 25000.00" in result


def test_extract_text_from_empty_pdf(tmp_path):
    pdf_path = tmp_path / "empty.pdf"

    document = fitz.open()
    document.new_page()
    document.save(pdf_path)
    document.close()

    result = extract_text_from_pdf(pdf_path)

    assert result == ""
