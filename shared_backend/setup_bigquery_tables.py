"""
BigQuery Table Setup for Unified Platform
Creates all required tables for: KaamyabPakistan, YouInvent, HomeFranchise, NoCodeAI
"""

from google.cloud import bigquery
import sys

PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'kaamyabpakistan_data'

client = bigquery.Client(project=PROJECT_ID)
dataset_ref = f"{PROJECT_ID}.{DATASET_ID}"

# Table schemas
TABLES = {
    # Shared Users Table
    'users': [
        bigquery.SchemaField('user_id', 'INTEGER', mode='REQUIRED'),
        bigquery.SchemaField('username', 'STRING', mode='REQUIRED'),
        bigquery.SchemaField('email', 'STRING', mode='REQUIRED'),
        bigquery.SchemaField('password_hash', 'STRING', mode='REQUIRED'),
        bigquery.SchemaField('role', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('platform', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('is_active', 'BOOLEAN', mode='NULLABLE'),
        bigquery.SchemaField('created_at', 'TIMESTAMP', mode='NULLABLE'),
        bigquery.SchemaField('updated_at', 'TIMESTAMP', mode='NULLABLE'),
    ],

    # YouInvent - Inventions Table
    'inventions': [
        bigquery.SchemaField('invention_id', 'INTEGER', mode='REQUIRED'),
        bigquery.SchemaField('title', 'STRING', mode='REQUIRED'),
        bigquery.SchemaField('category', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('description', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('problem_solved', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('development_stage', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('investment_needed', 'INTEGER', mode='NULLABLE'),
        bigquery.SchemaField('unique_features', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('patent_status', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('prototype_ready', 'BOOLEAN', mode='NULLABLE'),
        bigquery.SchemaField('inventor_id', 'INTEGER', mode='NULLABLE'),
        bigquery.SchemaField('inventor_email', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('status', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('views', 'INTEGER', mode='NULLABLE'),
        bigquery.SchemaField('submitted_at', 'TIMESTAMP', mode='NULLABLE'),
        bigquery.SchemaField('updated_at', 'TIMESTAMP', mode='NULLABLE'),
    ],

    # HomeFranchise - Franchises Table
    'franchises': [
        bigquery.SchemaField('franchise_id', 'INTEGER', mode='REQUIRED'),
        bigquery.SchemaField('business_name', 'STRING', mode='REQUIRED'),
        bigquery.SchemaField('category', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('description', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('investment_min', 'INTEGER', mode='NULLABLE'),
        bigquery.SchemaField('investment_max', 'INTEGER', mode='NULLABLE'),
        bigquery.SchemaField('franchise_fee', 'INTEGER', mode='NULLABLE'),
        bigquery.SchemaField('royalty_percent', 'FLOAT', mode='NULLABLE'),
        bigquery.SchemaField('locations_available', 'INTEGER', mode='NULLABLE'),
        bigquery.SchemaField('training_provided', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('support_provided', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('requirements', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('contact_email', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('contact_phone', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('website', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('owner_id', 'INTEGER', mode='NULLABLE'),
        bigquery.SchemaField('owner_email', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('status', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('views', 'INTEGER', mode='NULLABLE'),
        bigquery.SchemaField('applications_count', 'INTEGER', mode='NULLABLE'),
        bigquery.SchemaField('created_at', 'TIMESTAMP', mode='NULLABLE'),
        bigquery.SchemaField('updated_at', 'TIMESTAMP', mode='NULLABLE'),
    ],

    # HomeFranchise - Franchise Applications Table
    'franchise_applications': [
        bigquery.SchemaField('application_id', 'INTEGER', mode='REQUIRED'),
        bigquery.SchemaField('franchise_id', 'INTEGER', mode='REQUIRED'),
        bigquery.SchemaField('applicant_id', 'INTEGER', mode='NULLABLE'),
        bigquery.SchemaField('applicant_email', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('applicant_name', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('phone', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('city', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('investment_capacity', 'INTEGER', mode='NULLABLE'),
        bigquery.SchemaField('experience', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('message', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('status', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('created_at', 'TIMESTAMP', mode='NULLABLE'),
        bigquery.SchemaField('updated_at', 'TIMESTAMP', mode='NULLABLE'),
    ],

    # NoCodeAI - Consulting Requests Table
    'consulting_requests': [
        bigquery.SchemaField('request_id', 'INTEGER', mode='REQUIRED'),
        bigquery.SchemaField('user_id', 'INTEGER', mode='NULLABLE'),
        bigquery.SchemaField('name', 'STRING', mode='REQUIRED'),
        bigquery.SchemaField('email', 'STRING', mode='REQUIRED'),
        bigquery.SchemaField('company', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('phone', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('service_type', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('budget_range', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('timeline', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('description', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('preferred_consultant', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('status', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('admin_notes', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('assigned_consultant', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('created_at', 'TIMESTAMP', mode='NULLABLE'),
        bigquery.SchemaField('updated_at', 'TIMESTAMP', mode='NULLABLE'),
    ],

    # NoCodeAI - Client Projects Table
    'client_projects': [
        bigquery.SchemaField('project_id', 'INTEGER', mode='REQUIRED'),
        bigquery.SchemaField('request_id', 'INTEGER', mode='NULLABLE'),
        bigquery.SchemaField('client_name', 'STRING', mode='REQUIRED'),
        bigquery.SchemaField('client_email', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('project_name', 'STRING', mode='REQUIRED'),
        bigquery.SchemaField('description', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('service_type', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('budget', 'FLOAT', mode='NULLABLE'),
        bigquery.SchemaField('start_date', 'TIMESTAMP', mode='NULLABLE'),
        bigquery.SchemaField('estimated_end_date', 'TIMESTAMP', mode='NULLABLE'),
        bigquery.SchemaField('actual_end_date', 'TIMESTAMP', mode='NULLABLE'),
        bigquery.SchemaField('assigned_consultant', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('status', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('created_at', 'TIMESTAMP', mode='NULLABLE'),
        bigquery.SchemaField('updated_at', 'TIMESTAMP', mode='NULLABLE'),
    ],

    # KaamyabPakistan - Investors Table
    'investors': [
        bigquery.SchemaField('investor_id', 'INTEGER', mode='REQUIRED'),
        bigquery.SchemaField('name', 'STRING', mode='REQUIRED'),
        bigquery.SchemaField('email', 'STRING', mode='REQUIRED'),
        bigquery.SchemaField('investor_type', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('investment_range', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('interests', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('message', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('status', 'STRING', mode='NULLABLE'),
        bigquery.SchemaField('created_at', 'TIMESTAMP', mode='NULLABLE'),
        bigquery.SchemaField('updated_at', 'TIMESTAMP', mode='NULLABLE'),
    ],
}


def create_table(table_name, schema):
    """Create a BigQuery table if it doesn't exist."""
    table_id = f"{dataset_ref}.{table_name}"

    try:
        client.get_table(table_id)
        print(f"  [EXISTS] {table_name}")
        return False
    except Exception:
        pass

    table = bigquery.Table(table_id, schema=schema)
    client.create_table(table)
    print(f"  [CREATED] {table_name}")
    return True


def main():
    print("=" * 50)
    print("  Unified Platform - BigQuery Table Setup")
    print("=" * 50)
    print(f"  Project: {PROJECT_ID}")
    print(f"  Dataset: {DATASET_ID}")
    print("=" * 50)

    # Ensure dataset exists
    try:
        client.get_dataset(dataset_ref)
        print(f"\nDataset '{DATASET_ID}' exists.")
    except Exception:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"
        client.create_dataset(dataset)
        print(f"\nDataset '{DATASET_ID}' created.")

    print("\nCreating tables...")

    created_count = 0
    for table_name, schema in TABLES.items():
        if create_table(table_name, schema):
            created_count += 1

    print("\n" + "=" * 50)
    print(f"  Setup complete! {created_count} tables created.")
    print("=" * 50)


if __name__ == '__main__':
    main()
