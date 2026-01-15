"""
Trigger all Cloud Functions to populate BigQuery tables
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import time

FUNCTIONS = [
    {
        'name': 'Daily Crypto Fetcher',
        'url': 'https://daily-crypto-fetcher-cnyn5l4u2a-uc.a.run.app',
        'timeout': 1200,  # 20 minutes
        'description': 'Collects daily OHLCV data for all crypto pairs'
    },
    {
        'name': 'Hourly Crypto Fetcher',
        'url': 'https://hourly-crypto-fetcher-cnyn5l4u2a-uc.a.run.app',
        'timeout': 900,  # 15 minutes
        'description': 'Collects hourly OHLCV data for all crypto pairs'
    },
    {
        'name': '5-Minute Top 10 Fetcher',
        'url': 'https://fivemin-top10-fetcher-cnyn5l4u2a-uc.a.run.app',
        'timeout': 420,  # 7 minutes
        'description': 'Collects 5-minute data for top 10 gainers'
    }
]

def trigger_function(func_info):
    """Trigger a Cloud Function"""
    print(f"\n{'='*70}")
    print(f"Triggering: {func_info['name']}")
    print(f"Description: {func_info['description']}")
    print(f"Expected runtime: {func_info['timeout']//60} minutes")
    print(f"{'='*70}")

    try:
        print(f"Sending request to {func_info['url']}...")
        print(f"This may take up to {func_info['timeout']//60} minutes...")

        start_time = time.time()
        response = requests.get(func_info['url'], timeout=func_info['timeout'])
        elapsed = time.time() - start_time

        print(f"\nResponse received in {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            print(f"✓ {func_info['name']} completed successfully!")
            try:
                result = response.json()
                print(f"Result: {result}")
            except:
                print(f"Response: {response.text[:500]}")
            return True
        else:
            print(f"✗ {func_info['name']} returned error")
            print(f"Response: {response.text[:500]}")
            return False

    except requests.exceptions.Timeout:
        print(f"⚠ Function timed out after {func_info['timeout']} seconds")
        print(f"This is normal for large data collection. The function is still running in the background.")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    print("="*70)
    print("TRIGGERING ALL CLOUD FUNCTIONS")
    print("="*70)
    print("\nThis will populate your BigQuery tables with initial crypto data.")
    print("Total expected time: 30-45 minutes\n")

    results = {}

    for func_info in FUNCTIONS:
        results[func_info['name']] = trigger_function(func_info)

        # Wait between triggers
        if func_info != FUNCTIONS[-1]:
            print("\nWaiting 10 seconds before next trigger...")
            time.sleep(10)

    print("\n" + "="*70)
    print("TRIGGER SUMMARY")
    print("="*70)

    for name, success in results.items():
        status = "✓" if success else "✗"
        print(f"{status} {name}")

    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print("\n1. Wait 30-45 minutes for all functions to complete")
    print("2. Run: python check_bigquery_counts.py")
    print("3. Verify data is being collected\n")

    if all(results.values()):
        print("✓ All functions triggered successfully!")
        print("\nYour crypto trading data pipeline is now operational!")
    else:
        print("⚠ Some functions failed to trigger")
        print("\nCheck the error messages above for details.")


if __name__ == "__main__":
    main()
