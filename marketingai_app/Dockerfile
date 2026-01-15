# MarketingAI - Multi-User Social Media Content Creation Platform
# Cloud Run Dockerfile

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application code
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV PROJECT_ID=aialgotradehits
ENV GOOGLE_CLOUD_PROJECT=aialgotradehits

# Expose port
EXPOSE 8080

# Set working directory to backend for proper imports
WORKDIR /app/backend

# Run the application with gunicorn
CMD exec gunicorn --bind :$PORT --workers 2 --threads 4 --timeout 120 main:app
