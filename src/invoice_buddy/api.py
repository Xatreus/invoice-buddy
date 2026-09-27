from pathlib import Path
import shutil
import tempfile
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from fastapi.middleware.cors import CORSMiddleware

from fastapi import (
    Depends,
    FastAPI,
    File,
    Header,
    HTTPException,
    UploadFile,
)
from invoice_buddy.security import (
    require_api_key,
    validate_filename,
    validate_question,
)
from pydantic import BaseModel

from invoice_buddy.agent import run_agent
from invoice_buddy.database import SessionLocal, init_db
from invoice_buddy.monitoring import monitor_invoices
from invoice_buddy.repositories import list_invoices


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next,
    ):
        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"

        response.headers["X-Frame-Options"] = "DENY"

        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        response.headers["Content-Security-Policy"] = (
            "default-src 'none'; frame-ancestors 'none'"
        )

        return response


app = FastAPI(
    title="Invoice Buddy",
    description="AI-powered invoice processing assistant",
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
    ],
    allow_headers=[
        "Content-Type",
        "X-API-Key",
    ],
)
app.add_middleware(SecurityHeadersMiddleware)


def authenticate(
    x_api_key: str | None = Header(default=None),
):
    try:
        require_api_key(x_api_key)

    except RuntimeError as exc:
        raise HTTPException(
            status_code=500,
            detail="API authentication is not configured.",
        ) from exc

    except PermissionError as exc:
        raise HTTPException(
            status_code=401,
            detail=str(exc),
        ) from exc


init_db()


MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB


class QuestionRequest(BaseModel):
    question: str


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "invoice-buddy",
    }


@app.get("/invoices")
def get_invoices():
    with SessionLocal() as session:
        invoices = list_invoices(session)

        return [
            {
                "id": invoice.id,
                "invoice_number": invoice.invoice_number,
                "vendor": invoice.vendor,
                "invoice_date": invoice.invoice_date.isoformat(),
                "due_date": (
                    invoice.due_date.isoformat() if invoice.due_date else None
                ),
                "currency": invoice.currency,
                "subtotal": str(invoice.subtotal),
                "tax": str(invoice.tax),
                "total": str(invoice.total),
            }
            for invoice in invoices
        ]


@app.post("/ask")
def ask_invoice_buddy(
    request: QuestionRequest,
    _: None = Depends(authenticate),
):
    try:
        question = validate_question(request.question)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    with SessionLocal() as session:
        answer = run_agent(
            session,
            question,
        )

        return {
            "question": question,
            "answer": answer,
        }


@app.post("/monitor")
def monitor(
    _: None = Depends(authenticate),
):
    with SessionLocal() as session:
        return monitor_invoices(session)


@app.get("/anomalies")
def get_anomalies(
    _: None = Depends(authenticate),
):
    from invoice_buddy.anomaly_repository import (
        list_unresolved_anomalies,
    )

    with SessionLocal() as session:
        anomalies = list_unresolved_anomalies(session)

        return [
            {
                "id": anomaly.id,
                "invoice_id": anomaly.invoice_id,
                "anomaly_type": anomaly.anomaly_type,
                "severity": anomaly.severity,
                "message": anomaly.message,
                "detected_at": anomaly.detected_at.isoformat(),
                "resolved": anomaly.resolved,
            }
            for anomaly in anomalies
        ]


@app.post("/invoices/upload")
async def upload_invoice(
    file: UploadFile = File(...),
    _: None = Depends(authenticate),
):
    """
    Upload a PDF invoice, extract its data using the LLM,
    validate it, check for duplicates, and save it to the database.
    """

    try:
        filename = validate_filename(file.filename or "")
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    if Path(filename).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    temporary_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf",
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)

            total_size = 0

            while True:
                chunk = await file.read(1024 * 1024)

                if not chunk:
                    break

                total_size += len(chunk)

                if total_size > MAX_UPLOAD_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail=("PDF file is too large. Maximum size is 10 MB."),
                    )

                temporary_file.write(chunk)

        from invoice_buddy.pdf_import_service import (
            import_invoice_from_pdf,
        )

        with SessionLocal() as session:
            try:
                invoice = import_invoice_from_pdf(
                    session,
                    temporary_path,
                )

            except ValueError as exc:
                raise HTTPException(
                    status_code=400,
                    detail=str(exc),
                ) from exc

            return {
                "status": "imported",
                "filename": filename,
                "invoice": {
                    "invoice_number": (invoice.invoice_number),
                    "vendor": invoice.vendor,
                    "invoice_date": (invoice.invoice_date.isoformat()),
                    "due_date": (
                        invoice.due_date.isoformat() if invoice.due_date else None
                    ),
                    "currency": invoice.currency,
                    "subtotal": str(invoice.subtotal),
                    "tax": str(invoice.tax),
                    "total": str(invoice.total),
                    "line_items": [
                        {
                            "description": item.description,
                            "quantity": str(item.quantity),
                            "unit_price": str(item.unit_price),
                            "amount": str(item.amount),
                        }
                        for item in invoice.line_items
                    ],
                },
            }

    finally:
        await file.close()

        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def authenticate(
    x_api_key: str | None = Header(default=None),
):
    try:
        require_api_key(x_api_key)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=500,
            detail="API authentication is not configured.",
        ) from exc
    except PermissionError as exc:
        raise HTTPException(
            status_code=401,
            detail=str(exc),
        ) from exc
