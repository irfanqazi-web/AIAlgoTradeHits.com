"""
Reset Passwords for MarketingAI Users
Creates simple login credentials
"""

import sys
import io
import hashlib
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


def reset_password(email, new_password):
    """Reset password for a user"""
    password_hash = get_password_hash(new_password)

    update_query = f"""
        UPDATE `{PROJECT_ID}.{DATASET_ID}.users`
        SET password_hash = @password_hash
        WHERE email = @email
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("email", "STRING", email),
            bigquery.ScalarQueryParameter("password_hash", "STRING", password_hash),
        ]
    )

    try:
        client.query(update_query, job_config=job_config).result()
        print(f"Password reset for: {email}")
        print(f"   New Password: {new_password}")
        return True
    except Exception as e:
        print(f"Error resetting password: {e}")
        return False


if __name__ == '__main__':
    print("="*60)
    print("MarketingAI - Reset Passwords")
    print("="*60)

    # Reset passwords to simple ones
    users = [
        {"email": "irfan.qazi@aialgotradehits.com", "password": "admin123"},
        {"email": "waqasulhaq2004@gmail.com", "password": "waqas123"},
    ]

    for user in users:
        print(f"\nResetting password for: {user['email']}")
        reset_password(user['email'], user['password'])

    print("\n" + "="*60)
    print("Password Reset Complete!")
    print("="*60)
    print("""
Login Credentials:

1. Irfan:
   Email: irfan.qazi@aialgotradehits.com
   Password: admin123

2. Waqas:
   Email: waqasulhaq2004@gmail.com
   Password: waqas123

Login URL: https://marketingai-1075463475276.us-central1.run.app
""")
