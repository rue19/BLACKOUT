FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

COPY . .

RUN chmod +x seed_on_startup.py 2>/dev/null || true

CMD ["sh", "-c", "python seed_on_startup.py && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
