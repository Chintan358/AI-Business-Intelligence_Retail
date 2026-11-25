FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency specifications
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and dataset
COPY . .

# Set Python path to ensure backend modules resolve properly
ENV PYTHONPATH=/app

EXPOSE 8000

# Run database initialization/migrations and start FastAPI with dynamic port binding for Render
CMD ["sh", "-c", "python backend/init_db.py && uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
