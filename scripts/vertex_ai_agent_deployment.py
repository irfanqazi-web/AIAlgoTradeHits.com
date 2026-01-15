"""
Vertex AI Agent Engine Deployment Configuration
Following Google ADK Text-to-SQL Reference Guide Section 7

Developer: irfan.qazi@aialgotradehits.com

This module provides:
1. Deployment configuration for Vertex AI Agent Engine
2. Cloud Functions deployment for agent endpoints
3. Infrastructure setup scripts
4. Production deployment pipeline
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
import json
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional

# =============================================================================
# CONFIGURATION
# =============================================================================

# GCP Configuration
PROJECT_ID = 'aialgotradehits'
REGION = 'us-central1'
DATASET_ID = 'crypto_trading_data'

# Agent Configuration
AGENT_CONFIG = {
    'display_name': 'AIAlgoTradeHits Trading Agent',
    'description': 'Multi-agent trading analytics system with Text-to-SQL capabilities',
    'model': 'gemini-2.5-flash',
    'temperature': 0.1,
    'max_output_tokens': 8192,
}

# Cloud Function Configuration
FUNCTION_CONFIG = {
    'runtime': 'python312',
    'memory': '512MB',
    'timeout': '300s',
    'max_instances': 100,
    'min_instances': 0,
}

# MCP Toolbox Configuration
MCP_CONFIG = {
    'toolbox_version': '0.3.0',
    'sources': {
        'bigquery-trading': {
            'kind': 'bigquery',
            'project': PROJECT_ID,
            'dataset': DATASET_ID,
        }
    }
}

# =============================================================================
# DEPLOYMENT FILES
# =============================================================================

def generate_requirements_txt() -> str:
    """Generate requirements.txt for Cloud Functions."""
    return """# AIAlgoTradeHits Trading Agent Dependencies
# Generated: {date}

# Google Cloud
google-cloud-bigquery>=3.13.0
google-cloud-aiplatform>=1.38.0
google-cloud-storage>=2.13.0

# Google AI SDK
google-genai>=0.3.0

# ADK Framework
google-adk>=0.3.0

# Utilities
pyyaml>=6.0
python-dateutil>=2.8.2
requests>=2.31.0

# Data Processing
pandas>=2.0.0
numpy>=1.24.0
""".format(date=datetime.now().strftime('%Y-%m-%d'))


def generate_cloud_function_main() -> str:
    """Generate main.py for Cloud Functions deployment."""
    return '''"""
AIAlgoTradeHits Trading Agent - Cloud Function Entry Point
Deployed to: {project}.{region}
"""

import os
import json
import functions_framework
from flask import jsonify
from datetime import datetime

# Import trading agents
from adk_complete_trading_agents import (
    scan_market,
    get_trading_opportunities,
    analyze_asset,
    TradingTextToSQLAgent
)
from bigquery_nl2sql_integration import BigQueryNL2SQL

# Initialize NL2SQL engine (cached)
_nl2sql_engine = None

def get_nl2sql_engine():
    global _nl2sql_engine
    if _nl2sql_engine is None:
        api_key = os.environ.get('GEMINI_API_KEY')
        _nl2sql_engine = BigQueryNL2SQL(api_key=api_key)
    return _nl2sql_engine


@functions_framework.http
def trading_agent(request):
    """
    Main entry point for trading agent HTTP requests.

    Endpoints:
    - POST /query - Natural language query
    - POST /scan - Market scan
    - POST /analyze - Analyze specific asset
    - GET /health - Health check
    """
    # CORS headers
    headers = {{
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    }}

    # Handle preflight
    if request.method == 'OPTIONS':
        return ('', 204, headers)

    # Parse request
    path = request.path.strip('/')

    try:
        if request.method == 'GET':
            if path == 'health':
                return jsonify({{
                    'status': 'healthy',
                    'timestamp': datetime.now().isoformat(),
                    'version': '1.0.0'
                }}), 200, headers

            return jsonify({{'error': 'Invalid endpoint'}}), 404, headers

        # POST requests
        data = request.get_json(silent=True) or {{}}

        if path == 'query':
            # Natural language query
            query = data.get('query', '')
            if not query:
                return jsonify({{'error': 'Query required'}}), 400, headers

            engine = get_nl2sql_engine()
            result = engine.query(query, execute=True)
            return jsonify(result), 200, headers

        elif path == 'scan':
            # Market scan
            scan_type = data.get('scan_type', 'oversold')
            asset_type = data.get('asset_type', 'stocks')
            limit = data.get('limit', 20)

            result = scan_market(scan_type, asset_type, limit)
            return jsonify(result), 200, headers

        elif path == 'analyze':
            # Analyze asset
            symbol = data.get('symbol', '')
            asset_type = data.get('asset_type', 'stocks')

            if not symbol:
                return jsonify({{'error': 'Symbol required'}}), 400, headers

            signal = analyze_asset(symbol, asset_type)
            return jsonify({{
                'symbol': signal.symbol,
                'signal': signal.signal,
                'strength': signal.strength,
                'price': signal.price,
                'indicators': signal.indicators,
                'reasons': signal.reasons,
                'timestamp': signal.timestamp.isoformat()
            }}), 200, headers

        elif path == 'opportunities':
            # Get all trading opportunities
            asset_type = data.get('asset_type', 'stocks')
            result = get_trading_opportunities(asset_type)
            return jsonify(result), 200, headers

        else:
            return jsonify({{'error': 'Invalid endpoint'}}), 404, headers

    except Exception as e:
        return jsonify({{
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }}), 500, headers
'''.format(project=PROJECT_ID, region=REGION)


def generate_cloudbuild_yaml() -> str:
    """Generate cloudbuild.yaml for CI/CD."""
    return """# AIAlgoTradeHits Trading Agent - Cloud Build Configuration
