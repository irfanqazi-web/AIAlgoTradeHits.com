"""
Fetch Today's Data from Twelve Data API
Downloads fresh quotes for all 6 asset types and uploads to BigQuery
"""
import requests
import time
from datetime import datetime, timezone
from google.cloud import bigquery
import sys
import io

# Windows UTF-8 fix
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'crypto_trading_data'
TWELVE_DATA_API_KEY = '16ee060fd4d34a628a14bcb6f0167565'

# Asset symbols to fetch
STOCKS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B', 'UNH', 'JNJ',
    'V', 'JPM', 'PG', 'MA', 'HD', 'CVX', 'MRK', 'ABBV', 'PFE', 'KO',
    'PEP', 'COST', 'AVGO', 'TMO', 'MCD', 'WMT', 'CSCO', 'ABT', 'ACN', 'DHR',
    'NKE', 'DIS', 'VZ', 'ADBE', 'CRM', 'TXN', 'NEE', 'PM', 'UNP', 'RTX',
    'INTC', 'AMD', 'IBM', 'QCOM', 'ORCL', 'LOW', 'CAT', 'BA', 'GE', 'SPGI'
]

CRYPTOS = [
    'BTC/USD', 'ETH/USD', 'XRP/USD', 'SOL/USD', 'ADA/USD', 'DOGE/USD', 'DOT/USD',
    'AVAX/USD', 'MATIC/USD', 'LTC/USD', 'LINK/USD', 'UNI/USD', 'ATOM/USD', 'XLM/USD',
    'ALGO/USD', 'VET/USD', 'FIL/USD', 'AAVE/USD', 'EOS/USD', 'XTZ/USD'
]

ETFS = [
    'SPY', 'QQQ', 'IWM', 'DIA', 'VTI', 'VOO', 'VEA', 'VWO', 'EFA', 'EEM',
    'AGG', 'BND', 'LQD', 'TLT', 'GLD', 'SLV', 'USO', 'XLF', 'XLK', 'XLE',
    'XLV', 'XLI', 'XLY', 'XLP', 'XLU', 'ARKK', 'ARKG', 'ARKF', 'VNQ', 'SCHD'
]

FOREX = [
    'EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD', 'USD/CAD', 'NZD/USD',
    'EUR/GBP', 'EUR/JPY', 'GBP/JPY', 'AUD/JPY', 'EUR/CHF', 'EUR/AUD', 'GBP/AUD',
    'USD/SGD', 'USD/HKD', 'USD/MXN', 'USD/ZAR', 'USD/INR', 'EUR/CAD'
]

INDICES = [
    'SPX', 'NDX', 'DJI', 'RUT', 'VIX', 'FTSE', 'DAX', 'CAC', 'N225', 'HSI',
    'STOXX50E', 'IBEX', 'FTSEMIB', 'AEX', 'SMI'
]

COMMODITIES = [
    'XAU/USD', 'XAG/USD', 'XPT/USD', 'XPD/USD', 'CL', 'BZ', 'NG', 'HO',
    'ZC', 'ZW', 'ZS', 'KC', 'CC', 'SB', 'CT', 'LC'
]


def fetch_quote(symbol, asset_type='stock'):
    """Fetch quote data from Twelve Data"""
    try:
        url = f"https://api.twelvedata.com/quote?symbol={symbol}&apikey={TWELVE_DATA_API_KEY}"
        resp = requests.get(url, timeout=15)
        data = resp.json()

        if 'code' in data and data['code'] != 200:
            print(f"  Error for {symbol}: {data.get('message', 'Unknown error')}")
            return None

        current_price = float(data.get('close', 0)) if data.get('close') else 0
        prev_close = float(data.get('previous_close', 0)) if data.get('previous_close') else 0

        weekly_change = current_price - prev_close if prev_close else 0
        weekly_change_pct = (weekly_change / prev_close * 100) if prev_close else 0

        return {
            'symbol': symbol,
            'name': data.get('name', symbol),
            'current_price': current_price,
            'open_price': float(data.get('open', 0)) if data.get('open') else None,
            'high_price': float(data.get('high', 0)) if data.get('high') else None,
            'low_price': float(data.get('low', 0)) if data.get('low') else None,
            'close_price': current_price,
            'previous_close': prev_close,
            'volume': float(data.get('volume', 0)) if data.get('volume') else None,
            'weekly_change': weekly_change,
            'weekly_change_percent': weekly_change_pct,
            'fetch_timestamp': datetime.now(timezone.utc).isoformat(),
            'data_source': 'twelvedata',
            'exchange': data.get('exchange', ''),
        }
    except Exception as e:
        print(f"  Exception for {symbol}: {str(e)[:50]}")
        return None


