from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from invoice_buddy.database import Base


class InvoiceDB(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    invoice_number: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
    )

    vendor: Mapped[str] = mapped_column(
        String(255),
        index=True,
    )

    invoice_date: Mapped[date] = mapped_column(Date)

    due_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    currency: Mapped[str] = mapped_column(
        String(10),
    )

    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
    )

    tax: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
    )

    total: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
    )

    line_items: Mapped[list[LineItemDB]] = relationship(
        back_populates="invoice",
        cascade="all, delete-orphan",
    )


class LineItemDB(Base):
    __tablename__ = "line_items"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    invoice_id: Mapped[int] = mapped_column(
        ForeignKey("invoices.id"),
        index=True,
    )

    description: Mapped[str] = mapped_column(
        String(255),
    )

    quantity: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
    )

    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
    )

    invoice: Mapped[InvoiceDB] = relationship(
        back_populates="line_items",
    )


class InvoiceAnomalyDB(Base):
    __tablename__ = "invoice_anomalies"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    invoice_id: Mapped[int] = mapped_column(
        ForeignKey("invoices.id"),
        index=True,
    )

    anomaly_type: Mapped[str] = mapped_column(
        String(100),
        index=True,
    )

    severity: Mapped[str] = mapped_column(
        String(50),
        default="warning",
    )

    message: Mapped[str] = mapped_column(
        String(1000),
    )

    detected_at: Mapped[datetime] = mapped_column(
        DateTime,
    )

    resolved: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        index=True,
    )

    invoice: Mapped["InvoiceDB"] = relationship()
