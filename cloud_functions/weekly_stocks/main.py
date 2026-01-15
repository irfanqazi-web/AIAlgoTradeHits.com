"""
Weekly Stock Data Loader - Cloud Function
Fetches ALL US stocks from Twelve Data API and loads into BigQuery
Designed to run once per week (Sunday night)
"""

import functions_framework
import requests
import pandas as pd
import numpy as np
from google.cloud import bigquery
from datetime import datetime, timezone, timedelta
import time
import uuid

PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'
TWELVE_DATA_API_KEY = '16ee060fd4d34a628a14bcb6f0167565'

# Sector/Industry mapping for day trading categories
SECTOR_CATEGORIES = {
    'Technology': 'growth',
    'Healthcare': 'defensive',
    'Financial Services': 'cyclical',
    'Consumer Cyclical': 'cyclical',
    'Communication Services': 'growth',
    'Industrials': 'cyclical',
    'Consumer Defensive': 'defensive',
    'Energy': 'cyclical',
    'Utilities': 'defensive',
    'Real Estate': 'income',
    'Basic Materials': 'cyclical'
}


def log_execution(client, execution_id, scheduler_name, function_name, table_name,
                  start_time, end_time=None, status='RUNNING', error_msg=None,
                  total_symbols=0, successful=0, failed=0, records_inserted=0,
                  api_calls=0, was_manual=False):
    """Log scheduler execution to BigQuery"""
    duration = None
    if end_time:
        duration = (end_time - start_time).total_seconds()

    log_record = {
        'execution_id': execution_id,
        'scheduler_name': scheduler_name,
        'function_name': function_name,
        'table_name': table_name,
        'execution_date': start_time.date().isoformat(),
        'start_time': start_time.isoformat(),
        'end_time': end_time.isoformat() if end_time else None,
        'duration_seconds': duration,
        'duration_minutes': duration / 60 if duration else None,
        'status': status,
        'error_message': error_msg,
        'total_symbols': total_symbols,
        'successful_symbols': successful,
        'failed_symbols': failed,
        'records_inserted': records_inserted,
        'api_calls_made': api_calls,
        'was_manual_trigger': was_manual,
        'trigger_source': 'manual' if was_manual else 'scheduler',
        'created_at': datetime.now(timezone.utc).isoformat()
    }

    table_id = f"{PROJECT_ID}.{DATASET_ID}.scheduler_execution_log"
    errors = client.insert_rows_json(table_id, [log_record])
    return len(errors) == 0


def get_all_us_stocks():
    """Get list of all US stocks from Twelve Data"""
    url = "https://api.twelvedata.com/stocks"
    params = {
        'country': 'United States',
        'apikey': TWELVE_DATA_API_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=60)
        data = response.json()

        if 'data' not in data:
            return None, data.get('message', 'No data')

        stocks = []
        for item in data['data']:
            # Filter to common stocks and ETFs (skip warrants, units, etc)
            if item.get('type') in ['Common Stock', 'ETF']:
                stocks.append({
                    'symbol': item['symbol'],
                    'name': item['name'],
                    'exchange': item['exchange'],
                    'type': item['type'],
                    'currency': item.get('currency', 'USD')
                })

        return stocks, None
    except Exception as e:
        return None, str(e)


