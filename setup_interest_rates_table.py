"""
Setup Interest Rates BigQuery Table and Upload G20 Data
Organizes data by daily and hourly timeframes
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import json
from datetime import datetime, timedelta
from google.cloud import bigquery
from google.oauth2 import service_account

# Configuration
PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'crypto_trading_data'
TABLE_ID = 'interest_rates'
CREDENTIALS_FILE = 'aialgotradehits-8863a22a9958.json'

def get_bigquery_client():
    """Get BigQuery client with service account credentials"""
    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE,
        scopes=["https://www.googleapis.com/auth/bigquery"]
    )
    return bigquery.Client(credentials=credentials, project=PROJECT_ID)

def create_interest_rates_table():
    """Create the interest_rates table in BigQuery"""
    client = get_bigquery_client()

    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

    schema = [
        bigquery.SchemaField("country", "STRING", mode="REQUIRED", description="Country or region name"),
        bigquery.SchemaField("central_bank", "STRING", mode="REQUIRED", description="Central bank name"),
        bigquery.SchemaField("rate_name", "STRING", mode="REQUIRED", description="Name of the interest rate"),
        bigquery.SchemaField("rate_value", "FLOAT64", mode="REQUIRED", description="Interest rate value in percentage"),
        bigquery.SchemaField("currency", "STRING", mode="REQUIRED", description="Currency code"),
        bigquery.SchemaField("timeframe", "STRING", mode="REQUIRED", description="Timeframe: daily or hourly"),
        bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED", description="Data timestamp"),
        bigquery.SchemaField("fetch_date", "DATE", mode="REQUIRED", description="Date when data was fetched"),
        bigquery.SchemaField("fetch_hour", "INT64", mode="NULLABLE", description="Hour when data was fetched (for hourly data)"),
        bigquery.SchemaField("source", "STRING", mode="REQUIRED", description="Data source"),
        bigquery.SchemaField("g20_member", "BOOL", mode="REQUIRED", description="Is G20 member country"),
        bigquery.SchemaField("region", "STRING", mode="NULLABLE", description="Geographic region"),
    ]

    table = bigquery.Table(table_ref, schema=schema)

    # Add partitioning by fetch_date for efficient queries
    table.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field="fetch_date"
    )

    # Add clustering for faster queries
    table.clustering_fields = ["country", "timeframe", "rate_name"]

    try:
        table = client.create_table(table)
        print(f"Created table {table_ref}")
    except Exception as e:
        if "Already Exists" in str(e):
            print(f"Table {table_ref} already exists")
        else:
            raise e

    return table_ref

def load_g20_data():
    """Load G20 interest rates from JSON file"""
    with open('g20_interest_rates.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def get_region(country):
    """Get geographic region for a country"""
    regions = {
        "United States": "North America",
        "Canada": "North America",
        "Mexico": "North America",
        "Brazil": "South America",
        "Argentina": "South America",
        "European Union": "Europe",
        "Germany": "Europe",
        "France": "Europe",
        "Italy": "Europe",
        "United Kingdom": "Europe",
        "Russia": "Europe/Asia",
        "Turkey": "Europe/Asia",
        "Japan": "Asia",
        "China": "Asia",
        "South Korea": "Asia",
        "India": "Asia",
        "Indonesia": "Asia",
        "Saudi Arabia": "Middle East",
        "Australia": "Oceania",
        "South Africa": "Africa",
    }
    return regions.get(country, "Other")

def upload_interest_rates_data(g20_data, timeframe='daily'):
    """Upload interest rates data to BigQuery"""
    client = get_bigquery_client()
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

    now = datetime.utcnow()
    fetch_date = now.date()
    fetch_hour = now.hour if timeframe == 'hourly' else None

    rows = []
    for rate in g20_data:
        row = {
            "country": rate["country"],
            "central_bank": rate["bank"],
            "rate_name": rate["rate_name"],
            "rate_value": rate["rate"],
            "currency": rate["currency"],
            "timeframe": timeframe,
            "timestamp": rate["timestamp"],
            "fetch_date": str(fetch_date),
            "fetch_hour": fetch_hour,
            "source": rate["source"],
            "g20_member": True,
            "region": get_region(rate["country"]),
        }
        rows.append(row)

    # Add additional interest rate data
    additional_data = load_additional_rates()
    for rate in additional_data:
        row = {
            "country": rate["country"],
            "central_bank": rate["source"],
            "rate_name": rate["name"],
            "rate_value": rate["rate"],
            "currency": rate["currency"],
            "timeframe": timeframe,
            "timestamp": rate["timestamp"],
            "fetch_date": str(fetch_date),
            "fetch_hour": fetch_hour,
            "source": rate["source"],
            "g20_member": rate["country"] in ["United States", "European Union"],
            "region": get_region(rate["country"]),
        }
        rows.append(row)

    errors = client.insert_rows_json(table_ref, rows)

    if errors:
        print(f"Errors inserting rows: {errors}")
        return False
    else:
        print(f"Uploaded {len(rows)} {timeframe} interest rate records to BigQuery")
        return True

def load_additional_rates():
    """Load additional interest rates data"""
    try:
        with open('interest_rates_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def main():
    print("=" * 60)
    print("Setting up Interest Rates Table in BigQuery")
    print("=" * 60)

    # Step 1: Create the table
    print("\n1. Creating interest_rates table...")
    create_interest_rates_table()

    # Step 2: Load G20 data
    print("\n2. Loading G20 interest rates data...")
    g20_data = load_g20_data()
    print(f"   Loaded {len(g20_data)} G20 country rates")

    # Step 3: Upload as daily data
    print("\n3. Uploading as DAILY timeframe...")
    upload_interest_rates_data(g20_data, timeframe='daily')

    # Step 4: Upload as hourly data (same data, different timeframe marker)
    print("\n4. Uploading as HOURLY timeframe...")
    upload_interest_rates_data(g20_data, timeframe='hourly')

    print("\n" + "=" * 60)
    print("Interest rates data setup complete!")
    print("=" * 60)

    # Print summary
    print("\nG20 Interest Rates Summary:")
    print("-" * 50)
    for rate in sorted(g20_data, key=lambda x: x["rate"], reverse=True):
        print(f"  {rate['country']:20} | {rate['rate']:6.2f}% | {rate['rate_name']}")

if __name__ == "__main__":
    main()
