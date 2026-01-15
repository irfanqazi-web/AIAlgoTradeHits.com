"""
Deploy all three Cloud Functions to cryptobot-462709 project
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
import shutil
import tempfile
from pathlib import Path

# New project configuration
NEW_PROJECT_ID = 'cryptobot-462709'
NEW_DATASET_ID = 'crypto_trading_data'
OLD_PROJECT_ID = 'molten-optics-310919'
OLD_DATASET_ID = 'kamiyabPakistan'

def update_cloud_function(function_dir, function_name):
    """Update project IDs in Cloud Function code"""
    print(f"\n{'='*70}")
    print(f"Updating {function_name}...")
    print('='*70)

    main_py = os.path.join(function_dir, 'main.py')

    # Read file
    with open(main_py, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace project and dataset IDs
    content = content.replace(f"PROJECT_ID = '{OLD_PROJECT_ID}'", f"PROJECT_ID = '{NEW_PROJECT_ID}'")
    content = content.replace(f"DATASET_ID = '{OLD_DATASET_ID}'", f"DATASET_ID = '{NEW_DATASET_ID}'")

    # Write back
    with open(main_py, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✓ Updated {function_name}/main.py")
    print(f"  - Project: {OLD_PROJECT_ID} → {NEW_PROJECT_ID}")
    print(f"  - Dataset: {OLD_DATASET_ID} → {NEW_DATASET_ID}")

    return True


def update_deploy_script(function_dir, script_name):
    """Update deploy script project ID"""
    script_path = os.path.join(function_dir, script_name)

    if not os.path.exists(script_path):
        print(f"  - No {script_name} found, skipping")
        return

    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()

    content = content.replace(f"PROJECT_ID = '{OLD_PROJECT_ID}'", f"PROJECT_ID = '{NEW_PROJECT_ID}'")

    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✓ Updated {script_name}")


def main():
    base_dir = Path(os.path.dirname(os.path.abspath(__file__)))

    print("="*70)
    print("UPDATING CLOUD FUNCTIONS FOR CRYPTOBOT-462709")
    print("="*70)

    # Update Daily Function
    daily_dir = base_dir / 'cloud_function_daily'
    update_cloud_function(str(daily_dir), 'Daily Function')
    update_deploy_script(str(daily_dir), 'deploy_via_api.py')

    # Update Hourly Function
    hourly_dir = base_dir / 'cloud_function_hourly'
    update_cloud_function(str(hourly_dir), 'Hourly Function')
    update_deploy_script(str(hourly_dir), 'deploy.py')

    # Update 5-Minute Function
    fivemin_dir = base_dir / 'cloud_function_5min'
    update_cloud_function(str(fivemin_dir), '5-Minute Function')
    update_deploy_script(str(fivemin_dir), 'deploy_all.py')

    print("\n" + "="*70)
    print("✓ ALL FUNCTIONS UPDATED!")
    print("="*70)
    print(f"\nNew Configuration:")
    print(f"  Project: {NEW_PROJECT_ID}")
    print(f"  Dataset: {NEW_DATASET_ID}")
    print(f"\nNext: Deploy functions individually:")
    print(f"  1. cd cloud_function_daily && python deploy_via_api.py")
    print(f"  2. cd cloud_function_hourly && python deploy.py")
    print(f"  3. cd cloud_function_5min && python deploy_all.py")


if __name__ == "__main__":
    main()
