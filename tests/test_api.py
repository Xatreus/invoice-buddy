from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from fastapi.testclient import TestClient

from invoice_buddy.api import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "invoice-buddy",
    }


def test_upload_rejects_non_pdf():
    response = client.post(
        "/invoices/upload",
        files={
            "file": (
                "invoice.txt",
                b"not a pdf",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == ("Only PDF files are supported.")


def test_upload_requires_file():
    response = client.post("/invoices/upload")

    assert response.status_code == 422


def test_upload_imports_invoice(monkeypatch):
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

        return fake_invoice

    monkeypatch.setattr(
        "invoice_buddy.pdf_import_service.import_invoice_from_pdf",
        fake_import,
    )

    response = client.post(
        "/invoices/upload",
        files={
            "file": (
                "test_invoice.pdf",
                b"fake pdf content",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "imported"
    assert data["filename"] == "test_invoice.pdf"

    invoice = data["invoice"]

    assert invoice["invoice_number"] == "INV-TEST-001"
    assert invoice["vendor"] == "Test Vendor"
    assert invoice["currency"] == "USD"
    assert invoice["subtotal"] == "100.00"
    assert invoice["tax"] == "18.00"
    assert invoice["total"] == "118.00"

    assert invoice["line_items"][0]["description"] == ("Testing Service")


def test_upload_handles_duplicate_invoice(monkeypatch):
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
                b"fake pdf content",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == ("Invoice INV-001 already exists.")
