import os
import secrets


API_KEY = os.getenv("INVOICE_BUDDY_API_KEY")

MAX_QUESTION_LENGTH = 2000
MAX_FILENAME_LENGTH = 255


def require_api_key(
    provided_key: str | None,
) -> None:
    if not API_KEY:
        raise RuntimeError("INVOICE_BUDDY_API_KEY is not configured.")

    if not provided_key:
        raise PermissionError("API key is required.")

    if not secrets.compare_digest(
        provided_key,
        API_KEY,
    ):
        raise PermissionError("Invalid API key.")


def validate_question(question: str) -> str:
    question = question.strip()

    if not question:
        raise ValueError("Question cannot be empty.")

    if len(question) > MAX_QUESTION_LENGTH:
        raise ValueError("Question is too long.")

    return question


def validate_filename(filename: str) -> str:
    filename = filename.strip()

    if not filename:
        raise ValueError("Filename is required.")

    if len(filename) > MAX_FILENAME_LENGTH:
        raise ValueError("Filename is too long.")

    return filename
