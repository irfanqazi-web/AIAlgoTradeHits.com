#!/bin/bash
# ============================================================
# STEP 1: ENABLE ALL REQUIRED APIs
# Run this in GCP Cloud Shell (project: aialgotradehits)
# ============================================================

PROJECT_ID="aialgotradehits"

echo "Setting project..."
gcloud config set project $PROJECT_ID

echo ""
echo "Enabling required APIs..."
echo "This may take 2-3 minutes..."
echo ""

# Core APIs
gcloud services enable bigquery.googleapis.com
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable cloudscheduler.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable secretmanager.googleapis.com

# AI/ML APIs (Vertex AI & Gemini)
gcloud services enable aiplatform.googleapis.com
gcloud services enable ml.googleapis.com
gcloud services enable notebooks.googleapis.com

# Additional APIs
gcloud services enable cloudresourcemanager.googleapis.com
gcloud services enable iam.googleapis.com

echo ""
echo "✅ STEP 1 COMPLETE: All APIs enabled!"
echo ""
echo "Run STEP 2 next..."
