from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy.orm import Session

from invoice_buddy.db_models import InvoiceDB
from invoice_buddy.repositories import list_invoices_by_vendor


@dataclass(frozen=True)
class Anomaly:
    invoice_id: int
    invoice_number: str
    vendor: str
    anomaly_type: str
    message: str


def detect_large_invoice(
    invoice: InvoiceDB,
    threshold: Decimal,
) -> Anomaly | None:
    if invoice.total <= threshold:
        return None

    return Anomaly(
        invoice_id=invoice.id,
        invoice_number=invoice.invoice_number,
        vendor=invoice.vendor,
        anomaly_type="large_invoice",
        message=(
            f"Invoice {invoice.invoice_number} from "
            f"{invoice.vendor} is {invoice.total}, "
            f"which exceeds the threshold of {threshold}."
        ),
    )


def detect_vendor_outlier(
    session: Session,
    invoice: InvoiceDB,
    multiplier: Decimal = Decimal("2"),
) -> Anomaly | None:
    vendor_invoices = list_invoices_by_vendor(
        session,
        invoice.vendor,
    )

    if len(vendor_invoices) < 2:
        return None

    previous_invoices = [item for item in vendor_invoices if item.id != invoice.id]

    if not previous_invoices:
        return None

    average = sum(
        (item.total for item in previous_invoices),
        Decimal("0.00"),
    ) / Decimal(len(previous_invoices))

    if invoice.total <= average * multiplier:
        return None

    return Anomaly(
        invoice_id=invoice.id,
        invoice_number=invoice.invoice_number,
        vendor=invoice.vendor,
        anomaly_type="vendor_outlier",
        message=(
            f"Invoice {invoice.invoice_number} from "
            f"{invoice.vendor} is {invoice.total}, "
            f"which is more than {multiplier}x the "
            f"previous average of {average:.2f}."
        ),
    )


def detect_invoice_anomalies(
    session: Session,
    invoice: InvoiceDB,
    large_invoice_threshold: Decimal = Decimal("100000"),
) -> list[Anomaly]:
    anomalies: list[Anomaly] = []

    large_invoice = detect_large_invoice(
        invoice,
        large_invoice_threshold,
    )

    if large_invoice is not None:
        anomalies.append(large_invoice)

    vendor_outlier = detect_vendor_outlier(
        session,
        invoice,
    )

    if vendor_outlier is not None:
        anomalies.append(vendor_outlier)

    return anomalies
