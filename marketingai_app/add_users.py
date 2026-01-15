"""
Add Admin Users to MarketingAI Platform
"""

import sys
import io
import hashlib
import secrets
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery

PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'marketingai_data'

client = bigquery.Client(project=PROJECT_ID)


def get_password_hash(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def add_user(email, name, company, role, password):
    """Add a user to the MarketingAI platform"""

    # Check if user exists
    check_query = f"""
        SELECT email FROM `{PROJECT_ID}.{DATASET_ID}.users`
        WHERE email = @email
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("email", "STRING", email)
        ]
    )
    results = list(client.query(check_query, job_config=job_config).result())

    if results:
        print(f"User already exists: {email}")
        return False

    # Create user
    user_id = secrets.token_hex(16)
    password_hash = get_password_hash(password)
    now = datetime.utcnow().isoformat()

    insert_query = f"""
        INSERT INTO `{PROJECT_ID}.{DATASET_ID}.users`
        (user_id, email, password_hash, name, company, role, created_at, last_login, is_active, subscription_tier)
        VALUES (@user_id, @email, @password_hash, @name, @company, @role, @now, @now, TRUE, @tier)
    """

    tier = 'enterprise' if role == 'admin' else 'pro'

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("email", "STRING", email),
            bigquery.ScalarQueryParameter("password_hash", "STRING", password_hash),
            bigquery.ScalarQueryParameter("name", "STRING", name),
            bigquery.ScalarQueryParameter("company", "STRING", company),
            bigquery.ScalarQueryParameter("role", "STRING", role),
            bigquery.ScalarQueryParameter("now", "STRING", now),
            bigquery.ScalarQueryParameter("tier", "STRING", tier),
        ]
    )

    try:
        client.query(insert_query, job_config=job_config).result()
        print(f"Created {role}: {email}")
        print(f"   Password: {password}")
        return True
    except Exception as e:
        print(f"Error creating user: {e}")
        return False


if __name__ == '__main__':
    print("="*60)
    print("MarketingAI - Add Admin Users")
    print("="*60)

    users = [
        {
            "email": "irfan.qazi@aialgotradehits.com",
            "name": "Irfan Qazi",
            "company": "AIAlgoTradeHits",
            "role": "admin",
            "password": "Marketing2025!"
        },
        {
            "email": "waqasulhaq2004@gmail.com",
            "name": "Waqas Ul Haq",
            "company": "AIAlgoTradeHits",
            "role": "admin",
            "password": "Marketing2025!"
        }
    ]

    for user in users:
        print(f"\nAdding user: {user['email']}")
        add_user(
            email=user['email'],
            name=user['name'],
            company=user['company'],
            role=user['role'],
            password=user['password']
        )

    print("\n" + "="*60)
    print("Users Added Successfully!")
    print("="*60)
    print("""
Admin Accounts Created:
  1. irfan.qazi@aialgotradehits.com (Admin)
  2. waqasulhaq2004@gmail.com (Admin)

Default Password: Marketing2025!
(Users should change password on first login)

Access MarketingAI at:
  - Local: http://localhost:8080
  - Cloud Run: https://marketingai-[project].run.app
""")