def fetch_and_upload(symbols, table_name, asset_type, extra_fields=None):
    """Fetch data for symbols and upload to BigQuery"""
    print(f"\n{'='*60}")
    print(f"Fetching {asset_type} data for {len(symbols)} symbols...")
    print(f"Table: {table_name}")
    print(f"{'='*60}")

    client = bigquery.Client(project=PROJECT_ID)
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

    records = []
    for i, symbol in enumerate(symbols):
        print(f"[{i+1}/{len(symbols)}] Fetching {symbol}...", end=" ")

        data = fetch_quote(symbol, asset_type)
        if data:
            # Add extra fields if provided
            if extra_fields:
                data.update(extra_fields)

            # Add common fields that may be missing
            data.setdefault('monthly_change_percent', None)
            data.setdefault('ytd_change_percent', None)
            data.setdefault('week_52_high', None)
            data.setdefault('week_52_low', None)
            data.setdefault('percent_from_52_high', None)
            data.setdefault('percent_from_52_low', None)
            data.setdefault('volatility_weekly', None)
            data.setdefault('volatility_monthly', None)
            data.setdefault('atr', None)
            data.setdefault('atr_percent', None)
            data.setdefault('rsi_weekly', None)
            data.setdefault('macd_weekly', None)
            data.setdefault('macd_signal_weekly', None)
            data.setdefault('sma_20', None)
            data.setdefault('sma_50', None)
            data.setdefault('sma_200', None)
            data.setdefault('trend_short', 'bullish' if data.get('weekly_change_percent', 0) > 0 else 'bearish')
            data.setdefault('trend_medium', None)
            data.setdefault('trend_long', None)
            data.setdefault('above_sma_20', None)
            data.setdefault('above_sma_50', None)
            data.setdefault('above_sma_200', None)
            data.setdefault('volatility_category', 'medium')
            data.setdefault('momentum_category', 'up' if data.get('weekly_change_percent', 0) > 0 else 'down')
            data.setdefault('day_trade_score', 50)
            data.setdefault('liquidity_score', 75)
            data.setdefault('momentum_score', abs(data.get('weekly_change_percent', 0)) * 10)
            data.setdefault('week_start_date', None)
            data.setdefault('week_end_date', None)

            records.append(data)
            print(f"OK - ${data['current_price']:.2f} ({data['weekly_change_percent']:+.2f}%)")
        else:
            print("FAILED")

        # Rate limiting - 8 calls/minute = 7.5 seconds between calls
        time.sleep(8)

    print(f"\nSuccessfully fetched {len(records)} records")

    if records:
        try:
            errors = client.insert_rows_json(table_ref, records)
            if errors:
                print(f"Insert errors: {errors[:3]}")
            else:
                print(f"Successfully uploaded {len(records)} records to {table_name}")
        except Exception as e:
            print(f"Upload error: {e}")

    return len(records)


def main():
    print("="*60)
    print("TWELVE DATA FETCHER - Today's Market Data")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    total_records = 0

    # Fetch Stocks
    stock_fields = {'sector': None, 'industry': None, 'market_cap': None, 'pe_ratio': None, 'dividend_yield': None}
    total_records += fetch_and_upload(STOCKS[:25], 'stocks_weekly_summary', 'stock', stock_fields)

    # Fetch Cryptos
    crypto_fields = {'market_cap': None, 'circulating_supply': None, 'max_supply': None, 'rank': None}
    total_records += fetch_and_upload(CRYPTOS[:10], 'cryptos_weekly_summary', 'crypto', crypto_fields)

    # Fetch ETFs
    etf_fields = {'category': None, 'expense_ratio': None, 'aum': None, 'holdings_count': None}
    total_records += fetch_and_upload(ETFS[:15], 'etfs_weekly_summary', 'etf', etf_fields)

    # Fetch Forex
    forex_fields = {'base_currency': None, 'quote_currency': None, 'pip_value': None}
    total_records += fetch_and_upload(FOREX[:10], 'forex_weekly_summary', 'forex', forex_fields)

    # Fetch Indices
    index_fields = {'country': None, 'components': None}
    total_records += fetch_and_upload(INDICES[:8], 'indices_weekly_summary', 'index', index_fields)

    # Fetch Commodities
    commodity_fields = {'category': None, 'subcategory': None, 'currency': 'USD', 'unit': None}
    total_records += fetch_and_upload(COMMODITIES[:8], 'commodities_weekly_summary', 'commodity', commodity_fields)

    print("\n" + "="*60)
    print(f"COMPLETE! Total records fetched: {total_records}")
    print("="*60)


if __name__ == '__main__':
    main()
