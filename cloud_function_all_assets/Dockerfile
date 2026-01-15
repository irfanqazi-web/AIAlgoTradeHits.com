FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

ENV PORT=8080
ENV GCP_PROJECT=aialgotradehits

EXPOSE 8080

CMD exec functions-framework --target=main --port=$PORT
