from sqlalchemy.orm import Session

from invoice_buddy.anomaly_repository import list_unresolved_anomalies


def list_unresolved_anomalies_tool(
    session: Session,
) -> list[dict]:
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
