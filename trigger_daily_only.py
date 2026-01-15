"""
Trigger only the daily function with extended timeout
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests

DAILY_URL = 'https://daily-crypto-fetcher-cnyn5l4u2a-uc.a.run.app'

print("="*70)
print("TRIGGERING DAILY CRYPTO FETCHER")
print("="*70)
print(f"\nURL: {DAILY_URL}")
print("Expected runtime: 15-20 minutes")
print("The function may timeout on the client side but will continue running in the background.\n")

try:
    print("Sending request...")
    response = requests.get(DAILY_URL, timeout=1800)  # 30 minute timeout

    print(f"\nStatus Code: {response.status_code}")

    if response.status_code == 200:
        print("✓ Daily function completed successfully!")
        try:
            result = response.json()
            print(f"Result: {result}")
        except:
            print(f"Response: {response.text}")
    else:
        print(f"Response: {response.text[:500]}")

except requests.exceptions.Timeout:
    print("\n⚠ Client-side timeout reached (after 30 minutes)")
    print("The function is still running in the background on Google Cloud.")
    print("Check BigQuery table counts in a few minutes.")

except Exception as e:
    print(f"\n✗ Error: {e}")

print("\n" + "="*70)
print("To check progress:")
print("  python check_bigquery_counts.py")
print("="*70)
