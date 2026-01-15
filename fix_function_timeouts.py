"""
Fix Cloud Function timeout issues by updating function configurations
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import functions_v2
from google.cloud.functions_v2 import types

PROJECT_ID = 'cryptobot-462709'
REGION = 'us-central1'

FUNCTIONS = [
    {
        'name': 'daily-crypto-fetcher',
        'source': 'cloud_function_daily',
        'timeout': 3600,  # 60 minutes
        'memory': 1024  # 1GB
    },
    {
        'name': 'hourly-crypto-fetcher',
        'source': 'cloud_function_hourly',
        'timeout': 1800,  # 30 minutes
        'memory': 1024  # 1GB
    },
    {
        'name': 'fivemin-top10-fetcher',
        'source': 'cloud_function_5min',
        'timeout': 600,  # 10 minutes
        'memory': 512  # 512MB
    }
]

def update_function_timeout(func_info):
    """Update Cloud Function timeout and memory settings"""
    print(f"\n{'='*70}")
    print(f"Updating {func_info['name']}")
    print(f"{'='*70}")
    print(f"New timeout: {func_info['timeout']} seconds ({func_info['timeout']//60} minutes)")
    print(f"New memory: {func_info['memory']} MB")

    try:
        client = functions_v2.FunctionServiceClient()
        function_path = f"projects/{PROJECT_ID}/locations/{REGION}/functions/{func_info['name']}"

        # Get current function
        print(f"Fetching current function configuration...")
        function = client.get_function(name=function_path)

        # Update service config
        print(f"Updating service configuration...")
        function.service_config.timeout_seconds = func_info['timeout']
        function.service_config.available_memory = f"{func_info['memory']}Mi"

        # Create update mask
        update_mask = types.FieldMask(paths=[
            "service_config.timeout_seconds",
            "service_config.available_memory"
        ])

        # Update function
        print(f"Applying updates...")
        operation = client.update_function(
            function=function,
            update_mask=update_mask
        )

        print(f"Waiting for operation to complete...")
        result = operation.result(timeout=600)  # Wait up to 10 minutes

        print(f"✓ {func_info['name']} updated successfully!")
        print(f"  Timeout: {func_info['timeout']}s")
        print(f"  Memory: {func_info['memory']}MB")
        return True

    except Exception as e:
        print(f"✗ Error updating {func_info['name']}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("="*70)
    print("FIXING CLOUD FUNCTION TIMEOUT ISSUES")
    print("="*70)
    print("\nThis will increase timeout and memory limits for all functions.")
    print("This process may take 5-10 minutes per function.\n")

    results = {}
    for func_info in FUNCTIONS:
        results[func_info['name']] = update_function_timeout(func_info)

    print("\n" + "="*70)
    print("UPDATE SUMMARY")
    print("="*70)

    for name, success in results.items():
        status = "✓" if success else "✗"
        print(f"{status} {name}")

    if all(results.values()):
        print("\n✓ All functions updated successfully!")
        print("\nYou can now trigger the functions and they should complete without timeout:")
        print("  python trigger_all_functions.py")
    else:
        print("\n⚠ Some functions failed to update")
        print("You may need to update manually using gcloud CLI")


if __name__ == "__main__":
    main()
