from invoice_buddy.agent import run_agent
from invoice_buddy.database import SessionLocal


QUESTION = "What services or products are mentioned in the invoice document?"


def main():
    print("=" * 60)
    print("INVOICE BUDDY - AGENT + RAG DEMO")
    print("=" * 60)

    print()
    print(f"Question: {QUESTION}")
    print()

    with SessionLocal() as session:
        answer = run_agent(
            session,
            QUESTION,
        )

    print()
    print("=" * 60)
    print("FINAL ANSWER")
    print("=" * 60)
    print()
    print(answer)


if __name__ == "__main__":
    main()
