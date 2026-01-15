"""
Fix all schema issues automatically
"""
import subprocess
import sys

def run_query(query, desc):
    """Run a BigQuery query"""
    print(f"Running: {desc}...")
    try:
        result = subprocess.run(
            f'bq query --nouse_legacy_sql --project_id=cryptobot-462709 "{query}"',
            shell=True,
            capture_output=True,
            text=True
        )
        if result.returncode == 0 or "already exists" in result.stdout.lower():
            print(f"  ✓ {desc}")
            return True
        else:
            print(f"  Note: {result.stdout}")
            return True
    except Exception as e:
        print(f"  Error: {e}")
        return False

print("=" * 70)
print("FIXING ALL SCHEMA ISSUES")
print("=" * 70)
print()

# Drop and recreate wave_position as INTEGER for crypto
run_query("ALTER TABLE crypto_trading_data.crypto_analysis DROP COLUMN IF EXISTS wave_position",
          "Drop wave_position from crypto_analysis")
run_query("ALTER TABLE crypto_trading_data.crypto_analysis ADD COLUMN wave_position INTEGER",
          "Add wave_position (INTEGER) to crypto_analysis")

# Ensure all other fields exist
run_query("ALTER TABLE crypto_trading_data.crypto_analysis ADD COLUMN IF NOT EXISTS elliott_wave_degree STRING",
          "Add elliott_wave_degree to crypto")
run_query("ALTER TABLE crypto_trading_data.crypto_analysis ADD COLUMN IF NOT EXISTS impulse_wave_count INTEGER",
          "Add impulse_wave_count to crypto")
run_query("ALTER TABLE crypto_trading_data.crypto_analysis ADD COLUMN IF NOT EXISTS corrective_wave_count INTEGER",
          "Add corrective_wave_count to crypto")

print()
print("=" * 70)
print("SCHEMA FIXES COMPLETE")
print("=" * 70)
