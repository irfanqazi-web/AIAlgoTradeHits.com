"""Deploy System Monitoring Cloud Function"""

import subprocess

PROJECT_ID = 'cryptobot-462709'
FUNCTION_NAME = 'system-monitoring'
REGION = 'us-central1'
RUNTIME = 'python311'
ENTRY_POINT = 'system_monitoring'
MEMORY = '512MB'
TIMEOUT = '300s'

env_vars = f"GCP_PROJECT_ID={PROJECT_ID},BIGQUERY_DATASET=crypto_trading_data"

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
    print(f"\nTest with:")
    print(f"curl 'https://{FUNCTION_NAME}-<hash>-uc.a.run.app?endpoint=full'")
except subprocess.CalledProcessError as e:
    print(f"\n❌ Deployment failed!")
    print(e.stderr)
