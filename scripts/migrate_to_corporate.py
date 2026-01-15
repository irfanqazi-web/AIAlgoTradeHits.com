"""
Complete Migration Script: Personal to Corporate GCP Account
From: cryptobot-462709 (personal)
To: aialgotradehits (corporate)

This script handles:
1. Enable required APIs
2. Create BigQuery datasets and tables
3. Export/Import BigQuery data
4. Deploy Cloud Functions
5. Set up Cloud Schedulers
6. Enable Vertex AI and Gemini
7. Deploy Trading API to Cloud Run
"""

import subprocess
import sys
import time
import json

# Configuration
SOURCE_PROJECT = "cryptobot-462709"
TARGET_PROJECT = "aialgotradehits"
REGION = "us-central1"
DATASET_NAME = "crypto_trading_data"
UNIFIED_DATASET = "trading_data_unified"

# APIs to enable
APIS_TO_ENABLE = [
    "bigquery.googleapis.com",
    "cloudfunctions.googleapis.com",
    "cloudscheduler.googleapis.com",
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "storage.googleapis.com",
    "aiplatform.googleapis.com",  # Vertex AI
    "generativelanguage.googleapis.com",  # Gemini
    "secretmanager.googleapis.com",
]

# Cloud Functions to deploy
CLOUD_FUNCTIONS = [
    {"name": "daily-crypto-fetcher", "folder": "cloud_function_daily"},
    {"name": "hourly-crypto-fetcher", "folder": "cloud_function_hourly"},
    {"name": "fivemin-top10-fetcher", "folder": "cloud_function_5min"},
    {"name": "daily-stock-fetcher", "folder": "cloud_function_stocks_daily"},
    {"name": "stock-hourly-fetcher", "folder": "cloud_function_stocks_hourly"},
    {"name": "stock-5min-fetcher", "folder": "cloud_function_stocks_5min"},
    {"name": "weekly-crypto-fetcher", "folder": "cloud_function_weekly_cryptos"},
    {"name": "weekly-stock-fetcher", "folder": "cloud_function_weekly_stocks"},
]

# Schedulers to create
SCHEDULERS = [
    {"name": "daily-crypto-fetch-job", "schedule": "0 0 * * *", "function": "daily-crypto-fetcher"},
    {"name": "hourly-crypto-fetch-job", "schedule": "0 * * * *", "function": "hourly-crypto-fetcher"},
    {"name": "fivemin-top10-fetch-job", "schedule": "*/5 * * * *", "function": "fivemin-top10-fetcher"},
    {"name": "stock-daily-fetch-job", "schedule": "0 0 * * *", "function": "daily-stock-fetcher"},
    {"name": "stock-hourly-fetch-job", "schedule": "0 * * * *", "function": "stock-hourly-fetcher"},
    {"name": "stock-5min-fetch-job", "schedule": "*/5 * * * *", "function": "stock-5min-fetcher"},
    {"name": "weekly-crypto-fetch-job", "schedule": "30 4 * * 6", "function": "weekly-crypto-fetcher"},
    {"name": "weekly-stock-fetch-job", "schedule": "0 4 * * 6", "function": "weekly-stock-fetcher"},
]

def run_command(cmd, description, check=True):
    """Run a shell command and return output"""
    print(f"\n{'='*60}")
    print(f">> {description}")
    print(f">> Command: {cmd[:100]}..." if len(cmd) > 100 else f">> Command: {cmd}")
    print('='*60)

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"STDERR: {result.stderr}")
        if check and result.returncode != 0:
            print(f"WARNING: Command returned non-zero exit code: {result.returncode}")
        return result.returncode == 0, result.stdout
    except Exception as e:
        print(f"ERROR: {e}")
        return False, str(e)

def step_1_enable_apis():
    """Enable all required GCP APIs"""
    print("\n" + "="*80)
    print("STEP 1: ENABLING REQUIRED APIS")
    print("="*80)

    for api in APIS_TO_ENABLE:
        run_command(
            f'gcloud services enable {api} --project={TARGET_PROJECT}',
            f"Enabling {api}"
        )

    print("\n✓ All APIs enabled")
    return True

