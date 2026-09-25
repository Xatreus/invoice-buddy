from decimal import Decimal

from sqlalchemy.orm import Session

from invoice_buddy.anomaly_detection import detect_invoice_anomalies
from invoice_buddy.anomaly_repository import create_anomaly_if_missing
from invoice_buddy.repositories import list_invoices


def monitor_invoices(
    session: Session,
    large_invoice_threshold: Decimal = Decimal("100000.00"),
) -> dict:
    invoices = list_invoices(session)

    anomalies = []

    for invoice in invoices:
        invoice_anomalies = detect_invoice_anomalies(
            session,
            invoice,
            large_invoice_threshold=large_invoice_threshold,
        )

        for anomaly in invoice_anomalies:
            stored_anomaly = create_anomaly_if_missing(
                session=session,
                invoice_id=anomaly.invoice_id,
                anomaly_type=anomaly.anomaly_type,
                severity="warning",
                message=anomaly.message,
            )

            anomalies.append(
                {
                    "id": stored_anomaly.id,
                    "invoice_id": stored_anomaly.invoice_id,
                    "invoice_number": anomaly.invoice_number,
                    "vendor": anomaly.vendor,
                    "anomaly_type": stored_anomaly.anomaly_type,
                    "severity": stored_anomaly.severity,
                    "message": stored_anomaly.message,
                    "resolved": stored_anomaly.resolved,
                }
            )

    return {
        "anomaly_count": len(anomalies),
        "anomalies": anomalies,
    }
