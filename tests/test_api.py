from datetime import date
from decimal import Decimal
from types import SimpleNamespace

import fitz
import invoice_buddy.security as security
from fastapi.testclient import TestClient

from invoice_buddy.api import app


TEST_API_KEY = "test-api-key"

AUTH_HEADERS = {
    "X-API-Key": TEST_API_KEY,
}


client = TestClient(app)


def _valid_pdf_bytes() -> bytes:
    """Create a tiny valid PDF so upload tests exercise the import path."""
    with fitz.open() as document:
        document.new_page()
        return document.tobytes()


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "invoice-buddy",
    }


def test_upload_rejects_non_pdf(monkeypatch):
    monkeypatch.setattr(
        security,
        "API_KEY",
        TEST_API_KEY,
    )

    response = client.post(
        "/invoices/upload",
        files={
            "file": (
                "invoice.txt",
                b"not a pdf",
                "text/plain",
            )
        },
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == ("Only PDF files are supported.")


def test_upload_rejects_invalid_pdf_content(monkeypatch):
    monkeypatch.setattr(security, "API_KEY", TEST_API_KEY)

    response = client.post(
        "/invoices/upload",
        files={
            "file": (
                "invoice.pdf",
                b"not really a pdf",
                "application/pdf",
            )
        },
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Uploaded content is not a PDF."


def test_upload_requires_file(monkeypatch):
    monkeypatch.setattr(
        security,
        "API_KEY",
        TEST_API_KEY,
    )

    response = client.post(
        "/invoices/upload",
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 422


def test_upload_imports_invoice(monkeypatch):
    monkeypatch.setattr(
        security,
        "API_KEY",
        TEST_API_KEY,
    )

    fake_invoice = SimpleNamespace(
        invoice_number="INV-TEST-001",
        vendor="Test Vendor",
        invoice_date=date(2026, 9, 26),
        due_date=date(2026, 10, 26),
        currency="USD",
        subtotal=Decimal("100.00"),
        tax=Decimal("18.00"),
        total=Decimal("118.00"),
        line_items=[
            SimpleNamespace(
                description="Testing Service",
                quantity=Decimal("1"),
                unit_price=Decimal("100.00"),
                amount=Decimal("100.00"),
            )
        ],
    )

    def fake_import(session, file_path):
        assert file_path.exists()
        assert file_path.suffix == ".pdf"

        with fitz.open(file_path) as document:
            assert document.page_count == 1

        return fake_invoice

    monkeypatch.setattr(
        "invoice_buddy.pdf_import_service.import_invoice_from_pdf",
        fake_import,
    )

    response = client.post(
        "/invoices/upload",
        files={
            "file": (
                "invoice.pdf",
                _valid_pdf_bytes(),
                "application/pdf",
            ),
        },
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "imported"
    assert data["filename"] == "invoice.pdf"

    invoice = data["invoice"]

    assert invoice["invoice_number"] == "INV-TEST-001"
    assert invoice["vendor"] == "Test Vendor"
    assert invoice["currency"] == "USD"
    assert invoice["subtotal"] == "100.00"
    assert invoice["tax"] == "18.00"
    assert invoice["total"] == "118.00"

    assert invoice["line_items"][0]["description"] == ("Testing Service")


def test_upload_handles_duplicate_invoice(monkeypatch):
    monkeypatch.setattr(
        security,
        "API_KEY",
        TEST_API_KEY,
    )

    def fake_import(session, file_path):
        raise ValueError("Invoice INV-001 already exists.")

    monkeypatch.setattr(
        "invoice_buddy.pdf_import_service.import_invoice_from_pdf",
        fake_import,
    )

    response = client.post(
        "/invoices/upload",
        files={
            "file": (
                "duplicate.pdf",
                _valid_pdf_bytes(),
                "application/pdf",
            ),
        },
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == ("Invoice INV-001 already exists.")
