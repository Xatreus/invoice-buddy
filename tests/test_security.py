import pytest

from invoice_buddy.security import (
    validate_filename,
    validate_question,
)


def test_validate_question_accepts_normal_question():
    result = validate_question("What is the total of INV-001?")

    assert result == ("What is the total of INV-001?")


def test_validate_question_strips_whitespace():
    result = validate_question("   What is the total?   ")

    assert result == "What is the total?"


def test_validate_question_rejects_empty_question():
    with pytest.raises(
        ValueError,
        match="Question cannot be empty",
    ):
        validate_question("   ")


def test_validate_question_rejects_oversized_question():
    with pytest.raises(
        ValueError,
        match="Question is too long",
    ):
        validate_question("a" * 2001)


def test_validate_filename_accepts_pdf():
    result = validate_filename("invoice.pdf")

    assert result == "invoice.pdf"


def test_validate_filename_rejects_empty_filename():
    with pytest.raises(
        ValueError,
        match="Filename is required",
    ):
        validate_filename("")


def test_validate_filename_rejects_oversized_filename():
    with pytest.raises(
        ValueError,
        match="Filename is too long",
    ):
        validate_filename("a" * 256)