# Triggers on push to main branch

steps:
  # Install dependencies
  - name: 'python:3.12'
    entrypoint: pip
    args: ['install', '-r', 'requirements.txt', '-t', '.']

  # Run tests
  - name: 'python:3.12'
    entrypoint: python
    args: ['-m', 'pytest', 'tests/', '-v']
    env:
      - 'PROJECT_ID={project}'

  # Deploy Cloud Function
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'functions'
      - 'deploy'
      - 'trading-agent'
      - '--gen2'
      - '--runtime=python312'
      - '--region={region}'
      - '--source=.'
      - '--entry-point=trading_agent'
      - '--trigger-http'
      - '--allow-unauthenticated'
      - '--memory=512MB'
      - '--timeout=300s'
      - '--set-env-vars=PROJECT_ID={project},DATASET_ID={dataset}'
      - '--set-secrets=GEMINI_API_KEY=gemini-api-key:latest'

timeout: '1200s'

options:
  logging: CLOUD_LOGGING_ONLY
""".format(project=PROJECT_ID, region=REGION, dataset=DATASET_ID)


def generate_agent_config_yaml() -> str:
    """Generate agent configuration for Vertex AI Agent Engine."""
    return """# AIAlgoTradeHits Trading Agent Configuration
# For Vertex AI Agent Engine deployment

apiVersion: v1
kind: AgentConfig
metadata:
  name: trading-agent
  displayName: AIAlgoTradeHits Trading Agent
  description: Multi-agent trading analytics with Text-to-SQL capabilities

spec:
  model:
    name: gemini-2.5-flash
    config:
      temperature: 0.1
      maxOutputTokens: 8192
      topP: 0.95

  systemInstruction: |
    You are an expert trading analyst for the AIAlgoTradeHits platform.

    Your capabilities:
    1. Convert natural language queries to BigQuery SQL
    2. Analyze technical indicators (RSI, MACD, ADX, Bollinger Bands)
    3. Generate trading signals (BUY, SELL, HOLD)
    4. Scan markets for opportunities

    Database: aialgotradehits.crypto_trading_data

    Available tables:
    - v2_stocks_daily: Daily stock data with 29 technical indicators
    - v2_crypto_daily: Daily cryptocurrency data
    - v2_forex_daily: Daily forex data
    - v2_etfs_daily: Daily ETF data
    - v2_indices_daily: Market index data
    - v2_commodities_daily: Commodity data

    Trading terminology:
    - oversold = RSI < 30
    - overbought = RSI > 70
    - strong trend = ADX > 25
    - bullish MACD = MACD > MACD_SIGNAL

  tools:
    # MCP Toolbox connection
    - type: mcpToolbox
      config:
        source: bigquery-trading
        project: {project}
        dataset: {dataset}

    # Custom function tools
    - type: function
      name: scan_market
      description: Scan market for trading opportunities
      parameters:
        scan_type:
          type: string
          enum: [oversold, overbought, gainers, losers, breakouts, strong_trends]
        asset_type:
          type: string
          enum: [stocks, crypto, forex, etfs, indices, commodities]
        limit:
          type: integer
          default: 20

    - type: function
      name: analyze_asset
      description: Perform technical analysis on a specific asset
      parameters:
        symbol:
          type: string
          required: true
        asset_type:
          type: string
          default: stocks

  subAgents:
    - name: market_data_agent
      description: Retrieves real-time market data
      model: gemini-2.5-flash

    - name: technical_analysis_agent
      description: Analyzes technical indicators
      model: gemini-2.5-flash

    - name: database_agent
      description: Executes BigQuery queries
      model: gemini-2.5-flash

    - name: signal_agent
      description: Generates trading signals
      model: gemini-2.5-flash

  orchestration:
    type: sequential
    pipeline:
      - parallel:
          - market_data_agent
          - database_agent
      - technical_analysis_agent
      - signal_agent
