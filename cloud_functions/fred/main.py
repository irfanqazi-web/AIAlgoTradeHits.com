#!/usr/bin/env python3
"""
FRED Economic Data Fetcher
Fetches US economic indicators from Federal Reserve Economic Data
"""

import functions_framework
from flask import jsonify, request
import requests
import pandas as pd
from datetime import datetime, timedelta
from google.cloud import bigquery
import traceback

# FRED API Configuration
FRED_API_KEY = "608f96800c8a5d9bdb8d53ad059f06c1"
FRED_BASE_URL = "https://api.stlouisfed.org/fred"

# BigQuery Configuration
PROJECT_ID = "aialgotradehits"
DATASET_ID = "crypto_trading_data"

# Key Economic Series to Fetch
ECONOMIC_SERIES = {
    # Treasury Yields (Daily)
    'DGS1MO': {'name': '1-Month Treasury Yield', 'category': 'treasury', 'frequency': 'daily'},
    'DGS3MO': {'name': '3-Month Treasury Yield', 'category': 'treasury', 'frequency': 'daily'},
    'DGS6MO': {'name': '6-Month Treasury Yield', 'category': 'treasury', 'frequency': 'daily'},
    'DGS1': {'name': '1-Year Treasury Yield', 'category': 'treasury', 'frequency': 'daily'},
    'DGS2': {'name': '2-Year Treasury Yield', 'category': 'treasury', 'frequency': 'daily'},
    'DGS5': {'name': '5-Year Treasury Yield', 'category': 'treasury', 'frequency': 'daily'},
    'DGS7': {'name': '7-Year Treasury Yield', 'category': 'treasury', 'frequency': 'daily'},
    'DGS10': {'name': '10-Year Treasury Yield', 'category': 'treasury', 'frequency': 'daily'},
    'DGS20': {'name': '20-Year Treasury Yield', 'category': 'treasury', 'frequency': 'daily'},
    'DGS30': {'name': '30-Year Treasury Yield', 'category': 'treasury', 'frequency': 'daily'},

    # Treasury Spreads
    'T10Y2Y': {'name': '10Y-2Y Treasury Spread', 'category': 'spread', 'frequency': 'daily'},
    'T10Y3M': {'name': '10Y-3M Treasury Spread', 'category': 'spread', 'frequency': 'daily'},
    'T10YFF': {'name': '10Y-Fed Funds Spread', 'category': 'spread', 'frequency': 'daily'},

    # Interest Rates
    'FEDFUNDS': {'name': 'Federal Funds Rate', 'category': 'rates', 'frequency': 'monthly'},
    'DPRIME': {'name': 'Prime Rate', 'category': 'rates', 'frequency': 'daily'},
    'MORTGAGE30US': {'name': '30-Year Mortgage Rate', 'category': 'rates', 'frequency': 'weekly'},
    'MORTGAGE15US': {'name': '15-Year Mortgage Rate', 'category': 'rates', 'frequency': 'weekly'},

    # Market Indices
    'SP500': {'name': 'S&P 500 Index', 'category': 'market', 'frequency': 'daily'},
    'DJIA': {'name': 'Dow Jones Industrial', 'category': 'market', 'frequency': 'daily'},
    'NASDAQCOM': {'name': 'NASDAQ Composite', 'category': 'market', 'frequency': 'daily'},
    'VIXCLS': {'name': 'VIX Volatility Index', 'category': 'market', 'frequency': 'daily'},
    'WILL5000IND': {'name': 'Wilshire 5000', 'category': 'market', 'frequency': 'daily'},

    # Economic Indicators
    'UNRATE': {'name': 'Unemployment Rate', 'category': 'economic', 'frequency': 'monthly'},
    'CPIAUCSL': {'name': 'Consumer Price Index', 'category': 'economic', 'frequency': 'monthly'},
    'CPILFESL': {'name': 'Core CPI', 'category': 'economic', 'frequency': 'monthly'},
    'PCEPI': {'name': 'PCE Price Index', 'category': 'economic', 'frequency': 'monthly'},
    'GDP': {'name': 'Gross Domestic Product', 'category': 'economic', 'frequency': 'quarterly'},
    'GDPC1': {'name': 'Real GDP', 'category': 'economic', 'frequency': 'quarterly'},
    'PAYEMS': {'name': 'Nonfarm Payrolls', 'category': 'economic', 'frequency': 'monthly'},
    'INDPRO': {'name': 'Industrial Production', 'category': 'economic', 'frequency': 'monthly'},
    'RSAFS': {'name': 'Retail Sales', 'category': 'economic', 'frequency': 'monthly'},
    'HOUST': {'name': 'Housing Starts', 'category': 'economic', 'frequency': 'monthly'},

    # Money Supply & Fed Balance Sheet
    'M1SL': {'name': 'M1 Money Supply', 'category': 'monetary', 'frequency': 'monthly'},
    'M2SL': {'name': 'M2 Money Supply', 'category': 'monetary', 'frequency': 'monthly'},
    'WALCL': {'name': 'Fed Total Assets', 'category': 'monetary', 'frequency': 'weekly'},

    # Exchange Rates
    'DEXUSEU': {'name': 'USD/EUR Rate', 'category': 'forex', 'frequency': 'daily'},
    'DEXJPUS': {'name': 'JPY/USD Rate', 'category': 'forex', 'frequency': 'daily'},
    'DEXUSUK': {'name': 'USD/GBP Rate', 'category': 'forex', 'frequency': 'daily'},
    'DEXCHUS': {'name': 'CNY/USD Rate', 'category': 'forex', 'frequency': 'daily'},
    'DTWEXBGS': {'name': 'Trade Weighted USD Index', 'category': 'forex', 'frequency': 'daily'},

    # Commodities
    'GOLDAMGBD228NLBM': {'name': 'Gold Price (London)', 'category': 'commodity', 'frequency': 'daily'},
    'DCOILWTICO': {'name': 'WTI Crude Oil', 'category': 'commodity', 'frequency': 'daily'},
    'DCOILBRENTEU': {'name': 'Brent Crude Oil', 'category': 'commodity', 'frequency': 'daily'},
    'GASREGW': {'name': 'Regular Gas Price', 'category': 'commodity', 'frequency': 'weekly'},
}


