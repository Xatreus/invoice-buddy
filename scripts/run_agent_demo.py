from invoice_buddy.agent import run_agent
from invoice_buddy.database import SessionLocal, init_db


init_db()


questions = [
    "How many invoices are in the database?",
    "What is the total amount we have spent?",
    "How much have we spent with Global Tech Solutions?",
    "Show me our spending by vendor.",
    "Do I have any suspicious or unusual invoices?",
    "Monitor all invoices for potential problems.",
]

with SessionLocal() as session:
    for question in questions:
        print()
        print("=" * 60)
        print(f"USER: {question}")
        print("=" * 60)

        answer = run_agent(
            session,
            question,
        )

        print()
        print(f"INVOICE BUDDY: {answer}")
