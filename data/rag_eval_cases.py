from invoice_buddy.rag_evaluation import RAGEvaluationCase


RAG_EVALUATION_CASES = [
    RAGEvaluationCase(
        query="What are the payment terms?",
        expected_invoice_number="INV-001",
        expected_terms=(
            "payment",
            "30 days",
        ),
    ),
    RAGEvaluationCase(
        query="What cloud services were billed?",
        expected_invoice_number="INV-001",
        expected_terms=(
            "cloud",
            "hosting",
        ),
    ),
    RAGEvaluationCase(
        query="What is the billing period?",
        expected_invoice_number="INV-002",
        expected_terms=(
            "billing",
            "period",
        ),
    ),
    RAGEvaluationCase(
        query="What services did the vendor provide?",
        expected_invoice_number="INV-002",
        expected_terms=(
            "services",
            "vendor",
        ),
    ),
    RAGEvaluationCase(
        query="What are the invoice payment conditions?",
        expected_invoice_number="INV-003",
        expected_terms=(
            "payment",
            "conditions",
        ),
    ),
]
