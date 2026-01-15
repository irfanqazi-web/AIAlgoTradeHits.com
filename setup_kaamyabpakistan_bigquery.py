"""
Setup KaamyabPakistan BigQuery Dataset in AIAlgoTradeHits project
"""
import os
import pandas as pd
from google.cloud import bigquery

# Configuration
PROJECT_ID = "aialgotradehits"
DATASET_ID = "kaamyabpakistan"
LOCATION = "US"

# Initialize client
client = bigquery.Client(project=PROJECT_ID)

# Create dataset
dataset_id = f"{PROJECT_ID}.{DATASET_ID}"
dataset = bigquery.Dataset(dataset_id)
dataset.location = LOCATION
dataset.description = "KaamyabPakistan - Business opportunities for Pakistani entrepreneurs"

try:
    dataset = client.create_dataset(dataset, exists_ok=True)
    print(f"Dataset {dataset_id} created successfully!")
except Exception as e:
    print(f"Error creating dataset: {e}")
    # Try without IAM settings
    try:
        dataset = client.create_dataset(dataset, timeout=30)
        print(f"Dataset {dataset_id} created (retry)!")
    except Exception as e2:
        print(f"Retry failed: {e2}")

# Load CSV data
csv_path = "C:/1AITrading/Trading/sub_project_description.csv"
df = pd.read_csv(csv_path)

# Clean data
df = df[df['id'] != 'id']  # Remove header duplicates
df = df[df['id'] != 'undefined']
df = df.dropna(subset=['franchise', 'description'])

print(f"Loaded {len(df)} records from CSV")
print(f"Columns: {list(df.columns)}")

# Define table schema
table_id = f"{PROJECT_ID}.{DATASET_ID}.business_opportunities"

schema = [
    bigquery.SchemaField("id", "STRING"),
    bigquery.SchemaField("sub_id", "STRING"),
    bigquery.SchemaField("franchise", "STRING"),
    bigquery.SchemaField("type", "STRING"),
    bigquery.SchemaField("members", "STRING"),
    bigquery.SchemaField("foreign_jobs", "STRING"),
    bigquery.SchemaField("domestic_jobs", "STRING"),
    bigquery.SchemaField("export_market_size", "STRING"),
    bigquery.SchemaField("domestic_market_rs", "STRING"),
    bigquery.SchemaField("problem_statement", "STRING"),
    bigquery.SchemaField("description", "STRING"),
    bigquery.SchemaField("people_impact", "STRING"),
    bigquery.SchemaField("financial_impact", "STRING"),
    bigquery.SchemaField("edited_by", "STRING"),
    bigquery.SchemaField("edited_date", "STRING"),
    bigquery.SchemaField("is_deleted", "STRING"),
    bigquery.SchemaField("createdAt", "STRING"),
    bigquery.SchemaField("updatedAt", "STRING"),
]

# Create table and load data
try:
    job_config = bigquery.LoadJobConfig(
        schema=schema,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )

    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()  # Wait for job to complete

    table = client.get_table(table_id)
    print(f"Table {table_id} created with {table.num_rows} rows")
except Exception as e:
    print(f"Error creating table: {e}")

# List datasets to verify
print("\nDatasets in project:")
for ds in client.list_datasets():
    print(f"  - {ds.dataset_id}")