def fetch_stock_quote(symbol):
    """Fetch current quote for a stock"""
    url = "https://api.twelvedata.com/quote"
    params = {
        'symbol': symbol,
        'apikey': TWELVE_DATA_API_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        data = response.json()

        if 'code' in data and data['code'] != 200:
            return None, data.get('message', 'API Error')

        return data, None
    except Exception as e:
        return None, str(e)


def fetch_stock_statistics(symbol):
    """Fetch key statistics for a stock"""
    url = "https://api.twelvedata.com/statistics"
    params = {
        'symbol': symbol,
        'apikey': TWELVE_DATA_API_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        data = response.json()

        if 'code' in data and data['code'] != 200:
            return None, data.get('message', 'API Error')

        return data, None
    except Exception as e:
        return None, str(e)


def fetch_weekly_data(symbol):
    """Fetch weekly OHLC data for a stock"""
    url = "https://api.twelvedata.com/time_series"
    params = {
        'symbol': symbol,
        'interval': '1week',
        'outputsize': 52,  # 1 year of weekly data
        'apikey': TWELVE_DATA_API_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        data = response.json()

        if 'values' not in data:
            return None, data.get('message', 'No data')

        return data['values'], None
    except Exception as e:
        return None, str(e)


def calculate_metrics(quote, weekly_data, stats=None):
    """Calculate trading metrics and scores"""
    metrics = {}

    try:
        close = float(quote.get('close', 0))
        open_price = float(quote.get('open', 0))
        high = float(quote.get('high', 0))
        low = float(quote.get('low', 0))
        prev_close = float(quote.get('previous_close', close))
        volume = int(float(quote.get('volume', 0)))

        # Basic price data
        metrics['current_price'] = close
        metrics['open_price'] = open_price
        metrics['high_price'] = high
        metrics['low_price'] = low
        metrics['close_price'] = close
        metrics['previous_close'] = prev_close
        metrics['volume'] = volume

        # Weekly change
        if prev_close > 0:
            metrics['weekly_change'] = close - prev_close
            metrics['weekly_change_percent'] = ((close - prev_close) / prev_close) * 100
        else:
            metrics['weekly_change'] = 0
            metrics['weekly_change_percent'] = 0

        # 52-week range
        metrics['week_52_high'] = float(quote.get('fifty_two_week', {}).get('high', 0))
        metrics['week_52_low'] = float(quote.get('fifty_two_week', {}).get('low', 0))

        if metrics['week_52_high'] > 0:
            metrics['percent_from_52_high'] = ((metrics['week_52_high'] - close) / metrics['week_52_high']) * 100
        if metrics['week_52_low'] > 0:
            metrics['percent_from_52_low'] = ((close - metrics['week_52_low']) / metrics['week_52_low']) * 100

        # Calculate volatility from weekly data
        if weekly_data and len(weekly_data) >= 4:
            closes = [float(w['close']) for w in weekly_data[:4]]
            highs = [float(w['high']) for w in weekly_data[:4]]
            lows = [float(w['low']) for w in weekly_data[:4]]

            # Weekly volatility (standard deviation of returns)
            if len(closes) >= 2:
                returns = [(closes[i] - closes[i+1]) / closes[i+1] * 100 for i in range(len(closes)-1) if closes[i+1] > 0]
                if returns:
                    metrics['volatility_weekly'] = np.std(returns)

            # ATR calculation
            tr_values = []
            for i in range(len(highs)):
                if i == 0:
                    tr = highs[i] - lows[i]
                else:
                    prev_close_w = float(weekly_data[i-1]['close']) if i < len(weekly_data) else closes[i-1]
                    tr = max(highs[i] - lows[i], abs(highs[i] - prev_close_w), abs(lows[i] - prev_close_w))
                tr_values.append(tr)
            if tr_values:
                metrics['atr'] = np.mean(tr_values)
                if close > 0:
                    metrics['atr_percent'] = (metrics['atr'] / close) * 100

        # Calculate scores
        metrics['day_trade_score'] = calculate_day_trade_score(metrics, volume)
        metrics['liquidity_score'] = calculate_liquidity_score(volume)
        metrics['momentum_score'] = calculate_momentum_score(metrics)

        # Market cap category
        if stats and 'statistics' in stats:
            market_cap = stats['statistics'].get('valuations_metrics', {}).get('market_capitalization')
            if market_cap:
                metrics['market_cap'] = float(market_cap)
                metrics['market_cap_category'] = categorize_market_cap(float(market_cap))

            # PE ratio
            pe = stats['statistics'].get('valuations_metrics', {}).get('trailing_pe')
            if pe:
                metrics['pe_ratio'] = float(pe)

            # EPS
            eps = stats['statistics'].get('financials', {}).get('diluted_eps_ttm')
            if eps:
                metrics['eps'] = float(eps)

            # Beta
            beta = stats['statistics'].get('stock_price_summary', {}).get('beta')
            if beta:
                metrics['beta'] = float(beta)

        # Volatility category
        vol = metrics.get('volatility_weekly', 0)
        if vol > 5:
            metrics['volatility_category'] = 'high'
        elif vol > 2:
            metrics['volatility_category'] = 'medium'
        else:
            metrics['volatility_category'] = 'low'

        # Momentum category
        change_pct = metrics.get('weekly_change_percent', 0)
        if change_pct > 5:
            metrics['momentum_category'] = 'strong_up'
        elif change_pct > 2:
            metrics['momentum_category'] = 'up'
        elif change_pct < -5:
            metrics['momentum_category'] = 'strong_down'
        elif change_pct < -2:
            metrics['momentum_category'] = 'down'
        else:
            metrics['momentum_category'] = 'neutral'

    except Exception as e:
        print(f"Error calculating metrics: {e}")

    return metrics


def calculate_day_trade_score(metrics, volume):
    """Calculate day trading suitability score (0-100)"""
    score = 50  # Base score

    # Volume factor (higher is better for day trading)
    if volume > 10000000:
        score += 20
    elif volume > 5000000:
        score += 15
    elif volume > 1000000:
        score += 10
    elif volume > 500000:
        score += 5
    elif volume < 100000:
        score -= 20

    # Volatility factor (moderate volatility is ideal)
    vol = metrics.get('volatility_weekly', 0)
    if 2 <= vol <= 5:
        score += 15  # Sweet spot
    elif vol > 5:
        score += 10  # High volatility, more risk
    elif vol < 1:
        score -= 10  # Too stable for day trading

    # ATR factor
    atr_pct = metrics.get('atr_percent', 0)
    if 2 <= atr_pct <= 5:
        score += 10
    elif atr_pct > 5:
        score += 5

    # Price range factor (prefer $5-$500)
    price = metrics.get('current_price', 0)
    if 10 <= price <= 200:
        score += 5
    elif price < 5 or price > 1000:
        score -= 10

    return min(100, max(0, score))


def calculate_liquidity_score(volume):
    """Calculate liquidity score (0-100)"""
    if volume >= 20000000:
        return 100
    elif volume >= 10000000:
        return 90
    elif volume >= 5000000:
        return 80
    elif volume >= 1000000:
        return 70
    elif volume >= 500000:
        return 60
    elif volume >= 100000:
        return 40
    elif volume >= 50000:
        return 20
    else:
        return 10


def calculate_momentum_score(metrics):
    """Calculate momentum score (0-100)"""
    score = 50
    change = metrics.get('weekly_change_percent', 0)

    if change > 10:
        score += 30
    elif change > 5:
        score += 20
    elif change > 2:
        score += 10
    elif change < -10:
        score -= 30
    elif change < -5:
        score -= 20
    elif change < -2:
        score -= 10

    return min(100, max(0, score))


def categorize_market_cap(market_cap):
    """Categorize market cap"""
    if market_cap >= 200e9:
        return 'mega'
    elif market_cap >= 10e9:
        return 'large'
    elif market_cap >= 2e9:
        return 'mid'
    elif market_cap >= 300e6:
        return 'small'
    else:
        return 'micro'


def process_stock(stock_info, client):
    """Process a single stock"""
    symbol = stock_info['symbol']

    # Fetch quote
    quote, err = fetch_stock_quote(symbol)
    if not quote:
        return None, f"Quote error: {err}"

    # Fetch weekly data
    weekly_data, err = fetch_weekly_data(symbol)

    # Try to get statistics (may not be available for all stocks)
    stats, _ = fetch_stock_statistics(symbol)

    # Calculate metrics
    metrics = calculate_metrics(quote, weekly_data, stats)

    # Determine trend
    if metrics.get('current_price', 0) > metrics.get('sma_20', 0):
        metrics['above_sma_20'] = True
        metrics['trend_short'] = 'bullish'
    else:
        metrics['above_sma_20'] = False
        metrics['trend_short'] = 'bearish'

    # Build record
    now = datetime.now(timezone.utc)
    week_start = now - timedelta(days=now.weekday())
    week_end = week_start + timedelta(days=6)

    record = {
        'symbol': symbol,
        'name': stock_info.get('name', ''),
        'exchange': stock_info.get('exchange', ''),
        'type': stock_info.get('type', ''),
        'sector': quote.get('sector', ''),
        'industry': quote.get('industry', ''),
        'country': 'United States',
        'currency': stock_info.get('currency', 'USD'),
        **metrics,
        'week_start_date': week_start.date().isoformat(),
        'week_end_date': week_end.date().isoformat(),
        'fetch_timestamp': now.isoformat(),
        'data_source': 'twelvedata',
        'is_active_pick': False,
        'active_pick_reason': None
    }

    return record, None


def upload_batch(records, client):
    """Upload batch of records to BigQuery"""
    if not records:
        return 0

    table_id = f"{PROJECT_ID}.{DATASET_ID}.stocks_weekly_summary"
    df = pd.DataFrame(records)

    # Convert dates
    for col in ['week_start_date', 'week_end_date']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col]).dt.date

    df['fetch_timestamp'] = pd.to_datetime(df['fetch_timestamp'])

    # Replace inf with nan
    df = df.replace([np.inf, -np.inf], np.nan)

    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    )

    try:
        job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
        job.result()
        return len(records)
    except Exception as e:
        print(f"Upload error: {e}")
        return 0