""".format(project=PROJECT_ID, dataset=DATASET_ID)


def generate_terraform_config() -> str:
    """Generate Terraform configuration for infrastructure."""
    return """# AIAlgoTradeHits Trading Agent - Terraform Configuration
# Deploys all required GCP infrastructure

terraform {{
  required_providers {{
    google = {{
      source  = "hashicorp/google"
      version = "~> 5.0"
    }}
  }}
}}

provider "google" {{
  project = "{project}"
  region  = "{region}"
}}

# Enable required APIs
resource "google_project_service" "apis" {{
  for_each = toset([
    "cloudfunctions.googleapis.com",
    "run.googleapis.com",
    "bigquery.googleapis.com",
    "aiplatform.googleapis.com",
    "secretmanager.googleapis.com",
    "cloudbuild.googleapis.com",
  ])

  service = each.value
  disable_on_destroy = false
}}

# Secret for Gemini API Key
resource "google_secret_manager_secret" "gemini_api_key" {{
  secret_id = "gemini-api-key"

  replication {{
    auto {{}}
  }}
}}

# Cloud Function for Trading Agent
resource "google_cloudfunctions2_function" "trading_agent" {{
  name     = "trading-agent"
  location = "{region}"

  build_config {{
    runtime     = "python312"
    entry_point = "trading_agent"
    source {{
      storage_source {{
        bucket = google_storage_bucket.function_source.name
        object = google_storage_bucket_object.function_zip.name
      }}
    }}
  }}

  service_config {{
    max_instance_count = 100
    min_instance_count = 0
    available_memory   = "512M"
    timeout_seconds    = 300

    environment_variables = {{
      PROJECT_ID = "{project}"
      DATASET_ID = "{dataset}"
    }}

    secret_environment_variables {{
      key        = "GEMINI_API_KEY"
      project_id = "{project}"
      secret     = google_secret_manager_secret.gemini_api_key.secret_id
      version    = "latest"
    }}
  }}

  depends_on = [google_project_service.apis]
}}

# Allow unauthenticated access
resource "google_cloud_run_service_iam_member" "public_access" {{
  location = google_cloudfunctions2_function.trading_agent.location
  service  = google_cloudfunctions2_function.trading_agent.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}}

# Storage bucket for function source
resource "google_storage_bucket" "function_source" {{
  name     = "{project}-function-source"
  location = "{region}"

  uniform_bucket_level_access = true
}}

# BigQuery Dataset (if not exists)
resource "google_bigquery_dataset" "trading_data" {{
  dataset_id = "{dataset}"
  location   = "US"

  labels = {{
    environment = "production"
    application = "trading-agent"
  }}
}}

# Cloud Scheduler for periodic scans
resource "google_cloud_scheduler_job" "daily_scan" {{
  name        = "daily-trading-scan"
  description = "Daily market scan for trading opportunities"
  schedule    = "0 9 * * 1-5"  # 9 AM weekdays
  time_zone   = "America/New_York"

  http_target {{
    http_method = "POST"
    uri         = "${{google_cloudfunctions2_function.trading_agent.service_config[0].uri}}/scan"
    body        = base64encode(jsonencode({{
      scan_type  = "oversold"
      asset_type = "stocks"
      limit      = 50
    }}))
    headers = {{
      "Content-Type" = "application/json"
    }}
  }}
}}

# Outputs
output "function_uri" {{
  value = google_cloudfunctions2_function.trading_agent.service_config[0].uri
}}

output "project_id" {{
  value = "{project}"
}}
""".format(project=PROJECT_ID, region=REGION, dataset=DATASET_ID)


# =============================================================================
# DEPLOYMENT SCRIPTS
# =============================================================================

def generate_deploy_script() -> str:
    """Generate deployment script for Windows/Linux."""
    return """#!/bin/bash
# AIAlgoTradeHits Trading Agent - Deployment Script
# Usage: ./deploy.sh [dev|staging|prod]

set -e

ENVIRONMENT=${{1:-dev}}
PROJECT_ID="{project}"
REGION="{region}"
FUNCTION_NAME="trading-agent"

