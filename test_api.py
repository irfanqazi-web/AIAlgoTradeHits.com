"""
Test Trading API Endpoints
"""
import requests
import json

API_BASE = 'https://trading-api-cnyn5l4u2a-uc.a.run.app'

def test_health():
    """Test health endpoint"""
    print("\n=== Testing Health Endpoint ===")
    try:
        response = requests.get(f'{API_BASE}/health', timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_crypto_daily():
    """Test crypto daily data"""
    print("\n=== Testing Crypto Daily Data ===")
    try:
        response = requests.get(f'{API_BASE}/api/crypto/daily?limit=5', timeout=30)
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Success: {data.get('success')}")
        print(f"Record Count: {data.get('count')}")
        if data.get('data'):
            print(f"First Record: {data['data'][0].get('pair')} - ${data['data'][0].get('close')}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_stocks():
    """Test stock data"""
    print("\n=== Testing Stock Data ===")
    try:
        response = requests.get(f'{API_BASE}/api/stocks?limit=5', timeout=30)
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Success: {data.get('success')}")
        print(f"Record Count: {data.get('count')}")
        if data.get('data'):
            print(f"First Record: {data['data'][0].get('symbol')} - ${data['data'][0].get('close')}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_summary():
    """Test market summary"""
    print("\n=== Testing Market Summary ===")
    try:
        response = requests.get(f'{API_BASE}/api/summary/crypto', timeout=30)
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Success: {data.get('success')}")
        if data.get('summary'):
            summary = data['summary']
            print(f"Total Pairs: {summary.get('total_pairs')}")
            print(f"Oversold: {summary.get('oversold_count')}")
            print(f"Overbought: {summary.get('overbought_count')}")
            print(f"Bullish MACD: {summary.get('bullish_macd')}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_users():
    """Test user management"""
    print("\n=== Testing User Management ===")
    try:
        response = requests.get(f'{API_BASE}/api/users', timeout=30)
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Success: {data.get('success')}")
        print(f"User Count: {data.get('count')}")
        if data.get('users'):
            print(f"First User: {data['users'][0].get('email')} ({data['users'][0].get('role')})")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("TRADING API TEST SUITE")
    print("=" * 70)

    results = {
        'Health Check': test_health(),
        'Crypto Daily Data': test_crypto_daily(),
        'Stock Data': test_stocks(),
        'Market Summary': test_summary(),
        'User Management': test_users()
    }

    print("\n" + "=" * 70)
    print("TEST RESULTS SUMMARY")
    print("=" * 70)
    for test, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test}: {status}")

    total = len(results)
    passed = sum(results.values())
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 70)
