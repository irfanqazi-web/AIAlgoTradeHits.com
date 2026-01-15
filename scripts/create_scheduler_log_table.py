"""
Create Scheduler Execution Log Table for Admin Monitoring
Tracks execution time, status, and statistics for all data pipelines
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery

PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'crypto_trading_data'

def create_scheduler_log_table():
    """Create the scheduler execution log table"""
    client = bigquery.Client(project=PROJECT_ID)

    table_id = f"{PROJECT_ID}.{DATASET_ID}.scheduler_execution_log"

    schema = [
        # Execution Identification
        bigquery.SchemaField("execution_id", "STRING", mode="REQUIRED", description="Unique execution ID"),
        bigquery.SchemaField("scheduler_name", "STRING", mode="REQUIRED", description="Name of the scheduler job"),
        bigquery.SchemaField("function_name", "STRING", mode="REQUIRED", description="Cloud function name"),
        bigquery.SchemaField("table_name", "STRING", mode="REQUIRED", description="Target BigQuery table"),

        # Timing
        bigquery.SchemaField("execution_date", "DATE", mode="REQUIRED", description="Date of execution"),
        bigquery.SchemaField("start_time", "TIMESTAMP", mode="REQUIRED", description="When execution started"),
        bigquery.SchemaField("end_time", "TIMESTAMP", mode="NULLABLE", description="When execution ended"),
        bigquery.SchemaField("duration_seconds", "FLOAT64", mode="NULLABLE", description="Total execution time in seconds"),
        bigquery.SchemaField("duration_minutes", "FLOAT64", mode="NULLABLE", description="Total execution time in minutes"),

        # Status
        bigquery.SchemaField("status", "STRING", mode="REQUIRED", description="SUCCESS, FAILED, PARTIAL, RUNNING"),
        bigquery.SchemaField("error_message", "STRING", mode="NULLABLE", description="Error details if failed"),

        # Statistics
        bigquery.SchemaField("total_symbols", "INT64", mode="NULLABLE", description="Total symbols to process"),
        bigquery.SchemaField("successful_symbols", "INT64", mode="NULLABLE", description="Successfully processed"),
        bigquery.SchemaField("failed_symbols", "INT64", mode="NULLABLE", description="Failed to process"),
        bigquery.SchemaField("records_inserted", "INT64", mode="NULLABLE", description="Records inserted into table"),
        bigquery.SchemaField("records_updated", "INT64", mode="NULLABLE", description="Records updated"),
        bigquery.SchemaField("records_skipped", "INT64", mode="NULLABLE", description="Records skipped (duplicates)"),

        # API Usage
        bigquery.SchemaField("api_calls_made", "INT64", mode="NULLABLE", description="Number of API calls"),
        bigquery.SchemaField("api_rate_limited", "INT64", mode="NULLABLE", description="Times rate limited"),
        bigquery.SchemaField("api_errors", "INT64", mode="NULLABLE", description="API error count"),

        # Resource Usage
        bigquery.SchemaField("memory_used_mb", "FLOAT64", mode="NULLABLE", description="Memory used in MB"),
        bigquery.SchemaField("cpu_time_seconds", "FLOAT64", mode="NULLABLE", description="CPU time used"),

        # Data Quality
        bigquery.SchemaField("data_freshness", "STRING", mode="NULLABLE", description="How fresh is the data"),
        bigquery.SchemaField("oldest_record_date", "DATE", mode="NULLABLE", description="Oldest record date in batch"),
        bigquery.SchemaField("newest_record_date", "DATE", mode="NULLABLE", description="Newest record date in batch"),

        # Schedule Info
        bigquery.SchemaField("scheduled_time", "TIMESTAMP", mode="NULLABLE", description="When it was scheduled to run"),
        bigquery.SchemaField("was_manual_trigger", "BOOLEAN", mode="NULLABLE", description="Manually triggered vs scheduled"),
        bigquery.SchemaField("trigger_source", "STRING", mode="NULLABLE", description="scheduler/manual/api"),

        # Metadata
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED", description="Log entry creation time"),
        bigquery.SchemaField("notes", "STRING", mode="NULLABLE", description="Additional notes"),
    ]

    table = bigquery.Table(table_id, schema=schema)
    table.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field="execution_date"
    )
    table.clustering_fields = ["scheduler_name", "status"]

    try:
        table = client.create_table(table)
        print(f"Created table {table_id}")
        print(f"Columns: {len(schema)}")
        return True
    except Exception as e:
        if "Already Exists" in str(e):
            print(f"Table {table_id} already exists")
            return True
        print(f"Error creating table: {e}")
        return False


def create_scheduler_summary_view():
    """Create a view for scheduler summary statistics"""
    client = bigquery.Client(project=PROJECT_ID)

    view_id = f"{PROJECT_ID}.{DATASET_ID}.scheduler_summary_view"

    view_query = f"""
    WITH recent_executions AS (
        SELECT
            scheduler_name,
            function_name,
            table_name,
            execution_date,
            start_time,
            duration_minutes,
            status,
            successful_symbols,
            failed_symbols,
            records_inserted,
            ROW_NUMBER() OVER (PARTITION BY scheduler_name ORDER BY start_time DESC) as rn
        FROM `{PROJECT_ID}.{DATASET_ID}.scheduler_execution_log`
        WHERE execution_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
    )
    SELECT
        scheduler_name,
        function_name,
        table_name,
        -- Last execution
        MAX(CASE WHEN rn = 1 THEN start_time END) as last_execution_time,
        MAX(CASE WHEN rn = 1 THEN status END) as last_status,
        MAX(CASE WHEN rn = 1 THEN duration_minutes END) as last_duration_minutes,
        -- Statistics
        COUNT(*) as total_executions_30d,
        SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) as successful_runs_30d,
        SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) as failed_runs_30d,
        ROUND(AVG(duration_minutes), 2) as avg_duration_minutes,
        ROUND(MAX(duration_minutes), 2) as max_duration_minutes,
        ROUND(MIN(duration_minutes), 2) as min_duration_minutes,
        SUM(records_inserted) as total_records_inserted_30d,
        SUM(failed_symbols) as total_failed_symbols_30d
    FROM recent_executions
    GROUP BY scheduler_name, function_name, table_name
    ORDER BY scheduler_name
    """

    view = bigquery.Table(view_id)
    view.view_query = view_query

    try:
        view = client.create_table(view)
        print(f"Created view {view_id}")
        return True
    except Exception as e:
        if "Already Exists" in str(e):
            # Delete and recreate
            client.delete_table(view_id)
            view = bigquery.Table(view_id)
            view.view_query = view_query
            view = client.create_table(view)
            print(f"Recreated view {view_id}")
            return True
        print(f"Error creating view: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("CREATING SCHEDULER MONITORING TABLES")
    print(f"Project: {PROJECT_ID}")
    print(f"Dataset: {DATASET_ID}")
    print("=" * 60)

    print("\n1. Creating scheduler_execution_log table...")
    create_scheduler_log_table()

    print("\n2. Creating scheduler_summary_view...")
    create_scheduler_summary_view()

    print("\n" + "=" * 60)
    print("Tables for Admin Monitoring:")
    print("  - scheduler_execution_log: Detailed execution history")
    print("  - scheduler_summary_view: Aggregated statistics")
    print("=" * 60)
