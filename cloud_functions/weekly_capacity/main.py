#!/usr/bin/env python3
"""
Weekly Capacity Increase Scheduler
==================================
Automatically increases TwelveData capacity by 10% each week
Starting at 50%, increasing to 95% over 5 weeks

Week 1: 50% (576,000 credits/day)
Week 2: 60% (691,200 credits/day)
Week 3: 70% (806,400 credits/day)
Week 4: 80% (921,600 credits/day)
Week 5: 90% (1,036,800 credits/day)
Week 6: 95% (1,094,400 credits/day) - maintain
"""

import functions_framework
from google.cloud import bigquery, firestore
from datetime import datetime, timedelta
import json
import requests
import time

# Configuration
PROJECT_ID = "aialgotradehits"
DATASET_ID = "crypto_trading_data"
TWELVEDATA_API_KEY = "16ee060fd4d34a628a14bcb6f0167565"

# Capacity schedule
CAPACITY_SCHEDULE = {
    1: 50,   # Week 1: 50%
    2: 60,   # Week 2: 60%
    3: 70,   # Week 3: 70%
    4: 80,   # Week 4: 80%
    5: 90,   # Week 5: 90%
    6: 95,   # Week 6+: 95% (maintenance)
}

# S&P 500 Stocks grouped by priority
STOCK_TIERS = {
    'tier1': [  # Top 50 by market cap - always fetch
        "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "BRK.B", "LLY", "TSM", "AVGO",
        "JPM", "V", "UNH", "XOM", "MA", "JNJ", "PG", "HD", "COST", "ABBV",
        "MRK", "CRM", "CVX", "NFLX", "BAC", "AMD", "KO", "PEP", "WMT", "LIN",
        "TMO", "ACN", "MCD", "CSCO", "ABT", "ADBE", "DHR", "WFC", "TXN", "INTC",
        "PM", "INTU", "CMCSA", "IBM", "VZ", "GE", "QCOM", "CAT", "AXP", "AMGN"
    ],
    'tier2': [  # Next 100 - add at 60%
        "ISRG", "NOW", "GS", "NEE", "MS", "SPGI", "PFE", "RTX", "T", "UNP",
        "LOW", "HON", "BKNG", "BLK", "SYK", "ELV", "SBUX", "TJX", "DE", "MDLZ",
        "SCHW", "LMT", "C", "AMAT", "MMC", "ADP", "BMY", "GILD", "ADI", "VRTX",
        "CB", "SLB", "REGN", "PGR", "ZTS", "ETN", "LRCX", "BSX", "CI", "CME",
        "PANW", "MO", "BDX", "SNPS", "FI", "CDNS", "AON", "DUK", "ICE", "SO",
        "HUM", "CL", "EQIX", "ITW", "NOC", "WM", "KLAC", "SHW", "CSX", "MCO",
        "PLD", "APD", "USB", "MAR", "CMG", "PYPL", "MCK", "TGT", "COP", "GD",
        "NSC", "EMR", "MPC", "ORLY", "PH", "CTAS", "ROP", "MMM", "PCAR", "AZO",
        "CARR", "FDX", "MSI", "PSX", "HLT", "AFL", "AEP", "TFC", "HCA", "MET",
        "MCHP", "PSA", "AIG", "WELL", "TRV", "OXY", "KMB", "DXCM", "EW", "ECL"
    ],
    'tier3': [  # Remaining S&P 500 - add at 70%+
        "NUE", "SRE", "TEL", "FTNT", "ROST", "DLR", "IDXX", "PCG", "PAYX", "GIS",
        "D", "CCI", "O", "AJG", "VLO", "KDP", "YUM", "FAST", "EA", "A",
        "IQV", "AME", "CTVA", "KR", "PEG", "BK", "VRSK", "FANG", "XEL", "DVN",
        "GEHC", "ED", "HES", "HAL", "EXC", "CTSH", "VMC", "DOW", "MNST", "HPQ",
        "PWR", "PRU", "ROK", "VICI", "CPRT", "KHC", "KEYS", "BIIB", "RCL", "GPN",
        "IT", "ANSS", "AVB", "DAL", "SYY", "DD", "STZ", "MLM", "ON", "CBRE",
        "WTW", "EIX", "LYB", "URI", "TROW", "WAB", "MTD", "DOV", "ACGL", "EXR",
        "CHD", "IR", "SBAC", "PPG", "WEC", "GRMN", "IFF", "TTWO", "GWW", "WST"
    ]
}

