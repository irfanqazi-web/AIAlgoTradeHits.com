"""Deploy fundamentals fetcher to Cloud Functions"""
import subprocess
import os

FUNCTION_NAME = "fundamentals-fetcher"
REGION = "us-central1"
PROJECT_ID = "aialgotradehits"
ENTRY_POINT = "fundamentals_fetcher"

os.chdir(os.path.dirname(os.path.abspath(__file__)))

cmd = f"""gcloud functions deploy {FUNCTION_NAME} \
    --gen2 \
    --runtime=python311 \
    --region={REGION} \
    --source=. \
    --entry-point={ENTRY_POINT} \
    --trigger-http \
    --allow-unauthenticated \
    --memory=512MB \
    --timeout=540s \
    --project={PROJECT_ID}"""

print(f"Deploying {FUNCTION_NAME}...")
subprocess.run(cmd, shell=True)
print("Deployment complete!")