echo "========================================"
echo "Deploying Trading Agent"
echo "Environment: $ENVIRONMENT"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "========================================"

# Set project
gcloud config set project $PROJECT_ID

# Enable APIs
echo "Enabling required APIs..."
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable secretmanager.googleapis.com

# Check for Gemini API key secret
echo "Checking secrets..."
if ! gcloud secrets describe gemini-api-key --quiet 2>/dev/null; then
    echo "Creating Gemini API key secret..."
    echo "Please enter your Gemini API key:"
    read -s GEMINI_KEY
    echo -n "$GEMINI_KEY" | gcloud secrets create gemini-api-key --data-file=-
fi

# Deploy Cloud Function
echo "Deploying Cloud Function..."
gcloud functions deploy $FUNCTION_NAME \\
    --gen2 \\
    --runtime=python312 \\
    --region=$REGION \\
    --source=. \\
    --entry-point=trading_agent \\
    --trigger-http \\
    --allow-unauthenticated \\
    --memory=512MB \\
    --timeout=300s \\
    --set-env-vars=PROJECT_ID=$PROJECT_ID,DATASET_ID={dataset} \\
    --set-secrets=GEMINI_API_KEY=gemini-api-key:latest

# Get function URL
FUNCTION_URL=$(gcloud functions describe $FUNCTION_NAME --region=$REGION --format='value(serviceConfig.uri)')

echo "========================================"
echo "Deployment Complete!"
echo "Function URL: $FUNCTION_URL"
echo ""
echo "Test endpoints:"
echo "  Health: curl $FUNCTION_URL/health"
echo "  Query:  curl -X POST $FUNCTION_URL/query -d '{{\\"query\\":\\"top 10 stock gainers\\"}}' -H 'Content-Type: application/json'"
echo "  Scan:   curl -X POST $FUNCTION_URL/scan -d '{{\\"scan_type\\":\\"oversold\\"}}' -H 'Content-Type: application/json'"
echo "========================================"
""".format(project=PROJECT_ID, region=REGION, dataset=DATASET_ID)


def generate_deploy_powershell() -> str:
    """Generate PowerShell deployment script for Windows."""
    return """# AIAlgoTradeHits Trading Agent - Deployment Script (PowerShell)
# Usage: .\\deploy.ps1 [-Environment dev|staging|prod]

param(
    [string]$Environment = "dev"
)

$ErrorActionPreference = "Stop"

$PROJECT_ID = "{project}"
$REGION = "{region}"
$FUNCTION_NAME = "trading-agent"
$DATASET_ID = "{dataset}"

Write-Host "========================================"
Write-Host "Deploying Trading Agent"
Write-Host "Environment: $Environment"
Write-Host "Project: $PROJECT_ID"
Write-Host "Region: $REGION"
Write-Host "========================================"

# Set project
gcloud config set project $PROJECT_ID

# Enable APIs
Write-Host "Enabling required APIs..."
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable secretmanager.googleapis.com

# Check for Gemini API key secret
Write-Host "Checking secrets..."
$secretExists = gcloud secrets describe gemini-api-key --quiet 2>$null
if (-not $secretExists) {{
    Write-Host "Creating Gemini API key secret..."
    $GEMINI_KEY = Read-Host -Prompt "Enter your Gemini API key" -AsSecureString
    $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($GEMINI_KEY)
    $PlainKey = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
    $PlainKey | gcloud secrets create gemini-api-key --data-file=-
}}