# ETF Tiers
ETF_TIERS = {
    'tier1': [  # TOP 20 ETFs by AUM (>$4.8 trillion) - ALWAYS fetch
        # S&P 500 ETFs ($2.4T combined)
        "VOO", "IVV", "SPY", "SPLG",
        # Total Market & Growth
        "VTI", "QQQ", "VUG", "VGT", "IWF",
        # Value
        "VTV",
        # International Developed
        "VEA", "IEFA", "VXUS",
        # Emerging Markets
        "IEMG", "VWO",
        # Bonds
        "BND", "AGG",
        # Mid-Cap & Dividend
        "IJH", "VIG",
        # Gold
        "GLD"
    ],
    'tier2': [  # Sector ETFs - add at 60%
        "XLF", "XLK", "XLV", "XLE", "XLI", "XLP", "XLY", "XLU", "XLB", "XLRE",
        "XLC", "VHT", "VFH", "VNQ", "VDE", "VIS", "VCR", "VDC", "VAW",
        "IWM", "DIA", "EFA", "EEM", "IWD", "IJR", "MDY", "RSP"
    ],
    'tier3': [  # Thematic/Specialty - add at 70%+
        "ARKK", "ARKW", "ARKF", "ARKG", "ARKQ", "SOXX", "SMH", "XBI", "IBB", "ICLN",
        "TAN", "LIT", "BOTZ", "ROBO", "AIQ", "HACK", "CIBR", "FINX", "IPAY", "BLOK",
        "TLT", "IEF", "SHY", "LQD", "HYG", "JNK", "TIP", "VCIT",
        "SLV", "IAU", "GDX", "USO", "UNG", "DBA", "DBC", "PDBC", "GDXJ"
    ]
}


def get_current_week():
    """Get current week number since start"""
    # Start date: December 17, 2025
    start_date = datetime(2025, 12, 17)
    today = datetime.now()
    weeks = (today - start_date).days // 7 + 1
    return min(weeks, 6)  # Cap at week 6


def get_capacity_percent():
    """Get current capacity percentage based on week"""
    week = get_current_week()
    return CAPACITY_SCHEDULE.get(week, 95)


def get_symbols_for_capacity(capacity_pct):
    """Get symbols to fetch based on current capacity"""
    stocks = STOCK_TIERS['tier1'].copy()
    etfs = ETF_TIERS['tier1'].copy()

    if capacity_pct >= 60:
        stocks.extend(STOCK_TIERS['tier2'])
        etfs.extend(ETF_TIERS['tier2'])

    if capacity_pct >= 70:
        stocks.extend(STOCK_TIERS['tier3'])
        etfs.extend(ETF_TIERS['tier3'])

    return stocks, etfs