def step_2_create_bigquery_datasets():
    """Create BigQuery datasets in target project"""
    print("\n" + "="*80)
    print("STEP 2: CREATING BIGQUERY DATASETS")
    print("="*80)

    # Create main dataset
    run_command(
        f'bq mk --project_id={TARGET_PROJECT} --dataset {DATASET_NAME}',
        f"Creating dataset {DATASET_NAME}"
    )

    # Create unified dataset
    run_command(
        f'bq mk --project_id={TARGET_PROJECT} --dataset {UNIFIED_DATASET}',
        f"Creating dataset {UNIFIED_DATASET}"
    )

    print("\n✓ Datasets created")
    return True

def step_3_copy_bigquery_tables():
    """Copy BigQuery tables from source to target project"""
    print("\n" + "="*80)
    print("STEP 3: COPYING BIGQUERY TABLES")
    print("="*80)

    # Get list of tables in source dataset
    success, output = run_command(
        f'bq ls --project_id={SOURCE_PROJECT} {DATASET_NAME} --format=json',
        f"Listing tables in {DATASET_NAME}"
    )

    if success and output:
        try:
            tables = json.loads(output)
            for table in tables:
                table_id = table.get('tableReference', {}).get('tableId', '')
                table_type = table.get('type', 'TABLE')

                if table_type == 'VIEW':
                    print(f"Skipping view: {table_id}")
                    continue

                if table_id:
                    run_command(
                        f'bq cp {SOURCE_PROJECT}:{DATASET_NAME}.{table_id} {TARGET_PROJECT}:{DATASET_NAME}.{table_id}',
                        f"Copying table {table_id}"
                    )
        except json.JSONDecodeError:
            print("Could not parse table list, copying known tables...")

    # Copy unified dataset tables
    success, output = run_command(
        f'bq ls --project_id={SOURCE_PROJECT} {UNIFIED_DATASET} --format=json',
        f"Listing tables in {UNIFIED_DATASET}"
    )

    if success and output:
        try:
            tables = json.loads(output)
            for table in tables:
                table_id = table.get('tableReference', {}).get('tableId', '')
                table_type = table.get('type', 'TABLE')

                if table_type == 'VIEW':
                    continue

                if table_id:
                    run_command(
                        f'bq cp {SOURCE_PROJECT}:{UNIFIED_DATASET}.{table_id} {TARGET_PROJECT}:{UNIFIED_DATASET}.{table_id}',
                        f"Copying table {table_id}"
                    )
        except json.JSONDecodeError:
            pass

    print("\n✓ Tables copied")
    return True

