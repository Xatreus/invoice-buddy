# Portfolio-readiness remediation checklist

This document tracks proposed hardening work for the Invoice Buddy pull request. It deliberately distinguishes code changes from checks that must run in CI or locally.

## Included in this branch

- Protect invoice listing with the same API-key dependency as other sensitive endpoints.
- Bound invoice listing with limit/offset pagination (default 50, maximum 100).
- Validate PDF signature and parseability; reject empty PDFs and PDFs over 100 pages, in addition to the existing 10 MB upload cap.
- Prevent ambiguous mixed-currency totals, averages, largest-invoice comparisons, and vendor spend rankings. Use `spend_by_currency()` for mixed-currency datasets.
- Validate date range ordering and restrict repository update fields.
- Apply SQLite-only connection arguments only when the configured database URL is SQLite.
- Add a GitHub Actions workflow for supported Python versions, linting, tests, and dependency auditing.

## Follow-up work still required

- Run the workflow and address compatibility or lint/test failures; CI is evidence, not a guarantee of correctness.
- Add tests for the API authentication matrix, invalid and oversized PDFs, page limits, pagination boundaries, mixed currencies, and invalid date ranges.
- Make invoice persistence and vector indexing recoverable as a single workflow (for example, a persisted indexing status plus retryable job/outbox).
- Add OCR for scanned invoices; current text extraction should not be advertised as OCR support.
- Add synthetic 400-invoice benchmark/evaluation covering persistence, exact SQL answers, retrieval recall, and end-to-end answer grounding. Record measured results rather than making unverified performance claims.
- Evaluate prompt-injection resistance and tenant isolation before exposing the service to untrusted users.
- Decide whether to retain source PDFs, define retention/deletion behavior, and ensure deletion removes corresponding vector records.
- Consider dependency pinning/lockfile after resolving and testing a compatible set. Avoid blindly pinning versions without running the suite.

## API change

`GET /invoices` now requires `X-API-Key` and returns a paginated object:
`{"items": [...], "limit": 50, "offset": 0, "count": 50}`.
Clients relying on the previous unauthenticated array response must be updated.