def fetch_symbol_data(symbol, api_key):
    """Fetch daily data for a symbol"""
    url = "https://api.twelvedata.com/time_series"
    params = {
        'symbol': symbol,
        'interval': '1day',
        'outputsize': 30,  # Last 30 days
        'apikey': api_key
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        data = response.json()
        if 'values' in data:
            return data['values']
        return None
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None


def fetch_fundamentals(symbol, endpoint, api_key):
    """Fetch fundamental data"""
    url = f"https://api.twelvedata.com{endpoint}"
    params = {'symbol': symbol, 'apikey': api_key}

    try:
        response = requests.get(url, params=params, timeout=30)
        return response.json()
    except Exception as e:
        print(f"Error fetching {endpoint} for {symbol}: {e}")
        return None


@functions_framework.http
def weekly_capacity_fetch(request):
    """Main entry point - Cloud Function"""

    week = get_current_week()
    capacity_pct = get_capacity_percent()
    max_calls = int(800 * capacity_pct / 100)

    print(f"="*60)
    print(f"WEEKLY CAPACITY FETCH - Week {week}")
    print(f"Capacity: {capacity_pct}% ({max_calls} calls/min)")
    print(f"="*60)

    stocks, etfs = get_symbols_for_capacity(capacity_pct)

    print(f"Stocks to fetch: {len(stocks)}")
    print(f"ETFs to fetch: {len(etfs)}")

    # Initialize BigQuery
    client = bigquery.Client(project=PROJECT_ID)

    results = {
        'week': week,
        'capacity_pct': capacity_pct,
        'stocks_fetched': 0,
        'etfs_fetched': 0,
        'fundamentals_fetched': 0,
        'errors': []
    }

    calls_made = 0
    minute_start = time.time()

    # Rate limiting helper
    def rate_limit():
        nonlocal calls_made, minute_start
        if time.time() - minute_start >= 60:
            minute_start = time.time()
            calls_made = 0

        if calls_made >= max_calls:
            sleep_time = 60 - (time.time() - minute_start) + 1
            print(f"Rate limit: sleeping {sleep_time:.1f}s")
            time.sleep(sleep_time)
            minute_start = time.time()
            calls_made = 0

        calls_made += 1
        time.sleep(0.15)  # 150ms delay

    # Fetch stocks
    print("\n--- Fetching Stocks ---")
    for symbol in stocks[:50]:  # Limit for function timeout
        rate_limit()
        data = fetch_symbol_data(symbol, TWELVEDATA_API_KEY)
        if data:
            results['stocks_fetched'] += 1
            print(f"  {symbol}: OK")
        else:
            print(f"  {symbol}: FAILED")

    # Fetch ETFs
    print("\n--- Fetching ETFs ---")
    for symbol in etfs[:20]:
        rate_limit()
        data = fetch_symbol_data(symbol, TWELVEDATA_API_KEY)
        if data:
            results['etfs_fetched'] += 1
            print(f"  {symbol}: OK")
        else:
            print(f"  {symbol}: FAILED")

    # Fetch fundamentals for top stocks at higher capacity
    if capacity_pct >= 60:
        print("\n--- Fetching Fundamentals ---")
        for symbol in stocks[:20]:
            # Earnings
            rate_limit()
            data = fetch_fundamentals(symbol, '/earnings', TWELVEDATA_API_KEY)
            if data and 'earnings' in data:
                results['fundamentals_fetched'] += 1

            # Dividends
            rate_limit()
            data = fetch_fundamentals(symbol, '/dividends', TWELVEDATA_API_KEY)
            if data and 'dividends' in data:
                results['fundamentals_fetched'] += 1

    # Log results
    print(f"\n{'='*60}")
    print("WEEKLY FETCH COMPLETE")
    print(f"{'='*60}")
    print(f"Stocks: {results['stocks_fetched']}")
    print(f"ETFs: {results['etfs_fetched']}")
    print(f"Fundamentals: {results['fundamentals_fetched']}")

    # Store capacity tracking
    try:
        db = firestore.Client(project=PROJECT_ID)
        db.collection('capacity_tracking').document(f'week_{week}').set({
            'timestamp': datetime.now().isoformat(),
            'week': week,
            'capacity_percent': capacity_pct,
            'results': results
        })
    except Exception as e:
        print(f"Firestore logging failed: {e}")

    return json.dumps(results)


if __name__ == "__main__":
    # Test locally
    result = weekly_capacity_fetch(None)
    print(result)
