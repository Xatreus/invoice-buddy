FROM python:3.14-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml README.md LICENSE ./

COPY src ./src

RUN pip install --no-cache-dir -e .

RUN mkdir -p /app/data/chroma

COPY data/sample_invoice.json ./data/sample_invoice.json

EXPOSE 8000

CMD ["uvicorn", "invoice_buddy.api:app", "--host", "0.0.0.0", "--port", "8000"]