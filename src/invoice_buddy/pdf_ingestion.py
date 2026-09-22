from pathlib import Path

import fitz


def extract_text_from_pdf(file_path: str | Path) -> str:
    path = Path(file_path)

    with fitz.open(path) as document:
        pages = [page.get_text() for page in document]

    return "\n".join(pages).strip()
