# ============================================================
# Vision-to-Cart V4 — Multi-Stage Dockerfile
# ============================================================

# ── Stage 1: Builder (install dependencies) ──────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system dependencies needed by some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python requirements
COPY requirements.txt .

# Install only the essential, lightweight packages
# (heavy optional ones like ultralytics/rembg are skipped — graceful fallback is built-in)
RUN pip install --upgrade pip --no-cache-dir && \
    pip install --no-cache-dir \
        fastapi>=0.110.0 \
        "uvicorn[standard]>=0.29.0" \
        pydantic>=2.0.0 \
        python-dotenv>=1.0.0 \
        Pillow>=10.0.0 \
        requests>=2.31.0 \
        chromadb>=0.5.0 \
        sentence-transformers>=3.0.0 \
        numpy>=1.24.0 \
        redis>=5.0.0 \
        openai>=1.30.0

# ── Stage 2: Runtime ─────────────────────────────────────────
FROM python:3.11-slim AS runtime

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Install minimal runtime system libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy all project source code
COPY . .

# Create necessary directories
RUN mkdir -p \
    data_services/vector_store \
    data_services/catalog \
    data_services/embeddings_cache \
    inputs

# Run catalog ingestion at container startup to pre-load vector DB
# (will be called in CMD via entrypoint script)

# Expose the FastAPI port
EXPOSE 8000

# Environment defaults (overridable via docker-compose / .env)
ENV PORT=8000 \
    HOST=0.0.0.0 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    CHROMADB_PERSIST_DIR=/app/data_services/vector_store \
    CATALOG_PATH=/app/data_services/catalog/catalog.json \
    ENRICHED_CATALOG_PATH=/app/data_services/catalog/catalog_enriched.json

# Entrypoint: ingest catalog then start the server
CMD ["sh", "-c", "python scripts/ingest_catalog.py && uvicorn mcp_server.main:app --host 0.0.0.0 --port 8000"]
