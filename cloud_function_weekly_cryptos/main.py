"""
Weekly Crypto Data Loader - Cloud Function
Fetches ALL cryptos from Twelve Data API and loads into BigQuery
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

# Crypto categories
CRYPTO_CATEGORIES = {
    'BTC': ('Bitcoin', 'Store of Value'),
    'ETH': ('Ethereum', 'Smart Contract Platform'),
    'BNB': ('Binance', 'Exchange Token'),
    'SOL': ('Solana', 'Smart Contract Platform'),
    'XRP': ('Ripple', 'Payment'),
    'ADA': ('Cardano', 'Smart Contract Platform'),
    'AVAX': ('Avalanche', 'Smart Contract Platform'),
    'DOGE': ('Dogecoin', 'Meme'),
    'DOT': ('Polkadot', 'Interoperability'),
    'LINK': ('Chainlink', 'Oracle'),
    'MATIC': ('Polygon', 'Layer 2'),
    'SHIB': ('Shiba Inu', 'Meme'),
    'LTC': ('Litecoin', 'Payment'),
    'ATOM': ('Cosmos', 'Interoperability'),
    'UNI': ('Uniswap', 'DeFi'),
    'XLM': ('Stellar', 'Payment'),
    'XMR': ('Monero', 'Privacy'),
    'FIL': ('Filecoin', 'Storage'),
    'NEAR': ('NEAR Protocol', 'Smart Contract Platform'),
    'AAVE': ('Aave', 'DeFi'),
    'ARB': ('Arbitrum', 'Layer 2'),
    'OP': ('Optimism', 'Layer 2'),
    'INJ': ('Injective', 'DeFi'),
    'SUI': ('Sui', 'Smart Contract Platform'),
    'SEI': ('Sei', 'Smart Contract Platform'),
    'PEPE': ('Pepe', 'Meme'),
    'BONK': ('Bonk', 'Meme'),
    'WIF': ('dogwifhat', 'Meme'),
    'RNDR': ('Render', 'AI/GPU'),
    'FET': ('Fetch.ai', 'AI'),
    'OCEAN': ('Ocean Protocol', 'AI/Data'),
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


def get_all_cryptos():
    """Get list of all crypto pairs from Twelve Data"""
    url = "https://api.twelvedata.com/cryptocurrencies"
    params = {
        'apikey': TWELVE_DATA_API_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=60)
        data = response.json()

        if 'data' not in data:
            return None, data.get('message', 'No data')

        cryptos = []
        seen = set()
        for item in data['data']:
            # Only USD pairs
            if '/USD' in item['symbol'] and item['symbol'] not in seen:
                seen.add(item['symbol'])
                base = item['symbol'].split('/')[0]
                category_info = CRYPTO_CATEGORIES.get(base, (base, 'Other'))
                cryptos.append({
                    'symbol': base,
                    'pair': item['symbol'],
                    'name': category_info[0] if category_info[0] != base else item.get('currency_base', base),
                    'category': category_info[1],
                    'available_exchanges': item.get('available_exchanges', [])
                })

        return cryptos, None
    except Exception as e:
        return None, str(e)


def fetch_crypto_quote(pair):
    """Fetch current quote for a crypto"""
    url = "https://api.twelvedata.com/quote"
    params = {
        'symbol': pair,
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


def fetch_weekly_data(pair):
    """Fetch weekly OHLC data for a crypto"""
    url = "https://api.twelvedata.com/time_series"
    params = {
        'symbol': pair,
        'interval': '1week',
        'outputsize': 52,
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


def calculate_metrics(quote, weekly_data):
    """Calculate trading metrics and scores"""
    metrics = {}

    try:
        close = float(quote.get('close', 0))
        open_price = float(quote.get('open', 0))
        high = float(quote.get('high', 0))
        low = float(quote.get('low', 0))
        prev_close = float(quote.get('previous_close', close))
        volume = float(quote.get('volume', 0))

        # Basic price data
        metrics['current_price'] = close
        metrics['open_price'] = open_price
        metrics['high_price'] = high
        metrics['low_price'] = low
        metrics['close_price'] = close
        metrics['previous_close'] = prev_close
        metrics['volume_24h'] = volume

        # Weekly change
        if prev_close > 0:
            metrics['weekly_change'] = close - prev_close
            metrics['weekly_change_percent'] = ((close - prev_close) / prev_close) * 100
        else:
            metrics['weekly_change'] = 0
            metrics['weekly_change_percent'] = 0

        # 52-week range
        metrics['ath'] = float(quote.get('fifty_two_week', {}).get('high', 0))
        metrics['atl'] = float(quote.get('fifty_two_week', {}).get('low', 0))

        if metrics['ath'] > 0:
            metrics['percent_from_ath'] = ((metrics['ath'] - close) / metrics['ath']) * 100

        # Calculate volatility from weekly data
        if weekly_data and len(weekly_data) >= 4:
            closes = [float(w['close']) for w in weekly_data[:4]]
            highs = [float(w['high']) for w in weekly_data[:4]]
            lows = [float(w['low']) for w in weekly_data[:4]]

            # Weekly volume sum
            volumes = [float(w.get('volume', 0)) for w in weekly_data[:1]]
            metrics['volume_weekly'] = sum(volumes)

            # Weekly volatility
            if len(closes) >= 2:
                returns = [(closes[i] - closes[i+1]) / closes[i+1] * 100 for i in range(len(closes)-1) if closes[i+1] > 0]
                if returns:
                    metrics['volatility_weekly'] = np.std(returns)

            # Monthly volatility (4 weeks)
            if len(weekly_data) >= 4:
                month_closes = [float(w['close']) for w in weekly_data[:4]]
                if len(month_closes) >= 2:
                    month_returns = [(month_closes[i] - month_closes[i+1]) / month_closes[i+1] * 100
                                     for i in range(len(month_closes)-1) if month_closes[i+1] > 0]
                    if month_returns:
                        metrics['volatility_monthly'] = np.std(month_returns)

            # ATR calculation
            tr_values = []
            for i in range(min(len(highs), 4)):
                if i == 0:
                    tr = highs[i] - lows[i]
                else:
                    prev_c = float(weekly_data[i-1]['close']) if i < len(weekly_data) else closes[i-1]
                    tr = max(highs[i] - lows[i], abs(highs[i] - prev_c), abs(lows[i] - prev_c))
                tr_values.append(tr)
            if tr_values:
                metrics['atr'] = np.mean(tr_values)
                if close > 0:
                    metrics['atr_percent'] = (metrics['atr'] / close) * 100

        # Calculate scores
        metrics['day_trade_score'] = calculate_day_trade_score(metrics)
        metrics['liquidity_score'] = calculate_liquidity_score(metrics.get('volume_24h', 0))
        metrics['momentum_score'] = calculate_momentum_score(metrics)

        # Volatility category
        vol = metrics.get('volatility_weekly', 0)
        if vol > 10:
            metrics['volatility_category'] = 'high'
        elif vol > 5:
            metrics['volatility_category'] = 'medium'
        else:
            metrics['volatility_category'] = 'low'

        # Momentum category
        change_pct = metrics.get('weekly_change_percent', 0)
        if change_pct > 10:
            metrics['momentum_category'] = 'strong_up'
        elif change_pct > 5:
            metrics['momentum_category'] = 'up'
        elif change_pct < -10:
            metrics['momentum_category'] = 'strong_down'
        elif change_pct < -5:
            metrics['momentum_category'] = 'down'
        else:
            metrics['momentum_category'] = 'neutral'

        # Market cap category (estimated from volume for cryptos)
        vol_24h = metrics.get('volume_24h', 0)
        if vol_24h > 1e9:
            metrics['market_cap_category'] = 'large'
        elif vol_24h > 100e6:
            metrics['market_cap_category'] = 'mid'
        elif vol_24h > 10e6:
            metrics['market_cap_category'] = 'small'
        else:
            metrics['market_cap_category'] = 'micro'

    except Exception as e:
        print(f"Error calculating metrics: {e}")

    return metrics


def calculate_day_trade_score(metrics):
    """Calculate day trading suitability score (0-100)"""
    score = 50

    # Volume factor
    vol_24h = metrics.get('volume_24h', 0)
    if vol_24h > 1e9:
        score += 25
    elif vol_24h > 100e6:
        score += 20
    elif vol_24h > 10e6:
        score += 10
    elif vol_24h < 1e6:
        score -= 20

    # Volatility factor (cryptos are naturally more volatile)
    vol = metrics.get('volatility_weekly', 0)
    if 5 <= vol <= 15:
        score += 15
    elif vol > 15:
        score += 10
    elif vol < 3:
        score -= 10

    # ATR factor
    atr_pct = metrics.get('atr_percent', 0)
    if 3 <= atr_pct <= 10:
        score += 10
    elif atr_pct > 10:
        score += 5

    return min(100, max(0, score))


def calculate_liquidity_score(volume):
    """Calculate liquidity score (0-100)"""
    if volume >= 1e9:
        return 100
    elif volume >= 500e6:
        return 90
    elif volume >= 100e6:
        return 80
    elif volume >= 50e6:
        return 70
    elif volume >= 10e6:
        return 60
    elif volume >= 1e6:
        return 40
    else:
        return 20


def calculate_momentum_score(metrics):
    """Calculate momentum score (0-100)"""
    score = 50
    change = metrics.get('weekly_change_percent', 0)

    if change > 20:
        score += 35
    elif change > 10:
        score += 25
    elif change > 5:
        score += 15
    elif change < -20:
        score -= 35
    elif change < -10:
        score -= 25
    elif change < -5:
        score -= 15

    return min(100, max(0, score))


def process_crypto(crypto_info, client):
    """Process a single crypto"""
    pair = crypto_info['pair']

    # Fetch quote
    quote, err = fetch_crypto_quote(pair)
    if not quote:
        return None, f"Quote error: {err}"

    # Fetch weekly data
    weekly_data, err = fetch_weekly_data(pair)

    # Calculate metrics
    metrics = calculate_metrics(quote, weekly_data)

    # Build record
    now = datetime.now(timezone.utc)
    week_start = now - timedelta(days=now.weekday())
    week_end = week_start + timedelta(days=6)

    record = {
        'symbol': crypto_info['symbol'],
        'name': crypto_info.get('name', ''),
        'pair': pair,
        'category': crypto_info.get('category', 'Other'),
        'subcategory': None,
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

    table_id = f"{PROJECT_ID}.{DATASET_ID}.cryptos_weekly_summary"
    df = pd.DataFrame(records)

    # Convert dates
    for col in ['week_start_date', 'week_end_date', 'ath_date', 'atl_date']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce').dt.date

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
def weekly_crypto_fetcher(request):
    """Main entry point for Cloud Function"""
    execution_id = str(uuid.uuid4())
    start_time = datetime.now(timezone.utc)
    client = bigquery.Client(project=PROJECT_ID)

    was_manual = request.args.get('manual', 'false').lower() == 'true'

    # Log start
    log_execution(client, execution_id, 'weekly-crypto-fetcher', 'weekly_crypto_fetcher',
                  'cryptos_weekly_summary', start_time, was_manual=was_manual)

    try:
        # Get all cryptos
        print("Fetching crypto list...")
        cryptos, err = get_all_cryptos()

        if not cryptos:
            end_time = datetime.now(timezone.utc)
            log_execution(client, execution_id, 'weekly-crypto-fetcher', 'weekly_crypto_fetcher',
                          'cryptos_weekly_summary', start_time, end_time, 'FAILED',
                          f"Failed to get crypto list: {err}", was_manual=was_manual)
            return f"Error: {err}", 500

        total_cryptos = len(cryptos)
        print(f"Found {total_cryptos} crypto pairs")

        successful = 0
        failed = 0
        records_inserted = 0
        batch = []
        batch_size = 50
        api_calls = 1

        for i, crypto in enumerate(cryptos):
            try:
                record, err = process_crypto(crypto, client)
                api_calls += 2  # quote + weekly

                if record:
                    batch.append(record)
                    successful += 1
                else:
                    failed += 1
                    print(f"Failed {crypto['pair']}: {err}")

                if len(batch) >= batch_size:
                    inserted = upload_batch(batch, client)
                    records_inserted += inserted
                    print(f"Progress: {i+1}/{total_cryptos} - Batch uploaded: {inserted}")
                    batch = []

                time.sleep(0.5)

                if (i + 1) % 100 == 0:
                    print(f"Processed {i+1}/{total_cryptos} cryptos")

            except Exception as e:
                failed += 1
                print(f"Error processing {crypto.get('pair', 'unknown')}: {e}")

        # Upload remaining
        if batch:
            inserted = upload_batch(batch, client)
            records_inserted += inserted

        # Log completion
        end_time = datetime.now(timezone.utc)
        status = 'SUCCESS' if failed == 0 else 'PARTIAL' if successful > 0 else 'FAILED'

        log_execution(client, execution_id, 'weekly-crypto-fetcher', 'weekly_crypto_fetcher',
                      'cryptos_weekly_summary', start_time, end_time, status,
                      total_symbols=total_cryptos, successful=successful, failed=failed,
                      records_inserted=records_inserted, api_calls=api_calls, was_manual=was_manual)

        duration = (end_time - start_time).total_seconds() / 60
        return f"Completed: {successful}/{total_cryptos} cryptos, {records_inserted} records in {duration:.1f} min", 200

    except Exception as e:
        end_time = datetime.now(timezone.utc)
        log_execution(client, execution_id, 'weekly-crypto-fetcher', 'weekly_crypto_fetcher',
                      'cryptos_weekly_summary', start_time, end_time, 'FAILED',
                      str(e), was_manual=was_manual)
        return f"Error: {str(e)}", 500


if __name__ == "__main__":
    class MockRequest:
        args = {'manual': 'true'}

    result, code = weekly_crypto_fetcher(MockRequest())
    print(f"Result: {result} (code: {code})")
