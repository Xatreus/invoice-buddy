import json
from pathlib import Path

from invoice_buddy.models import Invoice


def load_invoice_from_json(file_path: str | Path) -> Invoice:
    path = Path(file_path)

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return Invoice.model_validate(data)
