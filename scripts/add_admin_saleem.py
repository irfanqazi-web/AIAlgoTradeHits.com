"""
Add Saleem265@gmail.com as admin user
"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery
import hashlib
from datetime import datetime

PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'crypto_trading_data'

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def main():
    print("="*70)
    print("ADDING ADMIN USER: Saleem265@gmail.com")
    print("="*70)

    client = bigquery.Client(project=PROJECT_ID)

    # Default password (user will change on first login)
    default_password = "Admin@123"
    hashed_password = hash_password(default_password)

    # Generate user ID
    import uuid
    user_id = str(uuid.uuid4())

    # Insert admin user
    query = f"""
    INSERT INTO `{PROJECT_ID}.{DATASET_ID}.users`
    (user_id, username, email, password_hash, email_verified, account_status, subscription_tier, created_at, updated_at, first_login_completed, preferences)
    VALUES
    ('{user_id}', 'Saleem Ahmad', 'Saleem265@gmail.com', '{hashed_password}', TRUE, 'active', 'enterprise', CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), FALSE, '{{"role": "admin"}}')
    """

    print("\nInserting admin user...")
    try:
        result = client.query(query).result()
        print("✓ Admin user added successfully!")
        print()
        print("Login Credentials:")
        print(f"  Email: Saleem265@gmail.com")
        print(f"  Temporary Password: {default_password}")
        print()
        print("⚠️  User will be prompted to change password on first login")

    except Exception as e:
        print(f"✗ Error adding user: {e}")
        return False

    # Verify user was added
    verify_query = f"""
    SELECT username, email, subscription_tier, preferences, account_status, created_at
    FROM `{PROJECT_ID}.{DATASET_ID}.users`
    WHERE email = 'Saleem265@gmail.com'
    """

    print("\nVerifying user...")
    result = client.query(verify_query).result()
    for row in result:
        print(f"✓ Verified:")
        print(f"  Username: {row['username']}")
        print(f"  Email: {row['email']}")
        print(f"  Tier: {row['subscription_tier']}")
        print(f"  Status: {row['account_status']}")
        print(f"  Preferences: {row['preferences']}")
        print(f"  Created: {row['created_at']}")

    print("\n" + "="*70)
    print("ADMIN USER SETUP COMPLETE")
    print("="*70)

    return True

if __name__ == "__main__":
    main()
