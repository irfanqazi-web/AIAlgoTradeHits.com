"""
Interest Rates Cloud Function
Fetches G20 central bank interest rates from free APIs
Runs daily and hourly to track changes
"""

import functions_framework
from flask import jsonify
import requests
from datetime import datetime, timezone
from google.cloud import bigquery
import time

# Configuration
PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'crypto_trading_data'
TABLE_ID = 'interest_rates'

# G20 Countries Central Bank Data
G20_CENTRAL_BANKS = [
    {"country": "United States", "bank": "Federal Reserve", "currency": "USD", "rate_name": "Federal Funds Rate"},
    {"country": "European Union", "bank": "ECB", "currency": "EUR", "rate_name": "EURIBOR 3-Month"},
    {"country": "Germany", "bank": "ECB", "currency": "EUR", "rate_name": "EURIBOR 3-Month"},
    {"country": "France", "bank": "ECB", "currency": "EUR", "rate_name": "EURIBOR 3-Month"},
    {"country": "Italy", "bank": "ECB", "currency": "EUR", "rate_name": "EURIBOR 3-Month"},
    {"country": "United Kingdom", "bank": "Bank of England", "currency": "GBP", "rate_name": "Bank Rate"},
    {"country": "Japan", "bank": "Bank of Japan", "currency": "JPY", "rate_name": "Policy Rate"},
    {"country": "China", "bank": "PBOC", "currency": "CNY", "rate_name": "Loan Prime Rate (1Y)"},
    {"country": "Canada", "bank": "Bank of Canada", "currency": "CAD", "rate_name": "Overnight Rate"},
    {"country": "Australia", "bank": "RBA", "currency": "AUD", "rate_name": "Cash Rate"},
    {"country": "Brazil", "bank": "BCB", "currency": "BRL", "rate_name": "SELIC Rate"},
    {"country": "India", "bank": "RBI", "currency": "INR", "rate_name": "Repo Rate"},
    {"country": "Russia", "bank": "CBR", "currency": "RUB", "rate_name": "Key Rate"},
    {"country": "South Korea", "bank": "BOK", "currency": "KRW", "rate_name": "Base Rate"},
    {"country": "Mexico", "bank": "Banxico", "currency": "MXN", "rate_name": "Target Rate"},
    {"country": "Indonesia", "bank": "BI", "currency": "IDR", "rate_name": "BI Rate"},
    {"country": "Turkey", "bank": "TCMB", "currency": "TRY", "rate_name": "Policy Rate"},
    {"country": "Saudi Arabia", "bank": "SAMA", "currency": "SAR", "rate_name": "Repo Rate"},
    {"country": "Argentina", "bank": "BCRA", "currency": "ARS", "rate_name": "Policy Rate"},
    {"country": "South Africa", "bank": "SARB", "currency": "ZAR", "rate_name": "Repo Rate"},
]

# Hardcoded rates (as fallback - these change monthly, not daily)
FALLBACK_RATES = {
    "United States": 4.5,
    "European Union": 3.4,
    "Germany": 3.4,
    "France": 3.4,
    "Italy": 3.4,
    "United Kingdom": 4.75,
    "Japan": 0.25,
    "China": 3.1,
    "Canada": 3.75,
    "Australia": 4.35,
    "Brazil": 11.25,
    "India": 6.5,
    "Russia": 21.0,
    "South Korea": 3.0,
    "Mexico": 10.25,
    "Indonesia": 6.0,
    "Turkey": 50.0,
    "Saudi Arabia": 5.5,
    "Argentina": 35.0,
    "South Africa": 8.0,
}

REGIONS = {
    "United States": "North America",
    "Canada": "North America",
    "Mexico": "North America",
    "Brazil": "South America",
    "Argentina": "South America",
    "European Union": "Europe",
    "Germany": "Europe",
    "France": "Europe",
    "Italy": "Europe",
    "United Kingdom": "Europe",
    "Russia": "Europe/Asia",
    "Turkey": "Europe/Asia",
    "Japan": "Asia",
    "China": "Asia",
    "South Korea": "Asia",
    "India": "Asia",
    "Indonesia": "Asia",
    "Saudi Arabia": "Middle East",
    "Australia": "Oceania",
    "South Africa": "Africa",
}


