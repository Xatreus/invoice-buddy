from datetime import date
from decimal import Decimal
import json
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


def convert_llm_invoice(extracted: LLMInvoice) -> Invoice:
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


def extract_invoice_with_llm(text: str) -> Invoice:
    client = OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=os.environ["NVIDIA_API_KEY"],
    )

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": (
                    "Extract the invoice into the exact JSON structure "
                    "described below.\n\n"
                    "Required top-level fields:\n"
                    "invoice_number, vendor, invoice_date, due_date, "
                    "currency, subtotal, tax, total, line_items\n\n"
                    "Each line_items element MUST contain ALL four fields:\n"
                    "description, quantity, unit_price, amount\n\n"
                    "Rules:\n"
                    "- Never omit a required field.\n"
                    "- Copy values from the invoice text.\n"
                    "- Do not invent values.\n"
                    "- Dates must use YYYY-MM-DD.\n"
                    "- quantity, unit_price, amount, subtotal, tax, "
                    "and total must be strings containing decimal numbers.\n"
                    "- due_date may be null if it is missing.\n"
                    "- line_items must be an array.\n\n"
                    "Return ONLY valid JSON. No markdown. No explanation."
                ),
            },
            {
                "role": "user",
                "content": text,
            },
        ],
        response_format={"type": "json_object"},
        temperature=0,
        max_tokens=2000,
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError("LLM did not return any content.")

    extracted = LLMInvoice.model_validate(json.loads(content))

    return convert_llm_invoice(extracted)
