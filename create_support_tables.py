"""
Create support tables for AIAlgoTradeHits (no partitioning)
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery
from google.api_core.exceptions import Conflict

PROJECT_ID = "aialgotradehits"
DATASET_ID = "crypto_trading_data"


def create_table_simple(client, table_id, schema):
    """Create a BigQuery table without partitioning"""
    table = bigquery.Table(table_id, schema=schema)

    try:
        table = client.create_table(table)
        return True, f"Created table {table.table_id}"
    except Conflict:
        return False, f"Table {table_id} already exists"
    except Exception as e:
        return False, f"Error creating {table_id}: {str(e)}"


def main():
    print("=" * 60)
    print("CREATING SUPPORT TABLES FOR AIAlgoTradeHits")
    print("=" * 60)

    client = bigquery.Client(project=PROJECT_ID)

    # Users table
    users_schema = [
        bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("email", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("username", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("password_hash", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("role", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("is_active", "BOOL", mode="NULLABLE"),
        bigquery.SchemaField("preferences", "JSON", mode="NULLABLE"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="NULLABLE"),
        bigquery.SchemaField("last_login", "TIMESTAMP", mode="NULLABLE"),
    ]

    # Search history table
    search_schema = [
        bigquery.SchemaField("search_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("user_id", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("query_text", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("query_type", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("asset_type", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("timeframe", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("sql_generated", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("result_count", "INT64", mode="NULLABLE"),
        bigquery.SchemaField("execution_time_ms", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("ai_response", "JSON", mode="NULLABLE"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="NULLABLE"),
    ]

    # Watchlists table
    watchlist_schema = [
        bigquery.SchemaField("watchlist_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("symbols", "STRING", mode="REPEATED"),
        bigquery.SchemaField("is_default", "BOOL", mode="NULLABLE"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="NULLABLE"),
        bigquery.SchemaField("updated_at", "TIMESTAMP", mode="NULLABLE"),
    ]

    # Symbols master table
    symbols_schema = [
        bigquery.SchemaField("symbol", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("name", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("asset_type", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("exchange", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("currency", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("country", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("sector", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("industry", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("market_cap", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("is_active", "BOOL", mode="NULLABLE"),
        bigquery.SchemaField("twelvedata_symbol", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="NULLABLE"),
        bigquery.SchemaField("updated_at", "TIMESTAMP", mode="NULLABLE"),
    ]

    # Alerts table
    alerts_schema = [
        bigquery.SchemaField("alert_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("symbol", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("alert_type", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("condition", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("target_value", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("is_active", "BOOL", mode="NULLABLE"),
        bigquery.SchemaField("triggered_at", "TIMESTAMP", mode="NULLABLE"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="NULLABLE"),
    ]

    # Indicator metadata table
    indicator_schema = [
        bigquery.SchemaField("indicator_id", "INT64", mode="REQUIRED"),
        bigquery.SchemaField("indicator_code", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("indicator_name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("category", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("description", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("default_period", "INT64", mode="NULLABLE"),
        bigquery.SchemaField("parameters", "JSON", mode="NULLABLE"),
        bigquery.SchemaField("output_fields", "JSON", mode="NULLABLE"),
        bigquery.SchemaField("is_active", "BOOL", mode="NULLABLE"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="NULLABLE"),
    ]

    tables = [
        ("users", users_schema),
        ("search_history", search_schema),
        ("watchlists", watchlist_schema),
        ("symbols_master", symbols_schema),
        ("alerts", alerts_schema),
        ("indicator_metadata", indicator_schema),
    ]

    created = 0
    existed = 0
    failed = 0

    for table_name, schema in tables:
        table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
        success, msg = create_table_simple(client, table_id, schema)

        if success:
            print(f"  [+] Created: {table_name}")
            created += 1
        elif "already exists" in msg:
            print(f"  [=] Exists:  {table_name}")
            existed += 1
        else:
            print(f"  [!] Failed:  {table_name} - {msg}")
            failed += 1

    print()
    print("=" * 60)
    print(f"Created: {created} | Existed: {existed} | Failed: {failed}")
    print("=" * 60)


if __name__ == "__main__":
    main()