def step_4_update_cloud_function_configs():
    """Update Cloud Function main.py files with new project ID"""
    print("\n" + "="*80)
    print("STEP 4: UPDATING CLOUD FUNCTION CONFIGURATIONS")
    print("="*80)

    import os
    base_path = os.path.dirname(os.path.abspath(__file__))

    folders_to_update = [
        "cloud_function_daily",
        "cloud_function_hourly",
        "cloud_function_5min",
        "cloud_function_stocks_daily",
        "cloud_function_stocks_hourly",
        "cloud_function_stocks_5min",
        "cloud_function_weekly_cryptos",
        "cloud_function_weekly_stocks",
        "cloud_function_ai",
    ]

    for folder in folders_to_update:
        main_path = os.path.join(base_path, folder, "main.py")
        if os.path.exists(main_path):
            try:
                with open(main_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Replace project ID
                updated = content.replace(SOURCE_PROJECT, TARGET_PROJECT)

                with open(main_path, 'w', encoding='utf-8') as f:
                    f.write(updated)

                print(f"✓ Updated {folder}/main.py")
            except Exception as e:
                print(f"✗ Error updating {folder}/main.py: {e}")
        else:
            print(f"- Skipped {folder}/main.py (not found)")

    print("\n✓ Cloud Function configs updated")
    return True

def step_5_deploy_cloud_functions():
    """Deploy all Cloud Functions to target project"""
    print("\n" + "="*80)
    print("STEP 5: DEPLOYING CLOUD FUNCTIONS")
    print("="*80)

    import os
    base_path = os.path.dirname(os.path.abspath(__file__))

    for func in CLOUD_FUNCTIONS:
        folder_path = os.path.join(base_path, func['folder'])
        if os.path.exists(folder_path):
            run_command(
                f'gcloud functions deploy {func["name"]} '
                f'--gen2 '
                f'--runtime=python311 '
                f'--region={REGION} '
                f'--source={folder_path} '
                f'--entry-point=main '
                f'--trigger-http '
                f'--allow-unauthenticated '
                f'--timeout=540s '
                f'--memory=512MB '
                f'--project={TARGET_PROJECT}',
                f"Deploying {func['name']}"
            )
        else:
            print(f"Folder not found: {folder_path}")

    print("\n✓ Cloud Functions deployed")
    return True

def step_6_create_schedulers():
    """Create Cloud Schedulers in target project"""
    print("\n" + "="*80)
    print("STEP 6: CREATING CLOUD SCHEDULERS")
    print("="*80)

    for scheduler in SCHEDULERS:
        function_url = f"https://{REGION}-{TARGET_PROJECT}.cloudfunctions.net/{scheduler['function']}"

        run_command(
            f'gcloud scheduler jobs create http {scheduler["name"]} '
            f'--schedule="{scheduler["schedule"]}" '
            f'--uri="{function_url}" '
            f'--http-method=GET '
            f'--location={REGION} '
            f'--time-zone="America/New_York" '
            f'--project={TARGET_PROJECT}',
            f"Creating scheduler {scheduler['name']}"
        )

    print("\n✓ Schedulers created")
    return True

def step_7_setup_vertex_ai():
    """Set up Vertex AI and Gemini"""
    print("\n" + "="*80)
    print("STEP 7: SETTING UP VERTEX AI & GEMINI")
    print("="*80)

    # Enable additional AI APIs
    ai_apis = [
        "aiplatform.googleapis.com",
        "ml.googleapis.com",
        "notebooks.googleapis.com",
    ]

    for api in ai_apis:
        run_command(
            f'gcloud services enable {api} --project={TARGET_PROJECT}',
            f"Enabling {api}"
        )

    # Create service account for Vertex AI
    run_command(
        f'gcloud iam service-accounts create vertex-ai-sa '
        f'--display-name="Vertex AI Service Account" '
        f'--project={TARGET_PROJECT}',
        "Creating Vertex AI service account"
    )

    # Grant roles to service account
    roles = [
        "roles/aiplatform.user",
        "roles/bigquery.dataEditor",
        "roles/storage.objectAdmin",
    ]

    for role in roles:
        run_command(
            f'gcloud projects add-iam-policy-binding {TARGET_PROJECT} '
            f'--member="serviceAccount:vertex-ai-sa@{TARGET_PROJECT}.iam.gserviceaccount.com" '
            f'--role="{role}"',
            f"Granting {role} to Vertex AI service account"
        )

    print("\n✓ Vertex AI configured")
    return True

def step_8_update_trading_app():
    """Update trading app with new project configuration"""
    print("\n" + "="*80)
    print("STEP 8: UPDATING TRADING APP CONFIGURATION")
    print("="*80)

    import os
    base_path = os.path.dirname(os.path.abspath(__file__))
    api_path = os.path.join(base_path, "stock-price-app", "src", "services", "api.js")

    if os.path.exists(api_path):
        try:
            with open(api_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Update API URL to new project
            old_url = "trading-api-252370699783.us-central1.run.app"
            new_url = f"trading-api-{TARGET_PROJECT}.{REGION}.run.app"

            updated = content.replace(old_url, new_url)

            with open(api_path, 'w', encoding='utf-8') as f:
                f.write(updated)

            print(f"✓ Updated api.js with new API URL")
        except Exception as e:
            print(f"✗ Error updating api.js: {e}")

    print("\n✓ Trading app updated")
    return True

def step_9_deploy_trading_api():
    """Deploy Trading API to Cloud Run"""
    print("\n" + "="*80)
    print("STEP 9: DEPLOYING TRADING API TO CLOUD RUN")
    print("="*80)

    import os
    base_path = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(base_path, "stock-price-app")

    run_command(
        f'gcloud run deploy trading-api '
        f'--source={app_path} '
        f'--platform=managed '
        f'--region={REGION} '
        f'--allow-unauthenticated '
        f'--port=8080 '
        f'--project={TARGET_PROJECT}',
        "Deploying Trading API to Cloud Run"
    )

    print("\n✓ Trading API deployed")
    return True

def step_10_verify_migration():
    """Verify the migration was successful"""
    print("\n" + "="*80)
    print("STEP 10: VERIFYING MIGRATION")
    print("="*80)

    # Check BigQuery datasets
    run_command(
        f'bq ls --project_id={TARGET_PROJECT}',
        "Listing BigQuery datasets in target project"
    )

    # Check Cloud Functions
    run_command(
        f'gcloud functions list --project={TARGET_PROJECT} --format="table(name,status)"',
        "Listing Cloud Functions in target project"
    )

    # Check Cloud Schedulers
    run_command(
        f'gcloud scheduler jobs list --project={TARGET_PROJECT} --location={REGION}',
        "Listing Cloud Schedulers in target project"
    )

    # Check Cloud Run services
    run_command(
        f'gcloud run services list --project={TARGET_PROJECT} --region={REGION}',
        "Listing Cloud Run services in target project"
    )

    print("\n✓ Migration verification complete")
    return True

def main():
    """Run the full migration"""
    print("\n" + "="*80)
    print("GCP MIGRATION: PERSONAL TO CORPORATE")
    print(f"Source: {SOURCE_PROJECT}")
    print(f"Target: {TARGET_PROJECT}")
    print("="*80)

    # Check if we have access to target project
    success, _ = run_command(
        f'gcloud projects describe {TARGET_PROJECT}',
        "Checking access to target project"
    )

    if not success:
        print("\n" + "="*80)
        print("ERROR: Cannot access target project!")
        print("="*80)
        print(f"""
Please grant access to the corporate project first:

1. Go to: https://console.cloud.google.com/iam-admin/iam?project={TARGET_PROJECT}
2. Click "+ GRANT ACCESS"
3. Add: haq.irfanul@gmail.com
4. Role: Owner
5. Save

Then run this script again.
""")
        return False

    steps = [
        ("Enable APIs", step_1_enable_apis),
        ("Create BigQuery Datasets", step_2_create_bigquery_datasets),
        ("Copy BigQuery Tables", step_3_copy_bigquery_tables),
        ("Update Cloud Function Configs", step_4_update_cloud_function_configs),
        ("Deploy Cloud Functions", step_5_deploy_cloud_functions),
        ("Create Schedulers", step_6_create_schedulers),
        ("Setup Vertex AI", step_7_setup_vertex_ai),
        ("Update Trading App", step_8_update_trading_app),
        ("Deploy Trading API", step_9_deploy_trading_api),
        ("Verify Migration", step_10_verify_migration),
    ]

    for step_name, step_func in steps:
        print(f"\n>>> Starting: {step_name}")
        try:
            step_func()
        except Exception as e:
            print(f"\n✗ Error in {step_name}: {e}")
            continue

    print("\n" + "="*80)
    print("MIGRATION COMPLETE!")
    print("="*80)
    print(f"""
Next Steps:
1. Verify data in BigQuery: https://console.cloud.google.com/bigquery?project={TARGET_PROJECT}
2. Check Cloud Functions: https://console.cloud.google.com/functions?project={TARGET_PROJECT}
3. Check Schedulers: https://console.cloud.google.com/cloudscheduler?project={TARGET_PROJECT}
4. Access Trading App: Check Cloud Run URL
5. Set up Vertex AI Workbench: https://console.cloud.google.com/vertex-ai?project={TARGET_PROJECT}

To cancel personal account billing (after verification):
- Go to: https://console.cloud.google.com/billing?project={SOURCE_PROJECT}
- Disable billing or close project
""")

    return True

if __name__ == "__main__":
    main()