@functions_framework.http
def weekly_stock_fetcher(request):
    """Main entry point for Cloud Function"""
    execution_id = str(uuid.uuid4())
    start_time = datetime.now(timezone.utc)
    client = bigquery.Client(project=PROJECT_ID)

    # Check if manual trigger
    was_manual = request.args.get('manual', 'false').lower() == 'true'

    # Log start
    log_execution(client, execution_id, 'weekly-stock-fetcher', 'weekly_stock_fetcher',
                  'stocks_weekly_summary', start_time, was_manual=was_manual)

    try:
        # Get all US stocks
        print("Fetching US stock list...")
        stocks, err = get_all_us_stocks()

        if not stocks:
            end_time = datetime.now(timezone.utc)
            log_execution(client, execution_id, 'weekly-stock-fetcher', 'weekly_stock_fetcher',
                          'stocks_weekly_summary', start_time, end_time, 'FAILED',
                          f"Failed to get stock list: {err}", was_manual=was_manual)
            return f"Error: {err}", 500

        total_stocks = len(stocks)
        print(f"Found {total_stocks} US stocks")

        successful = 0
        failed = 0
        records_inserted = 0
        batch = []
        batch_size = 100
        api_calls = 1  # Initial stock list call

        for i, stock in enumerate(stocks):
            try:
                record, err = process_stock(stock, client)
                api_calls += 3  # quote + weekly + stats

                if record:
                    batch.append(record)
                    successful += 1
                else:
                    failed += 1
                    print(f"Failed {stock['symbol']}: {err}")

                # Upload batch
                if len(batch) >= batch_size:
                    inserted = upload_batch(batch, client)
                    records_inserted += inserted
                    print(f"Progress: {i+1}/{total_stocks} - Batch uploaded: {inserted}")
                    batch = []

                # Rate limiting (8 calls/min for free tier)
                time.sleep(0.5)

                # Progress logging
                if (i + 1) % 500 == 0:
                    print(f"Processed {i+1}/{total_stocks} stocks")

            except Exception as e:
                failed += 1
                print(f"Error processing {stock.get('symbol', 'unknown')}: {e}")

        # Upload remaining batch
        if batch:
            inserted = upload_batch(batch, client)
            records_inserted += inserted

        # Log completion
        end_time = datetime.now(timezone.utc)
        status = 'SUCCESS' if failed == 0 else 'PARTIAL' if successful > 0 else 'FAILED'

        log_execution(client, execution_id, 'weekly-stock-fetcher', 'weekly_stock_fetcher',
                      'stocks_weekly_summary', start_time, end_time, status,
                      total_symbols=total_stocks, successful=successful, failed=failed,
                      records_inserted=records_inserted, api_calls=api_calls, was_manual=was_manual)

        duration = (end_time - start_time).total_seconds() / 60
        return f"Completed: {successful}/{total_stocks} stocks, {records_inserted} records in {duration:.1f} min", 200

    except Exception as e:
        end_time = datetime.now(timezone.utc)
        log_execution(client, execution_id, 'weekly-stock-fetcher', 'weekly_stock_fetcher',
                      'stocks_weekly_summary', start_time, end_time, 'FAILED',
                      str(e), was_manual=was_manual)
        return f"Error: {str(e)}", 500


# For local testing
if __name__ == "__main__":
    class MockRequest:
        args = {'manual': 'true'}

    result, code = weekly_stock_fetcher(MockRequest())
    print(f"Result: {result} (code: {code})")
