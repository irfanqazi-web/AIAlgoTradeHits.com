"""
Manually trigger all Cloud Functions to populate BigQuery tables
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import time

PROJECT_ID = 'cryptobot-462709'

# Function URLs
FUNCTIONS = {
    'Daily': 'https://daily-crypto-fetcher-cnyn5l4u2a-uc.a.run.app',
    'Hourly': 'https://hourly-crypto-fetcher-cnyn5l4u2a-uc.a.run.app',
    '5-Minute': 'https://fivemin-top10-fetcher-cnyn5l4u2a-uc.a.run.app'
}

def trigger_function(name, url):
    """Trigger a Cloud Function"""
    print(f"\n{'='*70}")
    print(f"Triggering {name} Function")
    print('='*70)
    print(f"URL: {url}")

    try:
        print("Sending request...")
        response = requests.get(url, timeout=600)  # 10 minute timeout

        if response.status_code == 200:
            print(f"✓ {name} function completed successfully!")
            print(f"Response: {response.text}")
            return True
        else:
            print(f"✗ {name} function returned status {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print(f"⚠ {name} function timed out (still running in background)")
        return None
    except Exception as e:
        print(f"✗ Error triggering {name} function: {e}")
        return False


def main():
    print("="*70)
    print("MANUALLY TRIGGERING CLOUD FUNCTIONS")
    print("="*70)
    print("\nThis will populate the BigQuery tables with initial data.")
    print("Note: Functions may take 10-20 minutes to complete.")
    print()

    results = {}

    # Trigger functions in sequence
    # Note: 5-minute function depends on hourly data, so trigger it last
    order = ['Daily', 'Hourly', '5-Minute']

    for name in order:
        url = FUNCTIONS[name]
        result = trigger_function(name, url)
        results[name] = result

        if result is False:
            print(f"\n⚠ {name} function failed, but continuing...")

        # Wait a bit between triggers
        if name != order[-1]:
            print("\nWaiting 5 seconds before next trigger...")
            time.sleep(5)

    print("\n" + "="*70)
    print("TRIGGER SUMMARY")
    print("="*70)
    for name, result in results.items():
        status = "✓ Success" if result is True else ("⚠ Timeout/Running" if result is None else "✗ Failed")
        print(f"{name}: {status}")

    print("\n" + "="*70)
    print("Note: Functions may still be running in the background.")
    print("Wait 10-20 minutes, then check BigQuery table counts.")
    print("="*70)


if __name__ == "__main__":
    main()
