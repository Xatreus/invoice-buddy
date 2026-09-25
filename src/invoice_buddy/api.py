from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from invoice_buddy.agent import run_agent
from invoice_buddy.database import SessionLocal, init_db
from invoice_buddy.monitoring import monitor_invoices
from invoice_buddy.repositories import list_invoices


app = FastAPI(
    title="Invoice Buddy",
    description="AI-powered invoice processing assistant",
    version="0.1.0",
)


init_db()


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
def ask_invoice_buddy(request: QuestionRequest):
    with SessionLocal() as session:
        answer = run_agent(
            session,
            request.question,
        )

        return {
            "question": request.question,
            "answer": answer,
        }


@app.post("/monitor")
def monitor():
    with SessionLocal() as session:
        return monitor_invoices(session)


@app.get("/anomalies")
def get_anomalies():
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
