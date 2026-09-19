from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator


class LineItem(BaseModel):
    description: str
    quantity: Decimal = Field(gt=0)
    unit_price: Decimal = Field(ge=0)
    amount: Decimal = Field(ge=0)


class Invoice(BaseModel):
    invoice_number: str
    vendor: str
    invoice_date: date
    due_date: date | None = None
    currency: str
    subtotal: Decimal = Field(ge=0)
    tax: Decimal = Field(ge=0)
    total: Decimal = Field(ge=0)
    line_items: list[LineItem]

    @model_validator(mode="after")
    def validate_total(self):
        if self.subtotal + self.tax != self.total:
            raise ValueError("total must equal subtotal plus tax")

        return self