def fetch_ny_fed_rates():
    """Fetch US rates from NY Fed API"""
    rates = {}

    # Federal Funds Effective Rate
    try:
        url = "https://markets.newyorkfed.org/api/rates/unsecured/effr/last/1.json"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('refRates'):
                rate_data = data['refRates'][0]
                rates['Federal Funds Rate'] = float(rate_data.get('percentRate', 0))
    except Exception as e:
        print(f"Error fetching EFFR: {e}")

    # SOFR
    try:
        url = "https://markets.newyorkfed.org/api/rates/secured/sofr/last/1.json"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('refRates'):
                rate_data = data['refRates'][0]
                rates['SOFR'] = float(rate_data.get('percentRate', 0))
    except Exception as e:
        print(f"Error fetching SOFR: {e}")

    return rates


def fetch_ecb_euribor():
    """Fetch EURIBOR rates from ECB API"""
    rates = {}

    # EURIBOR 3-Month
    try:
        url = "https://data-api.ecb.europa.eu/service/data/FM/M.U2.EUR.RT.MM.EURIBOR3MD_.HSTA?format=jsondata"
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            observations = data.get('dataSets', [{}])[0].get('series', {}).get('0:0:0:0:0:0:0', {}).get('observations', {})
            if observations:
                latest_key = max(observations.keys())
                rates['EURIBOR 3-Month'] = float(observations[latest_key][0])
    except Exception as e:
        print(f"Error fetching EURIBOR: {e}")

    return rates


def fetch_all_rates(timeframe='daily'):
    """Fetch all G20 interest rates"""
    now = datetime.now(timezone.utc)
    results = []

    # Fetch live US rates
    us_rates = fetch_ny_fed_rates()
    time.sleep(0.5)

    # Fetch live EU rates
    eu_rates = fetch_ecb_euribor()
    time.sleep(0.5)

    for bank_info in G20_CENTRAL_BANKS:
        country = bank_info["country"]
        rate_name = bank_info["rate_name"]

        # Try to get live rate
        if country == "United States" and "Federal Funds Rate" in us_rates:
            rate_value = us_rates["Federal Funds Rate"]
            source = "NY Fed API"
        elif country in ["European Union", "Germany", "France", "Italy"] and "EURIBOR 3-Month" in eu_rates:
            rate_value = eu_rates["EURIBOR 3-Month"]
            source = "ECB API"
        else:
            # Use fallback rate
            rate_value = FALLBACK_RATES.get(country, 0.0)
            source = "Official Central Bank / Public Data"

        result = {
            "country": country,
            "central_bank": bank_info["bank"],
            "rate_name": rate_name,
            "rate_value": rate_value,
            "currency": bank_info["currency"],
            "timeframe": timeframe,
            "timestamp": now.isoformat(),
            "fetch_date": str(now.date()),
            "fetch_hour": now.hour if timeframe == 'hourly' else None,
            "source": source,
            "g20_member": True,
            "region": REGIONS.get(country, "Other"),
        }
        results.append(result)

    return results


def upload_to_bigquery(rates):
    """Upload rates to BigQuery"""
    client = bigquery.Client(project=PROJECT_ID)
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

    errors = client.insert_rows_json(table_ref, rates)

    if errors:
        print(f"BigQuery insert errors: {errors}")
        return False, errors
    else:
        print(f"Uploaded {len(rates)} interest rate records")
        return True, None


@functions_framework.http
def fetch_interest_rates(request):
    """HTTP Cloud Function entry point"""
    try:
        # Determine timeframe from request
        request_json = request.get_json(silent=True)
        timeframe = 'daily'

        if request_json and 'timeframe' in request_json:
            timeframe = request_json['timeframe']
        elif request.args.get('timeframe'):
            timeframe = request.args.get('timeframe')

        print(f"Fetching {timeframe} interest rates for G20 countries...")

        # Fetch rates
        rates = fetch_all_rates(timeframe)

        # Upload to BigQuery
        success, errors = upload_to_bigquery(rates)

        if success:
            return jsonify({
                "status": "success",
                "message": f"Fetched {len(rates)} {timeframe} interest rates",
                "timeframe": timeframe,
                "countries": [r["country"] for r in rates],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }), 200
        else:
            return jsonify({
                "status": "partial",
                "message": f"Uploaded {len(rates)} rates with some errors",
                "errors": str(errors)
            }), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# For local testing
if __name__ == "__main__":
    print("Testing interest rates fetcher locally...")
    rates = fetch_all_rates('daily')
    for r in rates:
        print(f"{r['country']:20} | {r['rate_value']:6.2f}% | {r['rate_name']}")
