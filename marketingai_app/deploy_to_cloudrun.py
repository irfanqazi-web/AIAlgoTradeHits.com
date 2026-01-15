"""
Deploy MarketingAI to Google Cloud Run
Run this script to deploy the application
"""

import subprocess
import sys

PROJECT_ID = 'aialgotradehits'
SERVICE_NAME = 'marketingai'
REGION = 'us-central1'

def run_command(cmd, description):
    print(f"\n{'='*50}")
    print(f"🚀 {description}")
    print(f"{'='*50}")
    print(f"Command: {cmd}")
    print()

    result = subprocess.run(cmd, shell=True, capture_output=False)
    return result.returncode == 0

def main():
    print("="*60)
    print("   MarketingAI - Cloud Run Deployment")
    print("="*60)

    # Step 1: Deploy to Cloud Run
    deploy_cmd = f"""gcloud run deploy {SERVICE_NAME} \
        --source . \
        --platform managed \
        --region {REGION} \
        --allow-unauthenticated \
        --memory 512Mi \
        --timeout 120 \
        --project {PROJECT_ID}"""

    if not run_command(deploy_cmd, "Deploying to Cloud Run"):
        print("❌ Deployment failed!")
        return False

    print("\n" + "="*60)
    print("✅ MarketingAI Deployed Successfully!")
    print("="*60)
    print(f"\nService URL: https://{SERVICE_NAME}-<hash>-{REGION.split('-')[0]}.a.run.app")
    print("\n📋 Next Steps:")
    print("1. Run setup_bigquery_schema.py from GCP Cloud Shell")
    print("2. Create admin user")
    print("3. Configure custom domain (optional)")

    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
