"""
Create users table in BigQuery for user management
"""

from google.cloud import bigquery

PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'crypto_trading_data'
TABLE_ID = 'users'

def create_users_table():
    """Create users table with proper schema"""

    client = bigquery.Client(project=PROJECT_ID)

    table_ref = f'{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}'

    schema = [
        bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("email", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("role", "STRING", mode="REQUIRED"),  # 'admin' or 'user'
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("is_active", "BOOLEAN", mode="REQUIRED"),
        bigquery.SchemaField("last_login", "TIMESTAMP", mode="NULLABLE"),
    ]

    table = bigquery.Table(table_ref, schema=schema)

    try:
        table = client.create_table(table)
        print(f"✓ Created table {table.project}.{table.dataset_id}.{table.table_id}")

        # Create a default admin user
        query = f"""
        INSERT INTO `{table_ref}`
        (user_id, email, name, role, created_at, is_active)
        VALUES
        (GENERATE_UUID(), 'admin@aialgotradehits.com', 'Admin User', 'admin', CURRENT_TIMESTAMP(), true)
        """

        query_job = client.query(query)
        query_job.result()
        print("✓ Created default admin user")

    except Exception as e:
        if 'Already Exists' in str(e):
            print(f"✓ Table already exists: {table_ref}")
        else:
            print(f"Error creating table: {str(e)}")
            raise

if __name__ == "__main__":
    create_users_table()
