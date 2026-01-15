"""Deploy AI Trading Intelligence Cloud Function to aialgotradehits"""

import subprocess
import os
import sys
import io

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PROJECT_ID = 'aialgotradehits'
DATA_PROJECT_ID = 'cryptobot-462709'  # Where trading data lives
FUNCTION_NAME = 'ai-trading-intelligence'
REGION = 'us-central1'
RUNTIME = 'python311'
ENTRY_POINT = 'ai_trading_intelligence'
MEMORY = '2GB'
TIMEOUT = '540s'
SERVICE_ACCOUNT = 'algotradingservice@aialgotradehits.iam.gserviceaccount.com'

# API Keys
gemini_key = os.environ.get('GEMINI_API_KEY', 'AIzaSyBfmO5dBuRNYc-4w-McEw8cPnb6lr2pao8')
anthropic_key = os.environ.get('ANTHROPIC_API_KEY', '')

if not anthropic_key:
    print("\n⚠️  Warning: ANTHROPIC_API_KEY not set in environment")
    print("Vertex AI/Gemini will still work without it.")
    print("You can add it later using:")
    print(f"gcloud functions deploy {FUNCTION_NAME} --update-env-vars ANTHROPIC_API_KEY=your_key")
    print("\nGet your key from: https://console.anthropic.com/\n")

env_vars = f"GCP_PROJECT_ID={PROJECT_ID},DATA_PROJECT_ID={DATA_PROJECT_ID},BIGQUERY_DATASET=crypto_trading_data,VERTEX_AI_LOCATION={REGION},GEMINI_API_KEY={gemini_key}"

if anthropic_key:
    env_vars += f",ANTHROPIC_API_KEY={anthropic_key}"

deploy_command = [
    'gcloud', 'functions', 'deploy', FUNCTION_NAME,
    '--gen2',
    '--runtime', RUNTIME,
    '--region', REGION,
    '--source', '.',
    '--entry-point', ENTRY_POINT,
    '--trigger-http',
    '--allow-unauthenticated',
    '--memory', MEMORY,
    '--timeout', TIMEOUT,
    '--set-env-vars', env_vars,
    '--service-account', SERVICE_ACCOUNT,
    '--project', PROJECT_ID
]

print(f"Deploying {FUNCTION_NAME} to {PROJECT_ID}...")
print(f"Region: {REGION}")
print(f"Memory: {MEMORY}")
print(f"Timeout: {TIMEOUT}")
print("\nThis may take 3-5 minutes...\n")

try:
    result = subprocess.run(deploy_command, check=True, capture_output=True, text=True)
    print(result.stdout)
    print("\n✅ Deployment successful!")
    print(f"\n🔗 Function URL will be displayed above")
    print(f"\nTest with:")
    print(f"curl 'https://{FUNCTION_NAME}-<hash>-uc.a.run.app?pair=BTCUSD&type=prediction&ai_provider=vertex'")
except subprocess.CalledProcessError as e:
    print(f"\n❌ Deployment failed!")
    print(e.stderr)
