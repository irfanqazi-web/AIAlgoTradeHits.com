"""Check users in database"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery

PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'crypto_trading_data'

client = bigquery.Client(project=PROJECT_ID)

query = f"""
SELECT user_id, email, username, password_hash, account_status, first_login_completed
FROM `{PROJECT_ID}.{DATASET_ID}.users`
ORDER BY created_at
"""

print("Checking users in database...")
print("="*70)

results = client.query(query).result()

for row in results:
    print(f"\nEmail: {row.email}")
    print(f"Username: {row.username}")
    print(f"Status: {row.account_status}")
    print(f"First Login Completed: {row.first_login_completed}")
    print(f"Password Hash: {row.password_hash[:50]}...")
    print("-"*70)
