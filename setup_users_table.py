"""
Setup users table with proper schema and populate with initial users
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery
from datetime import datetime, timezone
import time

PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'crypto_trading_data'
TABLE_ID = 'users'

def create_users_table():
    """Create or update users table with proper schema for authentication"""

    client = bigquery.Client(project=PROJECT_ID)
    table_ref = f'{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}'

    # Drop existing table if it exists
    try:
        client.delete_table(table_ref)
        print(f"✓ Deleted existing table {table_ref}")
    except Exception:
        print(f"✓ Table doesn't exist yet, creating new one")

    # Define schema with all required fields for authentication
    schema = [
        bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("email", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("username", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("password_hash", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("email_verified", "BOOLEAN", mode="NULLABLE"),
        bigquery.SchemaField("account_status", "STRING", mode="REQUIRED"),  # active, suspended, deleted
        bigquery.SchemaField("subscription_tier", "STRING", mode="REQUIRED"),  # free, basic, premium, enterprise
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("last_login", "TIMESTAMP", mode="NULLABLE"),
        bigquery.SchemaField("first_login_completed", "BOOLEAN", mode="NULLABLE"),
        bigquery.SchemaField("preferences", "STRING", mode="NULLABLE"),  # Store JSON as string
    ]

    table = bigquery.Table(table_ref, schema=schema)

    try:
        table = client.create_table(table)
        print(f"✓ Created table {table.project}.{table.dataset_id}.{table.table_id}")
        return True
    except Exception as e:
        print(f"Error creating table: {str(e)}")
        return False

def populate_users():
    """Populate table with initial users"""

    client = bigquery.Client(project=PROJECT_ID)
    table_ref = f'{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}'

    # User data provided by client
    # Note: All users will have first_login_completed = false to force password change
    users = [
        {
            "user_id": "80b055b8-54e5-458b-956c-7bcc51dccad0",
            "email": "waqasulhaq2003@gmail.com",
            "username": "Waqas Ul Haq",
            "password_hash": "$2b$12$VHrklknZnXj/hoCeCsA44OFhwG1s5HNqBBhiO8XElOmJSRf7c6epK",  # Irfan1234@
            "email_verified": True,
            "account_status": "active",
            "subscription_tier": "premium",
            "created_at": "2025-06-12 10:29:10",
            "first_login_completed": False
        },
        {
            "user_id": "2418c4bb-ef98-4268-a9a1-ce41504c1d6f",
            "email": "iqtayyaba@gmail.com",
            "username": "Tayyab Irfan",
            "password_hash": "$2b$12$juGMsm9V1DLrRZWOFFb5jewOwl1xsdauttBgyC0bpTXM.n6wWFRRW",  # Irfan1234@
            "email_verified": True,
            "account_status": "active",
            "subscription_tier": "premium",
            "created_at": "2025-06-12 10:29:34",
            "first_login_completed": False
        },
        {
            "user_id": "86325b39-fc04-4235-b597-a3c187ffc7a1",
            "email": "haq.irfanul@gmail.com",
            "username": "Irfanul Haq",
            "password_hash": "$2b$12$kei5OoumvapTFRjDXd4UqO262kqgxAOmHN7tXJpdN2x2mMAeaAfxI2",  # Irfan1234@
            "email_verified": True,
            "account_status": "active",
            "subscription_tier": "enterprise",  # Admin user
            "created_at": "2025-06-12 10:28:51",
            "first_login_completed": False
        },
        {
            "user_id": "5d105a02-a651-40a2-8513-d1be7f11868d",
            "email": "saleem265@gmail.com",
            "username": "Saleem Ahmed",
            "password_hash": "$2b$12$i4fTjSitF6m6kW9USomHCeWj5419K98uvn5XUUOe.pypD398rIQbW",  # Irfan1234@
            "email_verified": True,
            "account_status": "active",
            "subscription_tier": "premium",
            "created_at": "2025-06-12 10:28:51",
            "first_login_completed": False
        }
    ]

    # Build INSERT query
    query_parts = []
    for user in users:
        updated_at = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        query_parts.append(f"""
            ('{user["user_id"]}', '{user["email"]}', '{user["username"]}',
             '{user["password_hash"]}', {user["email_verified"]}, '{user["account_status"]}',
             '{user["subscription_tier"]}', TIMESTAMP('{user["created_at"]}'),
             TIMESTAMP('{updated_at}'), NULL, {user["first_login_completed"]}, '{{}}')
        """)

    query = f"""
    INSERT INTO `{table_ref}`
    (user_id, email, username, password_hash, email_verified, account_status,
     subscription_tier, created_at, updated_at, last_login, first_login_completed, preferences)
    VALUES {','.join(query_parts)}
    """

    try:
        query_job = client.query(query)
        query_job.result()

        print(f"✓ Successfully inserted {len(users)} users")
        print("\nUsers created:")
        for user in users:
            role = "Admin" if user["subscription_tier"] == "enterprise" else "User"
            print(f"  • {user['username']} ({user['email']}) - {role}")

        print(f"\n✓ All users have initial password: Irfan1234@")
        print(f"✓ Users will be required to change password on first login")
        return True

    except Exception as e:
        print(f"❌ Error inserting users: {str(e)}")
        return False

def verify_users():
    """Verify users were created successfully"""

    client = bigquery.Client(project=PROJECT_ID)

    query = f"""
    SELECT user_id, email, username, account_status, subscription_tier, created_at
    FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
    ORDER BY created_at
    """

    try:
        results = client.query(query).result()

        print("\n" + "="*70)
        print("USERS TABLE VERIFICATION")
        print("="*70)

        count = 0
        for row in results:
            count += 1
            role = "Admin" if row.subscription_tier == "enterprise" else "User"
            print(f"\n{count}. {row.username}")
            print(f"   Email: {row.email}")
            print(f"   Role: {role}")
            print(f"   Status: {row.account_status}")
            print(f"   Created: {row.created_at}")

        print("\n" + "="*70)
        print(f"✓ Total users: {count}")
        print("="*70)

    except Exception as e:
        print(f"❌ Error verifying users: {str(e)}")

if __name__ == "__main__":
    print("="*70)
    print("USERS TABLE SETUP")
    print("="*70)

    print("\n1. Creating users table...")
    if create_users_table():
        print("   Waiting for table to be ready...")
        time.sleep(3)  # Wait for table to be fully created
        print("\n2. Populating users table...")
        if populate_users():
            print("\n3. Verifying users...")
            verify_users()
            print("\n✓ SETUP COMPLETE!")
        else:
            print("\n❌ Failed to populate users")
    else:
        print("\n❌ Failed to create table")
