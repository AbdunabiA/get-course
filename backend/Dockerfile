# ---------- Stage 1: Builder ----------
FROM python:3.11-slim AS builder

# Env vars
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies (for psycopg2 / postgres / build tools)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# ---------- Stage 2: Runtime ----------
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy project
COPY . .

EXPOSE 8000

# Run Alembic migrations + start Gunicorn
CMD alembic upgrade head && \
    gunicorn -k uvicorn.workers.UvicornWorker app.main:app \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --timeout 60
