"""
Monitor backfill processes and report when complete
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import time
import os
from datetime import datetime

def check_backfill_status():
    """Check if backfill processes are still running and their progress"""

    print("=" * 70)
    print(f"BACKFILL MONITOR - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()

    # Check crypto backfill
    crypto_log = "crypto_backfill_log.txt"
    if os.path.exists(crypto_log):
        with open(crypto_log, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        # Find completed pairs
        completed = [line for line in lines if '✓ Completed' in line or 'Completed' in line]
        processing = [line for line in lines if 'Processing' in line and 'INFO:__main__:Processing' in line]
        errors = [line for line in lines if 'ERROR' in line]

        print(f"📊 CRYPTO BACKFILL STATUS")
        print(f"   Pairs processed: {len(completed)}")
        print(f"   Currently processing: {processing[-1].split('Processing')[-1].strip() if processing else 'Unknown'}")
        print(f"   Errors encountered: {len(errors)}")

        # Check if complete
        if '=' * 70 in ''.join(lines[-50:]) and 'BACKFILL COMPLETE' in ''.join(lines[-50:]):
            print(f"   ✅ STATUS: COMPLETE!")
            crypto_done = True
        else:
            print(f"   ⏳ STATUS: Running...")
            crypto_done = False
    else:
        print(f"📊 CRYPTO BACKFILL STATUS")
        print(f"   ❌ Log file not found")
        crypto_done = False

    print()

    # Check stock backfill
    stock_log = "stock_backfill_log.txt"
    if os.path.exists(stock_log):
        with open(stock_log, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        # Find completed symbols
        completed = [line for line in lines if '✓ Completed' in line or 'Completed' in line]
        processing = [line for line in lines if 'Processing' in line and 'INFO:__main__:Processing' in line]
        errors = [line for line in lines if 'ERROR' in line]

        print(f"📈 STOCK BACKFILL STATUS")
        print(f"   Symbols processed: {len(completed)}")
        print(f"   Currently processing: {processing[-1].split('Processing')[-1].strip() if processing else 'Unknown'}")
        print(f"   Errors encountered: {len(errors)}")

        # Check if complete
        if '=' * 70 in ''.join(lines[-50:]) and 'BACKFILL COMPLETE' in ''.join(lines[-50:]):
            print(f"   ✅ STATUS: COMPLETE!")
            stock_done = True
        else:
            print(f"   ⏳ STATUS: Running...")
            stock_done = False
    else:
        print(f"📈 STOCK BACKFILL STATUS")
        print(f"   ❌ Log file not found")
        stock_done = False

    print()
    print("=" * 70)

    return crypto_done, stock_done

def main():
    """Monitor until both backfills complete"""

    check_interval = 300  # Check every 5 minutes

    print("🔄 Starting backfill monitor...")
    print(f"⏰ Checking every {check_interval // 60} minutes")
    print()

    while True:
        crypto_done, stock_done = check_backfill_status()

        if crypto_done and stock_done:
            print()
            print("🎉" * 35)
            print("🎉 ALL BACKFILLS COMPLETE! 🎉")
            print("🎉" * 35)
            print()
            print("✅ Both crypto and stock indicator calculations are finished!")
            print("✅ All historical data now has complete technical indicators")
            print("✅ Ready to connect the app to BigQuery for real data")
            print()
            break

        print(f"\n⏰ Next check in {check_interval // 60} minutes...\n")
        time.sleep(check_interval)

if __name__ == "__main__":
    main()