# Deploy Cloud Function
Write-Host "Deploying Cloud Function..."
gcloud functions deploy $FUNCTION_NAME `
    --gen2 `
    --runtime=python312 `
    --region=$REGION `
    --source=. `
    --entry-point=trading_agent `
    --trigger-http `
    --allow-unauthenticated `
    --memory=512MB `
    --timeout=300s `
    --set-env-vars="PROJECT_ID=$PROJECT_ID,DATASET_ID=$DATASET_ID" `
    --set-secrets="GEMINI_API_KEY=gemini-api-key:latest"

# Get function URL
$FUNCTION_URL = gcloud functions describe $FUNCTION_NAME --region=$REGION --format='value(serviceConfig.uri)'

Write-Host "========================================"
Write-Host "Deployment Complete!"
Write-Host "Function URL: $FUNCTION_URL"
Write-Host ""
Write-Host "Test endpoints:"
Write-Host "  Health: Invoke-RestMethod -Uri '$FUNCTION_URL/health'"
Write-Host "  Query:  Invoke-RestMethod -Uri '$FUNCTION_URL/query' -Method POST -Body (@{{query='top 10 stock gainers'}}|ConvertTo-Json) -ContentType 'application/json'"
Write-Host "========================================"
""".format(project=PROJECT_ID, region=REGION, dataset=DATASET_ID)


# =============================================================================
# MAIN FUNCTIONS
# =============================================================================

def create_deployment_package(output_dir: str = 'deployment_package'):
    """Create complete deployment package."""
    import os

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    files = {
        'requirements.txt': generate_requirements_txt(),
        'main.py': generate_cloud_function_main(),
        'cloudbuild.yaml': generate_cloudbuild_yaml(),
        'agent_config.yaml': generate_agent_config_yaml(),
        'main.tf': generate_terraform_config(),
        'deploy.sh': generate_deploy_script(),
        'deploy.ps1': generate_deploy_powershell(),
    }

    for filename, content in files.items():
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created: {filepath}")

    print(f"\nDeployment package created in: {output_dir}/")
    print("\nNext steps:")
    print("1. Set your Gemini API key as a secret in GCP")
    print("2. Run deploy.ps1 (Windows) or deploy.sh (Linux/Mac)")
    print("3. Test the endpoints with the provided curl commands")


def verify_gcp_setup() -> Dict[str, bool]:
    """Verify GCP setup and permissions."""
    checks = {
        'gcloud_installed': False,
        'project_set': False,
        'bigquery_access': False,
        'functions_enabled': False,
        'vertex_enabled': False,
    }

    try:
        # Check gcloud
        result = subprocess.run(['gcloud', '--version'], capture_output=True, text=True)
        checks['gcloud_installed'] = result.returncode == 0

        # Check project
        result = subprocess.run(['gcloud', 'config', 'get', 'project'], capture_output=True, text=True)
        checks['project_set'] = PROJECT_ID in result.stdout

        # Check BigQuery access
        result = subprocess.run([
            'gcloud', 'alpha', 'bq', 'datasets', 'describe',
            f'{PROJECT_ID}:{DATASET_ID}', '--format=json'
        ], capture_output=True, text=True)
        checks['bigquery_access'] = result.returncode == 0

        # Check Cloud Functions
        result = subprocess.run([
            'gcloud', 'services', 'list', '--enabled',
            '--filter=NAME:cloudfunctions.googleapis.com',
            '--format=value(NAME)'
        ], capture_output=True, text=True)
        checks['functions_enabled'] = 'cloudfunctions' in result.stdout

        # Check Vertex AI
        result = subprocess.run([
            'gcloud', 'services', 'list', '--enabled',
            '--filter=NAME:aiplatform.googleapis.com',
            '--format=value(NAME)'
        ], capture_output=True, text=True)
        checks['vertex_enabled'] = 'aiplatform' in result.stdout

    except Exception as e:
        print(f"Error during verification: {e}")

    return checks


def main():
    """Main entry point."""
    print("=" * 70)
    print("AIAlgoTradeHits Vertex AI Agent Deployment")
    print("Developer: irfan.qazi@aialgotradehits.com")
    print("=" * 70)

    print("\nVerifying GCP setup...")
    checks = verify_gcp_setup()

    print("\nSetup Status:")
    for check, status in checks.items():
        status_str = "OK" if status else "MISSING"
        print(f"  {check}: {status_str}")

    print("\nCreating deployment package...")
    create_deployment_package('agent_deployment')

    print("\n" + "=" * 70)
    print("DEPLOYMENT INSTRUCTIONS")
    print("=" * 70)
    print("""
1. PREREQUISITES:
   - Google Cloud SDK installed and configured
   - Gemini API key from https://aistudio.google.com/app/apikey
   - GCP project with billing enabled

2. DEPLOY:
   Windows:  cd agent_deployment && .\\deploy.ps1
   Linux:    cd agent_deployment && chmod +x deploy.sh && ./deploy.sh

3. TEST:
   # Health check
   curl https://trading-agent-xxx.a.run.app/health

   # Natural language query
   curl -X POST https://trading-agent-xxx.a.run.app/query \\
     -H "Content-Type: application/json" \\
     -d '{"query": "find oversold tech stocks"}'

   # Market scan
   curl -X POST https://trading-agent-xxx.a.run.app/scan \\
     -H "Content-Type: application/json" \\
     -d '{"scan_type": "breakouts", "asset_type": "stocks"}'

4. MONITOR:
   gcloud functions logs read trading-agent --region=us-central1

5. UPDATE:
   Re-run the deployment script to update the function
""")


if __name__ == "__main__":
    main()
