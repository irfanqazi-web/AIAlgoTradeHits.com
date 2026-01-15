"""
Create BigQuery table for NLP Search History
Stores all user searches (voice and text) for quick access
"""

from google.cloud import bigquery
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuration
PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'crypto_trading_data'
TABLE_ID = 'search_history'

def create_search_history_table():
    """Create the search_history table in BigQuery"""

    client = bigquery.Client(project=PROJECT_ID)

    # Define table schema
    schema = [
        bigquery.SchemaField("search_id", "STRING", mode="REQUIRED", description="Unique identifier for the search"),
        bigquery.SchemaField("user_id", "STRING", mode="NULLABLE", description="User who performed the search (if authenticated)"),
        bigquery.SchemaField("email", "STRING", mode="NULLABLE", description="User email (if authenticated)"),
        bigquery.SchemaField("query_text", "STRING", mode="REQUIRED", description="The search query text (transcribed if voice)"),
        bigquery.SchemaField("input_method", "STRING", mode="REQUIRED", description="How query was entered: 'text' or 'voice'"),
        bigquery.SchemaField("interpretation", "STRING", mode="NULLABLE", description="NLP engine interpretation of the query"),
        bigquery.SchemaField("generated_sql", "STRING", mode="NULLABLE", description="SQL query generated from NLP"),
        bigquery.SchemaField("table_queried", "STRING", mode="NULLABLE", description="Which table was queried"),
        bigquery.SchemaField("result_count", "INTEGER", mode="NULLABLE", description="Number of results returned"),
        bigquery.SchemaField("search_timestamp", "TIMESTAMP", mode="REQUIRED", description="When the search was performed"),
        bigquery.SchemaField("response_time_ms", "INTEGER", mode="NULLABLE", description="Time taken to process query in milliseconds"),
        bigquery.SchemaField("success", "BOOLEAN", mode="REQUIRED", description="Whether the search was successful"),
        bigquery.SchemaField("error_message", "STRING", mode="NULLABLE", description="Error message if search failed"),
        bigquery.SchemaField("session_id", "STRING", mode="NULLABLE", description="Browser session identifier"),
        bigquery.SchemaField("ip_address", "STRING", mode="NULLABLE", description="IP address of the requester"),
        bigquery.SchemaField("user_agent", "STRING", mode="NULLABLE", description="Browser user agent"),
    ]

    # Create table reference
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
    table = bigquery.Table(table_ref, schema=schema)

    # Set table options
    table.description = "Search history for NLP Smart Search - stores all user queries (voice and text)"
    table.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field="search_timestamp",
    )

    try:
        # Create the table
        table = client.create_table(table)
        print(f"✅ Successfully created table: {table.project}.{table.dataset_id}.{table.table_id}")
        print(f"\n📋 Table Schema:")
        for field in schema:
            print(f"  • {field.name} ({field.field_type}) - {field.description}")

        return True

    except Exception as e:
        if "Already Exists" in str(e):
            print(f"⚠️  Table {table_ref} already exists")

            # Ask if user wants to update schema
            response = input("\nDo you want to update the table schema? (y/n): ").lower()
            if response == 'y':
                try:
                    # Get existing table
                    existing_table = client.get_table(table_ref)
                    # Update schema
                    existing_table.schema = schema
                    existing_table = client.update_table(existing_table, ["schema"])
                    print(f"✅ Successfully updated table schema")
                    return True
                except Exception as update_error:
                    print(f"❌ Error updating schema: {update_error}")
                    return False
            else:
                print("Table creation skipped")
                return True
        else:
            print(f"❌ Error creating table: {e}")
            return False


def test_table():
    """Test the table by inserting a sample record"""

    client = bigquery.Client(project=PROJECT_ID)
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

    # Sample record
    rows_to_insert = [
        {
            "search_id": "test-search-001",
            "user_id": "test-user",
            "email": "test@example.com",
            "query_text": "oversold cryptos",
            "input_method": "text",
            "interpretation": "Showing 20 results for cryptocurrencies with rsi below 30",
            "generated_sql": "SELECT * FROM crypto_analysis WHERE rsi < 30",
            "table_queried": "crypto_analysis",
            "result_count": 15,
            "search_timestamp": "2025-01-17 12:00:00 UTC",
            "response_time_ms": 1234,
            "success": True,
            "error_message": None,
            "session_id": "test-session-123",
            "ip_address": "127.0.0.1",
            "user_agent": "Test Browser",
        }
    ]

    try:
        errors = client.insert_rows_json(table_ref, rows_to_insert)
        if errors:
            print(f"❌ Error inserting test record: {errors}")
            return False
        else:
            print(f"✅ Successfully inserted test record")

            # Query to verify
            query = f"""
            SELECT search_id, query_text, input_method, result_count, search_timestamp
            FROM `{table_ref}`
            WHERE search_id = 'test-search-001'
            LIMIT 1
            """

            query_job = client.query(query)
            results = query_job.result()

            print("\n📊 Test Record Retrieved:")
            for row in results:
                print(f"  Search ID: {row.search_id}")
                print(f"  Query: {row.query_text}")
                print(f"  Method: {row.input_method}")
                print(f"  Results: {row.result_count}")
                print(f"  Timestamp: {row.search_timestamp}")

            return True

    except Exception as e:
        print(f"❌ Error testing table: {e}")
        return False


if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║     Create Search History Table in BigQuery               ║
    ║                                                            ║
    ║  This will create a table to store all NLP search         ║
    ║  queries (voice and text) for search history dropdown.    ║
    ╚════════════════════════════════════════════════════════════╝
    """)

    print(f"📍 Project: {PROJECT_ID}")
    print(f"📍 Dataset: {DATASET_ID}")
    print(f"📍 Table: {TABLE_ID}\n")

    # Create table
    if create_search_history_table():
        print("\n" + "="*60)

        # Ask if user wants to test
        response = input("\nDo you want to insert a test record? (y/n): ").lower()
        if response == 'y':
            test_table()

        print("\n✨ Setup complete!")
        print(f"\n🔗 View table in BigQuery Console:")
        print(f"   https://console.cloud.google.com/bigquery?project={PROJECT_ID}&ws=!1m5!1m4!4m3!1s{PROJECT_ID}!2s{DATASET_ID}!3s{TABLE_ID}")
    else:
        print("\n❌ Setup failed")
        sys.exit(1)
