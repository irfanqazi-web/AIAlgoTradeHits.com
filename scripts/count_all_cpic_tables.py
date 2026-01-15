"""
Count all records in CPIC BigQuery database tables
"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery

PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'cpic_data'

client = bigquery.Client(project=PROJECT_ID)

def main():
    print("=" * 70)
    print(f"CPIC BigQuery Database - All Tables Record Count")
    print(f"Dataset: {PROJECT_ID}.{DATASET_ID}")
    print("=" * 70)

    # Get all tables in dataset
    dataset_ref = client.dataset(DATASET_ID)
    tables = list(client.list_tables(dataset_ref))

    print(f"\nTotal Tables: {len(tables)}")
    print("-" * 70)

    total_records = 0
    table_counts = []

    for table in tables:
        table_id = f"{PROJECT_ID}.{DATASET_ID}.{table.table_id}"
        try:
            query = f"SELECT COUNT(*) as cnt FROM `{table_id}`"
            result = client.query(query).result()
            count = 0
            for row in result:
                count = row.cnt
            table_counts.append((table.table_id, count))
            total_records += count
        except Exception as e:
            table_counts.append((table.table_id, f"Error: {str(e)[:30]}"))

    # Sort by table name
    table_counts.sort(key=lambda x: x[0])

    # Print results
    print(f"\n{'Table Name':<40} {'Record Count':>15}")
    print("-" * 55)
    for table_name, count in table_counts:
        if isinstance(count, int):
            print(f"{table_name:<40} {count:>15,}")
        else:
            print(f"{table_name:<40} {count:>15}")

    print("-" * 55)
    print(f"{'TOTAL RECORDS':<40} {total_records:>15,}")
    print("=" * 70)

    # Show tables with 0 records
    empty_tables = [t for t, c in table_counts if c == 0]
    if empty_tables:
        print(f"\nTables with 0 records ({len(empty_tables)}):")
        for t in empty_tables:
            print(f"  - {t}")

if __name__ == "__main__":
    main()
