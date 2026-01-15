"""
Load KaamyabPakistan CSV data into BigQuery
"""
import pandas as pd
from google.cloud import bigquery

# Configuration - Using cryptobot project (no IAM issues)
PROJECT_ID = "cryptobot-462709"
DATASET_ID = "crypto_trading_data"
TABLE_ID = "kaamyabpakistan_opportunities"

# Initialize client
client = bigquery.Client(project=PROJECT_ID)

# Load CSV data
csv_path = "C:/1AITrading/Trading/sub_project_description.csv"
df = pd.read_csv(csv_path)

# Clean data - remove header duplicates and invalid entries
df = df[df['id'] != 'id']
df = df[df['id'] != 'undefined']
df = df.dropna(subset=['franchise', 'description'])

# Fill NaN values with empty strings
df = df.fillna('')

print(f"Loaded {len(df)} records from CSV")
print(f"Columns: {list(df.columns)}")

# Upload to BigQuery
table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

job_config = bigquery.LoadJobConfig(
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
)

try:
    job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
    job.result()  # Wait for job to complete

    table = client.get_table(table_ref)
    print(f"\nSuccess! Loaded {table.num_rows} rows into {table_ref}")

    # Show sample data
    query = f"SELECT franchise, type, description FROM `{table_ref}` LIMIT 5"
    results = client.query(query).result()
    print("\nSample data:")
    for row in results:
        print(f"  - {row.franchise[:50]}... ({row.type})")

except Exception as e:
    print(f"Error loading data: {e}")
