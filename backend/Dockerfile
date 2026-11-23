FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (build-essential, libpq for psycopg2 if building from source)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency definition and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI via Uvicorn (uses Render's $PORT or defaults to 8000)
CMD ["sh", "-c", "python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
