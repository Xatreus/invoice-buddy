from datetime import date
from decimal import Decimal
import os

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

from invoice_buddy.models import Invoice, LineItem


load_dotenv()


class LLMLineItem(BaseModel):
    description: str
    quantity: str
    unit_price: str
    amount: str


class LLMInvoice(BaseModel):
    invoice_number: str
    vendor: str
    invoice_date: str
    due_date: str | None
    currency: str
    subtotal: str
    tax: str
    total: str
    line_items: list[LLMLineItem]


def convert_llm_invoice(
    extracted: LLMInvoice,
) -> Invoice:
    line_items = [
        LineItem(
            description=item.description,
            quantity=Decimal(item.quantity),
            unit_price=Decimal(item.unit_price),
            amount=Decimal(item.amount),
        )
        for item in extracted.line_items
    ]

    return Invoice(
        invoice_number=extracted.invoice_number,
        vendor=extracted.vendor,
        invoice_date=date.fromisoformat(extracted.invoice_date),
        due_date=(
            date.fromisoformat(extracted.due_date) if extracted.due_date else None
        ),
        currency=extracted.currency,
        subtotal=Decimal(extracted.subtotal),
        tax=Decimal(extracted.tax),
        total=Decimal(extracted.total),
        line_items=line_items,
    )


def extract_invoice_with_llm(
    text: str,
) -> Invoice:
    client = OpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
    )

    response = client.responses.parse(
        model="gpt-5.6-luna",
        input=[
            {
                "role": "system",
                "content": (
                    "Extract invoice information from the "
                    "provided text. Return dates as YYYY-MM-DD "
                    "strings and monetary values and quantities "
                    "as decimal strings."
                ),
            },
            {
                "role": "user",
                "content": text,
            },
        ],
        text_format=LLMInvoice,
    )

    extracted = response.output_parsed

    if extracted is None:
        raise ValueError("LLM did not return a structured invoice.")

    return convert_llm_invoice(extracted)
