from decimal import Decimal

from sqlalchemy.orm import Session

from invoice_buddy.anomaly_detection import detect_invoice_anomalies
from invoice_buddy.repositories import list_invoices


def detect_anomalies_tool(
    session: Session,
    large_invoice_threshold: str = "100000.00",
) -> list[dict]:
    invoices = list_invoices(session)

    anomalies = []

    for invoice in invoices:
        invoice_anomalies = detect_invoice_anomalies(
            session,
            invoice,
            large_invoice_threshold=Decimal(large_invoice_threshold),
        )

        for anomaly in invoice_anomalies:
            anomalies.append(
                {
                    "invoice_id": anomaly.invoice_id,
                    "invoice_number": anomaly.invoice_number,
                    "vendor": anomaly.vendor,
                    "anomaly_type": anomaly.anomaly_type,
                    "message": anomaly.message,
                }
            )

    return anomalies