def fetch_fred_series(series_id, start_date=None, limit=5000):
    """Fetch a single FRED series"""
    try:
        params = {
            'series_id': series_id,
            'api_key': FRED_API_KEY,
            'file_type': 'json',
            'limit': limit,
            'sort_order': 'desc'
        }

        if start_date:
            params['observation_start'] = start_date

        response = requests.get(f"{FRED_BASE_URL}/series/observations", params=params, timeout=30)
        data = response.json()

        if 'observations' in data:
            observations = data['observations']
            if observations:
                df = pd.DataFrame(observations)
                df['series_id'] = series_id
                df['value'] = pd.to_numeric(df['value'], errors='coerce')
                df['date'] = pd.to_datetime(df['date'])
                df = df[df['value'].notna()]  # Remove missing values
                return df[['date', 'series_id', 'value']], None

        return None, data.get('error_message', 'No data')

    except Exception as e:
        return None, str(e)


def upload_to_bigquery(client, df, table_id='fred_economic_data'):
    """Upload FRED data to BigQuery"""
    if df.empty:
        return 0

    try:
        table_ref = client.dataset(DATASET_ID).table(table_id)

        # Rename columns for BigQuery
        df_upload = df.rename(columns={'date': 'datetime'})

        # Add metadata
        df_upload['fetched_at'] = datetime.utcnow()

        job_config = bigquery.LoadJobConfig(write_disposition='WRITE_APPEND')
        job = client.load_table_from_dataframe(df_upload, table_ref, job_config=job_config)
        job.result()

        return len(df_upload)

    except Exception as e:
        print(f"Upload error: {e}")
        return 0


def create_fred_table_if_not_exists(client):
    """Create FRED table if it doesn't exist"""
    table_id = f"{PROJECT_ID}.{DATASET_ID}.fred_economic_data"

    schema = [
        bigquery.SchemaField("datetime", "TIMESTAMP"),
        bigquery.SchemaField("series_id", "STRING"),
        bigquery.SchemaField("value", "FLOAT64"),
        bigquery.SchemaField("fetched_at", "TIMESTAMP"),
    ]

    table = bigquery.Table(table_id, schema=schema)
    table.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.MONTH,
        field="datetime"
    )

    try:
        client.create_table(table)
        print(f"Created table {table_id}")
    except Exception as e:
        if "Already Exists" not in str(e):
            print(f"Table creation note: {e}")


@functions_framework.http
def main(request):
    """Main entry point for FRED data fetching"""
    try:
        request_json = request.get_json(silent=True) or {}
        category = request_json.get('category', 'all')
        backfill = request_json.get('backfill', False)

        print(f"FRED Fetch: category={category}, backfill={backfill}")

        client = bigquery.Client(project=PROJECT_ID)

        # Create table if needed
        create_fred_table_if_not_exists(client)

        # Filter series by category
        if category == 'all':
            series_to_fetch = ECONOMIC_SERIES
        else:
            series_to_fetch = {k: v for k, v in ECONOMIC_SERIES.items() if v['category'] == category}

        # Determine date range
        if backfill:
            start_date = '1990-01-01'
            limit = 10000
        else:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            limit = 100

        results = {'success': 0, 'failed': 0, 'records': 0, 'series': []}

        for series_id, info in series_to_fetch.items():
            df, error = fetch_fred_series(series_id, start_date, limit)

            if error:
                results['failed'] += 1
                print(f"  {series_id}: FAILED - {error}")
            elif df is not None and not df.empty:
                records = upload_to_bigquery(client, df)
                results['records'] += records
                results['success'] += 1
                results['series'].append({
                    'series_id': series_id,
                    'name': info['name'],
                    'records': records
                })
                print(f"  {series_id}: {records} records ({info['name']})")
            else:
                results['failed'] += 1

        response = {
            'status': 'success',
            'timestamp': datetime.utcnow().isoformat(),
            'category': category,
            'backfill': backfill,
            'summary': {
                'total_series': len(series_to_fetch),
                'success': results['success'],
                'failed': results['failed'],
                'total_records': results['records']
            },
            'series': results['series']
        }

        return jsonify(response), 200

    except Exception as e:
        error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


if __name__ == "__main__":
    # Local testing
    class FakeRequest:
        def get_json(self, silent=False):
            return {'category': 'treasury', 'backfill': False}

    result = main(FakeRequest())
    print(result)
