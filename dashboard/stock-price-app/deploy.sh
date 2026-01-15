#!/bin/bash

# Deployment script for Google Cloud Run
# Project: cryptobot-462709

echo "Starting deployment to Google Cloud Run..."

# Set the project
echo "Setting GCP project..."
gcloud config set project cryptobot-462709

# Enable required APIs (if not already enabled)
echo "Enabling Cloud Run API..."
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Deploy to Cloud Run
echo "Deploying application..."
gcloud run deploy stock-price-app \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10

echo "Deployment complete!"
echo "Your application URL will be displayed above."
