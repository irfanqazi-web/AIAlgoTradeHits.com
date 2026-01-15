"""Fix schema issues and restart backfills automatically"""
import subprocess
import time

print("Fixing schema issues...")

# Add trend_direction to stock_analysis
print("1. Adding trend_direction to stock_analysis...")
subprocess.run([
    'bq', 'query', '--use_legacy_sql=false', '--project_id=cryptobot-462709',
    'ALTER TABLE crypto_trading_data.stock_analysis ADD COLUMN trend_direction STRING'
], capture_output=True)

# Add trend_direction to crypto_analysis
print("2. Adding trend_direction to crypto_analysis...")
subprocess.run([
    'bq', 'query', '--use_legacy_sql=false', '--project_id=cryptobot-462709',
    'ALTER TABLE crypto_trading_data.crypto_analysis ADD COLUMN trend_direction STRING'
], capture_output=True)

print("Schema fixes complete!")
print()
print("Starting backfills in 3 seconds...")
time.sleep(3)

# Start crypto backfill
print("Starting crypto backfill...")
subprocess.Popen(
    'python backfill_crypto_indicators_complete.py > crypto_backfill_log.txt 2>&1',
    shell=True
)

# Start stock backfill
print("Starting stock backfill...")
subprocess.Popen(
    'python backfill_stock_indicators.py > stock_backfill_log.txt 2>&1',
    shell=True
)

print()
print("Both backfills started successfully!")
print("Monitor progress with: python monitor_backfills.py")
