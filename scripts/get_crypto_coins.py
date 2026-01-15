from google.cloud import bigquery

# Initialize BigQuery client
client = bigquery.Client(project='molten-optics-310919')

# Query to get all crypto coins from the crypto_analysis table
query = """
SELECT DISTINCT *
FROM `molten-optics-310919.kamiyabPakistan.crypto_analysis`
"""

print("Fetching crypto coins from BigQuery...")
result = client.query(query).to_dataframe()

print(f"\nFound {len(result)} records in crypto_analysis table")
print("\nTable columns:")
print(result.columns.tolist())
print("\nFirst few rows:")
print(result.head(10))

# Save to CSV for reference
result.to_csv('crypto_coins_list.csv', index=False)
print(f"\nSaved full list to crypto_coins_list.csv")
