import pytest

from invoice_buddy.rag_evaluation import (
    RAGEvaluationCase,
    evaluate_case,
    evaluate_retrieval,
)


def test_evaluate_case_detects_correct_invoice():
    case = RAGEvaluationCase(
        query="payment terms",
        expected_invoice_number="INV-001",
        expected_terms=(
            "payment",
            "30 days",
        ),
    )

    results = [
        {
            "document": ("Payment is due within 30 days."),
            "metadata": {
                "invoice_number": "INV-001",
            },
            "distance": 0.1,
        }
    ]

    result = evaluate_case(
        case,
        results,
    )

    assert result.hit_at_k is True
    assert result.reciprocal_rank == 1.0
    assert result.keyword_coverage == 1.0


def test_evaluate_case_detects_wrong_invoice():
    case = RAGEvaluationCase(
        query="payment terms",
        expected_invoice_number="INV-001",
    )

    results = [
        {
            "document": "Google payment terms",
            "metadata": {
                "invoice_number": "INV-002",
            },
            "distance": 0.1,
        }
    ]

    result = evaluate_case(
        case,
        results,
    )

    assert result.hit_at_k is False
    assert result.reciprocal_rank == 0.0


def test_evaluate_case_calculates_rank():
    case = RAGEvaluationCase(
        query="payment terms",
        expected_invoice_number="INV-001",
    )

    results = [
        {
            "document": "Other invoice",
            "metadata": {
                "invoice_number": "INV-002",
            },
            "distance": 0.1,
        },
        {
            "document": "Correct invoice",
            "metadata": {
                "invoice_number": "INV-001",
            },
            "distance": 0.2,
        },
    ]

    result = evaluate_case(
        case,
        results,
    )

    assert result.hit_at_k is True
    assert result.reciprocal_rank == 0.5


def test_evaluate_case_calculates_partial_keyword_coverage():
    case = RAGEvaluationCase(
        query="payment terms",
        expected_invoice_number="INV-001",
        expected_terms=(
            "payment",
            "30 days",
            "net",
        ),
    )

    results = [
        {
            "document": "Payment is due within 30 days.",
            "metadata": {
                "invoice_number": "INV-001",
            },
            "distance": 0.1,
        }
    ]

    result = evaluate_case(
        case,
        results,
    )

    assert result.keyword_coverage == pytest.approx(2 / 3)


def test_evaluate_case_with_no_expected_terms():
    case = RAGEvaluationCase(
        query="invoice",
        expected_invoice_number="INV-001",
    )

    results = []

    result = evaluate_case(
        case,
        results,
    )

    assert result.hit_at_k is False
    assert result.reciprocal_rank == 0.0
    assert result.keyword_coverage == 1.0


def test_evaluate_retrieval_calculates_metrics():
    cases = [
        RAGEvaluationCase(
            query="payment",
            expected_invoice_number="INV-001",
        ),
        RAGEvaluationCase(
            query="hosting",
            expected_invoice_number="INV-002",
        ),
    ]

    fake_results = {
        "payment": [
            {
                "document": "Payment due in 30 days.",
                "metadata": {
                    "invoice_number": "INV-001",
                },
                "distance": 0.1,
            }
        ],
        "hosting": [
            {
                "document": "Cloud hosting.",
                "metadata": {
                    "invoice_number": "INV-002",
                },
                "distance": 0.2,
            }
        ],
    }

    def retrieve(query):
        return fake_results[query]

    metrics = evaluate_retrieval(
        cases,
        retrieve,
    )

    assert metrics["cases"] == 2.0
    assert metrics["hit_rate"] == 1.0
    assert metrics["mean_reciprocal_rank"] == 1.0


def test_evaluate_retrieval_rejects_empty_dataset():
    with pytest.raises(
        ValueError,
        match="At least one evaluation case",
    ):
        evaluate_retrieval(
            [],
            lambda query: [],
        )
