"""
Reset all user passwords to Irfan1234@
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery
import bcrypt

PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'crypto_trading_data'

def reset_passwords():
    """Reset all passwords to Irfan1234@"""

    client = bigquery.Client(project=PROJECT_ID)

    # Generate hash for Irfan1234@
    password = "Irfan1234@"
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    print(f"Generated password hash for: {password}")
    print(f"Hash: {password_hash}")
    print()

    # Get all users
    query = f"""
    SELECT user_id, email, username
    FROM `{PROJECT_ID}.{DATASET_ID}.users`
    """

    results = client.query(query).result()
    users = list(results)

    print(f"Found {len(users)} users. Resetting passwords...")
    print("="*70)

    for user in users:
        # Update password
        update_query = f"""
        UPDATE `{PROJECT_ID}.{DATASET_ID}.users`
        SET password_hash = @password_hash,
            first_login_completed = false,
            updated_at = CURRENT_TIMESTAMP()
        WHERE user_id = @user_id
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("password_hash", "STRING", password_hash),
                bigquery.ScalarQueryParameter("user_id", "STRING", user.user_id)
            ]
        )

        client.query(update_query, job_config=job_config).result()
        print(f"✓ Reset password for: {user.email} ({user.username})")

    print("="*70)
    print(f"\n✓ All {len(users)} passwords have been reset to: {password}")
    print("✓ All users must change password on first login")
    print("\nYou can now login with:")
    for user in users:
        print(f"  • {user.email} / {password}")

if __name__ == "__main__":
    reset_passwords()
