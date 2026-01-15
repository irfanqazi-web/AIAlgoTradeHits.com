#!/usr/bin/env python3
"""
Calculate Stock Market Trading Days
US Stock Market is open Mon-Fri except holidays
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from datetime import datetime, timedelta
import pandas as pd

# US Stock Market Holidays (NYSE/NASDAQ) - 2023 to 2025
US_MARKET_HOLIDAYS = {
    # 2023
    '2023-01-02',  # New Year's Day observed
    '2023-01-16',  # MLK Day
    '2023-02-20',  # Presidents Day
    '2023-04-07',  # Good Friday
    '2023-05-29',  # Memorial Day
    '2023-06-19',  # Juneteenth
    '2023-07-04',  # Independence Day
    '2023-09-04',  # Labor Day
    '2023-11-23',  # Thanksgiving
    '2023-12-25',  # Christmas

    # 2024
    '2024-01-01',  # New Year's Day
    '2024-01-15',  # MLK Day
    '2024-02-19',  # Presidents Day
    '2024-03-29',  # Good Friday
    '2024-05-27',  # Memorial Day
    '2024-06-19',  # Juneteenth
    '2024-07-04',  # Independence Day
    '2024-09-02',  # Labor Day
    '2024-11-28',  # Thanksgiving
    '2024-12-25',  # Christmas

    # 2025
    '2025-01-01',  # New Year's Day
    '2025-01-20',  # MLK Day
    '2025-02-17',  # Presidents Day
    '2025-04-18',  # Good Friday
    '2025-05-26',  # Memorial Day
    '2025-06-19',  # Juneteenth
    '2025-07-04',  # Independence Day
    '2025-09-01',  # Labor Day
    '2025-11-27',  # Thanksgiving
    '2025-12-25',  # Christmas
}


def is_trading_day(date):
    """Check if a date is a US stock market trading day"""
    # Check if weekend (Sat=5, Sun=6)
    if date.weekday() >= 5:
        return False

    # Check if holiday
    date_str = date.strftime('%Y-%m-%d')
    if date_str in US_MARKET_HOLIDAYS:
        return False

    return True


def count_trading_days(start_date, end_date):
    """Count trading days between two dates"""
    current = start_date
    count = 0
    trading_days = []

    while current <= end_date:
        if is_trading_day(current):
            count += 1
            trading_days.append(current)
        current += timedelta(days=1)

    return count, trading_days


def main():
    # Data coverage in BigQuery: 2023-11-27 to 2025-12-08
    start_date = datetime(2023, 11, 27)
    end_date = datetime(2025, 12, 9)  # Yesterday (latest trading day)

    print("=" * 70)
    print("STOCK MARKET TRADING DAYS CALCULATION")
    print("=" * 70)
    print(f"\nDate Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

    # Count trading days
    total_trading_days, trading_days = count_trading_days(start_date, end_date)

    print(f"\nTotal Calendar Days: {(end_date - start_date).days + 1}")
    print(f"Total Trading Days: {total_trading_days}")

    # Calculate by year
    print("\n" + "-" * 40)
    print("Trading Days by Year:")
    print("-" * 40)

    years = {}
    for d in trading_days:
        year = d.year
        if year not in years:
            years[year] = 0
        years[year] += 1

    for year, days in sorted(years.items()):
        print(f"  {year}: {days} trading days")

    # Show first and last 10 trading days
    print("\n" + "-" * 40)
    print("First 10 Trading Days:")
    print("-" * 40)
    for d in trading_days[:10]:
        print(f"  {d.strftime('%Y-%m-%d %A')}")

    print("\n" + "-" * 40)
    print("Last 10 Trading Days:")
    print("-" * 40)
    for d in trading_days[-10:]:
        print(f"  {d.strftime('%Y-%m-%d %A')}")

    # Expected records per symbol
    print("\n" + "=" * 70)
    print("EXPECTED RECORDS PER SYMBOL")
    print("=" * 70)
    print(f"\nEach symbol should have: {total_trading_days} records")
    print(f"For 106 symbols, total expected rows: {total_trading_days * 106:,}")

    # Current data stats
    print("\n" + "-" * 40)
    print("Current Data Status:")
    print("-" * 40)
    print("  Current rows in database: ~30,560")
    print(f"  Expected rows: {total_trading_days * 106:,}")
    print(f"  Missing rows: ~{(total_trading_days * 106) - 30560:,}")

    return total_trading_days, trading_days


if __name__ == "__main__":
    total, days = main()
