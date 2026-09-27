FROM python:3.14-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

# Copy project metadata
COPY pyproject.toml README.md LICENSE ./

# Install CPU-only PyTorch first.
# This prevents sentence-transformers from pulling CUDA/NVIDIA packages.
RUN pip install --no-cache-dir \
    --index-url https://download.pytorch.org/whl/cpu \
    torch

# Install application dependencies without installing the local package yet.
RUN pip install --no-cache-dir \
    "pydantic>=2.13.5" \
    "sqlalchemy>=2.0.54" \
    "pymupdf>=1.28.2" \
    "openai>=1.0" \
    "python-dotenv>=1.2.3" \
    "fastapi>=0.117.1" \
    "uvicorn>=0.36.0" \
    "python-multipart" \
    "chromadb>=1.5.9" \
    "sentence-transformers>=6.1.0"

# Copy application source code.
COPY src ./src

# Create persistent vector database directory.
RUN mkdir -p /app/data/chroma

# Copy sample data.
COPY data/sample_invoice.json ./data/sample_invoice.json

EXPOSE 8000

CMD ["uvicorn", "invoice_buddy.api:app", "--host", "0.0.0.0", "--port", "8000"]