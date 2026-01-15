"""
Make Cloud Functions publicly accessible for Cloud Scheduler
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import functions_v2

PROJECT_ID = 'cryptobot-462709'
REGION = 'us-central1'

FUNCTIONS = [
    'daily-crypto-fetcher',
    'hourly-crypto-fetcher',
    'fivemin-top10-fetcher'
]

def make_function_public(function_name):
    """Make function publicly accessible"""
    print(f"\nMaking {function_name} publicly accessible...")

    client = functions_v2.FunctionServiceClient()
    function_path = f"projects/{PROJECT_ID}/locations/{REGION}/functions/{function_name}"

    # Set IAM policy to allow unauthenticated access
    policy = {
        "bindings": [
            {
                "role": "roles/cloudfunctions.invoker",
                "members": ["allUsers"]
            }
        ]
    }

    try:
        client.set_iam_policy(resource=function_path, policy=policy)
        print(f"✓ {function_name} is now publicly accessible")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    print("="*70)
    print("MAKING CLOUD FUNCTIONS PUBLICLY ACCESSIBLE")
    print("="*70)

    results = {}
    for func in FUNCTIONS:
        results[func] = make_function_public(func)

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    for func, success in results.items():
        status = "✓" if success else "✗"
        print(f"{status} {func}")

    if all(results.values()):
        print("\n✓ All functions are now publicly accessible!")
    else:
        print("\n⚠ Some functions failed to be made public")


if __name__ == "__main__":
    main()
