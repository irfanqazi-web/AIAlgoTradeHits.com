FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# Cloud Run expects the service to listen on PORT
ENV PORT=8080

# Use gunicorn with extended timeout (3600s = 1 hour)
CMD exec gunicorn --bind :$PORT --workers 1 --threads 4 --timeout 3600 main:app
