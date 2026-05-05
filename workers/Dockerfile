FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy worker code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 worker && \
    chown -R worker:worker /app

USER worker

# Run worker
CMD ["python", "worker.py"]