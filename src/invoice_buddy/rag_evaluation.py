from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class RAGEvaluationCase:
    query: str
    expected_invoice_number: str
    expected_terms: tuple[str, ...] = ()


@dataclass(frozen=True)
class RAGEvaluationResult:
    query: str
    expected_invoice_number: str
    hit_at_k: bool
    reciprocal_rank: float
    keyword_coverage: float


def _document_text(result: dict[str, Any]) -> str:
    document = result.get("document", "")

    if not isinstance(document, str):
        return ""

    return document.lower()


def evaluate_case(
    case: RAGEvaluationCase,
    results: list[dict[str, Any]],
) -> RAGEvaluationResult:
    matching_ranks = []

    for rank, result in enumerate(results, start=1):
        metadata = result.get("metadata", {})

        if metadata.get("invoice_number") == (case.expected_invoice_number):
            matching_ranks.append(rank)

    if matching_ranks:
        first_rank = matching_ranks[0]

        reciprocal_rank = 1.0 / first_rank
        hit_at_k = True
    else:
        reciprocal_rank = 0.0
        hit_at_k = False

    if not case.expected_terms:
        keyword_coverage = 1.0
    else:
        combined_text = " ".join(_document_text(result) for result in results)

        matched_terms = [
            term for term in case.expected_terms if term.lower() in combined_text
        ]

        keyword_coverage = len(matched_terms) / len(case.expected_terms)

    return RAGEvaluationResult(
        query=case.query,
        expected_invoice_number=case.expected_invoice_number,
        hit_at_k=hit_at_k,
        reciprocal_rank=reciprocal_rank,
        keyword_coverage=keyword_coverage,
    )


def evaluate_retrieval(
    cases: list[RAGEvaluationCase],
    retrieve: Callable[[str], list[dict[str, Any]]],
) -> dict[str, float]:
    if not cases:
        raise ValueError("At least one evaluation case is required.")

    results = []

    for case in cases:
        retrieved_documents = retrieve(case.query)

        results.append(
            evaluate_case(
                case,
                retrieved_documents,
            )
        )

    hit_rate = sum(result.hit_at_k for result in results) / len(results)

    mean_reciprocal_rank = sum(result.reciprocal_rank for result in results) / len(
        results
    )

    average_keyword_coverage = sum(result.keyword_coverage for result in results) / len(
        results
    )

    return {
        "cases": float(len(results)),
        "hit_rate": hit_rate,
        "mean_reciprocal_rank": mean_reciprocal_rank,
        "average_keyword_coverage": average_keyword_coverage,
    }
