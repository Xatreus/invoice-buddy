from invoice_buddy.rag import search_invoice_text
from invoice_buddy.rag_evaluation import evaluate_retrieval
from data.rag_eval_cases import RAG_EVALUATION_CASES


def retrieve(query: str):
    return search_invoice_text(
        query=query,
        n_results=5,
    )


def main():
    metrics = evaluate_retrieval(
        cases=RAG_EVALUATION_CASES,
        retrieve=retrieve,
    )

    print()
    print("RAG EVALUATION")
    print("=" * 40)

    print(f"Cases: {int(metrics['cases'])}")

    print(f"Hit Rate: {metrics['hit_rate']:.2%}")

    print(f"Mean Reciprocal Rank: {metrics['mean_reciprocal_rank']:.3f}")

    print(f"Average Keyword Coverage: {metrics['average_keyword_coverage']:.2%}")


if __name__ == "__main__":
    main()
