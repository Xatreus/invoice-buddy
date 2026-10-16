# Invoice Buddy

An AI-powered invoice intelligence API built with Python. Invoice Buddy imports PDF invoices, extracts structured fields with an LLM, stores invoice records, and lets users query financial data or retrieve context from invoice documents through a tool-calling agent.

> **Project status:** Personal engineering project. Designed to run locally or with Docker Compose; no hosted demo is currently configured. Do not use with sensitive production financial data without a security and privacy review.

## What it does

- **PDF invoice ingestion** — accepts PDF uploads, extracts invoice content, and uses an LLM to structure invoice fields and line items.
- **Structured storage and queries** — persists invoice data with SQLAlchemy and SQLite; supports invoice lookup, filtering, spending summaries, vendor history, overdue-invoice queries, and date-range queries.
- **Tool-calling AI agent** — routes questions to registered tools rather than relying on the language model to invent financial facts.
- **Retrieval-augmented generation (RAG)** — indexes invoice-document text in ChromaDB and retrieves relevant context for questions about invoice terms and descriptions.
- **Anomaly and duplicate checks** — includes modules for duplicate detection, invoice monitoring, and anomaly reporting.
- **REST API** — exposes FastAPI endpoints and interactive API documentation.
- **Basic API protections** — API-key checks on selected endpoints, filename/question validation, a PDF upload size limit, and security response headers.
- **Tests and retrieval evaluation** — includes pytest coverage across API behavior, extraction, data access, tools, security, and retrieval-related modules.

## Tech stack

| Area | Technologies |
|---|---|
| Language and API | Python 3.14+, FastAPI, Uvicorn |
| LLM integration | OpenAI-compatible client / OpenRouter by default; Gemini provider code is also present |
| Retrieval | ChromaDB, sentence-transformers |
| Data and validation | SQLite, SQLAlchemy, Pydantic |
| Documents | PyMuPDF, python-multipart |
| Testing and quality | pytest |

## Architecture

```text
PDF invoice
    |
    v
FastAPI upload endpoint
    |
    v
PDF text extraction -> LLM structured extraction -> validation
    |
    +--> SQLAlchemy / SQLite (structured invoice fields)
    |
    +--> ChromaDB (retrievable invoice-document text)

User question
    |
    v
FastAPI /ask -> tool-calling agent
    |
    +--> SQL/database tools for totals, dates, vendors, and analytics
    |
    +--> RAG search for details from original invoice text
    |
    v
Answer grounded in tool results
```

## Requirements

- Python **3.14 or newer** (matches the current project metadata and Docker image)
- An OpenRouter API key for the default LLM provider
- Docker and Docker Compose (optional, for containerized use)

## Run locally

1. Clone the repository and enter the project directory:

   ```bash
   git clone https://github.com/Xatreus/invoice-buddy.git
   cd invoice-buddy
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   # macOS / Linux
   source .venv/bin/activate
   # Windows PowerShell
   .venv\Scripts\Activate.ps1
   ```

3. Install the project and test dependency:

   ```bash
   python -m pip install --upgrade pip
   pip install -e .
   pip install pytest
   ```

4. Set the environment variables in your shell before starting the API. Do not commit real keys.

   **macOS / Linux**
   ```bash
   export OPENROUTER_API_KEY="your-openrouter-api-key"
   export INVOICE_BUDDY_API_KEY="replace-with-a-long-random-secret"
   export LLM_PROVIDER="openrouter"
   export OPENROUTER_MODEL="openrouter/free"
   ```

   **Windows PowerShell**
   ```powershell
   $env:OPENROUTER_API_KEY = "your-openrouter-api-key"
   $env:INVOICE_BUDDY_API_KEY = "replace-with-a-long-random-secret"
   $env:LLM_PROVIDER = "openrouter"
   $env:OPENROUTER_MODEL = "openrouter/free"
   ```

5. Start the API:

   ```bash
   python -m uvicorn invoice_buddy.api:app --app-dir src --reload
   ```

6. Open the interactive API docs at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) or check [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health).

## Run with Docker Compose

Docker Compose reads environment variables from a local `.env` file. Create it from the safe template, then add your own keys:

```bash
cp .env.example .env
```

Edit `.env` and set `OPENROUTER_API_KEY` and a strong `INVOICE_BUDDY_API_KEY`. Then run:

```bash
docker compose up --build
```

The API is available at [http://127.0.0.1:8000](http://127.0.0.1:8000). Invoice data is persisted in the Docker volume configured by `docker-compose.yml`.

## API endpoints

| Method | Endpoint | Purpose | API key |
|---|---|---|---|
| GET | `/health` | Health check | No |
| GET | `/invoices` | List stored invoices | No |
| POST | `/invoices/upload` | Upload and import a PDF invoice | Yes |
| POST | `/ask` | Ask a natural-language invoice question | Yes |
| POST | `/monitor` | Run invoice monitoring | Yes |
| GET | `/anomalies` | List unresolved anomalies | Yes |

Protected endpoints expect the `X-API-Key` request header.

### Example: ask a question

```bash
curl -X POST "http://127.0.0.1:8000/ask" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: replace-with-a-long-random-secret" \
  -d '{"question":"What is the total spend by vendor?"}'
```

### Example: upload a PDF

```bash
curl -X POST "http://127.0.0.1:8000/invoices/upload" \
  -H "X-API-Key: replace-with-a-long-random-secret" \
  -F "file=@./invoice.pdf"
```

The current upload implementation accepts PDF files up to 10 MB. A successful request depends on valid invoice content and a configured LLM provider.

## Run tests

```bash
pytest
```

The repository contains tests for API behavior, PDF ingestion and extraction, invoice workflows, database access, tool registration, security validation, analytics, anomaly detection, and RAG-related behavior. Test results have not been independently verified as part of this README update.

## Configuration

| Variable | Purpose |
|---|---|
| `OPENROUTER_API_KEY` | API key for the default OpenRouter provider |
| `INVOICE_BUDDY_API_KEY` | Shared key required by protected API endpoints |
| `LLM_PROVIDER` | Provider selector; defaults to `openrouter` |
| `OPENROUTER_MODEL` | OpenRouter model name; defaults to `openrouter/free` |
| `GEMINI_API_KEY` | Required if using the Gemini provider code |
| `GEMINI_MODEL` | Gemini model name; defaults to `gemini-3-flash-preview` |
| `DATABASE_URL` | SQLAlchemy database URL; defaults to a local SQLite database |

## Security notes

- Never commit `.env`, API keys, real invoices, or customer financial data.
- The API-key mechanism is a simple shared-secret control, not a complete identity and access-management system.
- The current `/invoices` endpoint does not require an API key; review this before exposing the service beyond a trusted local environment.
- Review CORS, logging, rate limiting, file-content validation, access control, and data-retention behavior before any public deployment.
- Treat uploaded invoice text as untrusted input. The agent prompt instructs the model not to follow instructions found in retrieved documents, but prompt instructions alone are not a complete prompt-injection defense.

## Roadmap

- Add CI to run the test suite automatically.
- Add an API authentication test matrix and deployment-safe configuration checks.
- Add reproducible RAG evaluation results and a sample end-to-end demo.
- Add screenshots or a short demo recording once the user flow is stable.

## License

MIT. See [LICENSE](LICENSE).
