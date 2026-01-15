# AIAlgoTradeHits Trading Agent - Cloud Run Container
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared AI modules
COPY shared_ai_modules /app/shared_ai_modules

# Copy application code
COPY main.py .

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV GCP_PROJECT_ID=aialgotradehits

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "main.py"]
