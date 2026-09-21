from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric, String
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

    line_items: Mapped[list["LineItemDB"]] = relationship(
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
