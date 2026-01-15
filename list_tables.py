from google.cloud import bigquery

# Initialize BigQuery client
client = bigquery.Client(project='molten-optics-310919')

# List all tables in the dataset
dataset_id = 'molten-optics-310919.kamiyabPakistan'

print(f"Listing tables in dataset: {dataset_id}\n")
tables = client.list_tables(dataset_id)

print("Available tables:")
for table in tables:
    print(f"  - {table.table_id}")
