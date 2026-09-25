from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from invoice_buddy.db_models import InvoiceAnomalyDB


def create_anomaly_if_missing(
    session: Session,
    invoice_id: int,
    anomaly_type: str,
    severity: str,
    message: str,
) -> InvoiceAnomalyDB:
    statement = select(InvoiceAnomalyDB).where(
        InvoiceAnomalyDB.invoice_id == invoice_id,
        InvoiceAnomalyDB.anomaly_type == anomaly_type,
        InvoiceAnomalyDB.resolved.is_(False),
    )

    existing = session.scalar(statement)

    if existing is not None:
        return existing

    anomaly = InvoiceAnomalyDB(
        invoice_id=invoice_id,
        anomaly_type=anomaly_type,
        severity=severity,
        message=message,
        detected_at=datetime.now(),
        resolved=False,
    )

    session.add(anomaly)
    session.commit()
    session.refresh(anomaly)

    return anomaly


def list_unresolved_anomalies(
    session: Session,
) -> list[InvoiceAnomalyDB]:
    statement = (
        select(InvoiceAnomalyDB)
        .where(InvoiceAnomalyDB.resolved.is_(False))
        .order_by(InvoiceAnomalyDB.detected_at.desc())
    )

    return list(session.scalars(statement).all())


def resolve_anomaly(
    session: Session,
    anomaly_id: int,
) -> InvoiceAnomalyDB | None:
    anomaly = session.get(InvoiceAnomalyDB, anomaly_id)

    if anomaly is None:
        return None

    anomaly.resolved = True

    session.commit()
    session.refresh(anomaly)

    return anomaly
