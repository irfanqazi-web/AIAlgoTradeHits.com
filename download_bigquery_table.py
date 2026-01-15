from google.cloud import bigquery
import os

# Initialize BigQuery client
client = bigquery.Client(project='molten-optics-310919')

# Define table ID
table_id = 'molten-optics-310919.kamiyabPakistan.sub_project_description'

# Query to select all data from the table
query = f"SELECT * FROM `{table_id}`"

# Execute query and convert to dataframe
print(f"Downloading table: {table_id}")
df = client.query(query).to_dataframe()

# Save to CSV
output_file = 'sub_project_description.csv'
df.to_csv(output_file, index=False)

print(f"Successfully downloaded {len(df)} rows to {output_file}")
