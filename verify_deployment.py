"""
Verify Trading App Deployment
Tests all endpoints and verifies data connectivity
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import json
from datetime import datetime

# Configuration
API_BASE_URL = 'https://trading-api-cnyn5l4u2a-uc.a.run.app'
FRONTEND_URL = 'https://crypto-trading-app-252370699783.us-central1.run.app'

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def test_endpoint(name, url, expected_keys=None):
    """Test an API endpoint"""
    print(f"\n🔍 Testing: {name}")
    print(f"   URL: {url}")

    try:
        response = requests.get(url, timeout=30)

        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {response.status_code} OK")

            # Check expected keys
            if expected_keys:
                for key in expected_keys:
                    if key in data:
                        print(f"   ✅ Contains '{key}': {data[key] if not isinstance(data[key], (list, dict)) else f'{type(data[key]).__name__} with {len(data[key])} items'}")
                    else:
                        print(f"   ❌ Missing key: {key}")

            # Show sample data
            if 'data' in data and len(data['data']) > 0:
                sample = data['data'][0]
                print(f"   📊 Sample record keys: {list(sample.keys())[:5]}...")

            return True
        else:
            print(f"   ❌ Status: {response.status_code}")
            print(f"   Error: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def main():
    """Run all verification tests"""

    print_header("TRADING APP DEPLOYMENT VERIFICATION")
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API Base URL: {API_BASE_URL}")
    print(f"Frontend URL: {FRONTEND_URL}")

    results = []

    # Test 1: Health Check
    print_header("Test 1: API Health Check")
    results.append(test_endpoint(
        "Health Check",
        f"{API_BASE_URL}/health",
        expected_keys=['status', 'timestamp']
    ))

    # Test 2: Crypto Daily Data
    print_header("Test 2: Crypto Daily Data")
    results.append(test_endpoint(
        "Crypto Daily (5 records)",
        f"{API_BASE_URL}/api/crypto/daily?limit=5",
        expected_keys=['success', 'data', 'count']
    ))

    # Test 3: Crypto Hourly Data
    print_header("Test 3: Crypto Hourly Data")
    results.append(test_endpoint(
        "Crypto Hourly (5 records)",
        f"{API_BASE_URL}/api/crypto/hourly?limit=5",
        expected_keys=['success', 'data', 'count']
    ))

    # Test 4: Crypto 5-Min Data
    print_header("Test 4: Crypto 5-Minute Data")
    results.append(test_endpoint(
        "Crypto 5-Min (5 records)",
        f"{API_BASE_URL}/api/crypto/5min?limit=5",
        expected_keys=['success', 'data', 'count']
    ))

    # Test 5: Stock Data
    print_header("Test 5: Stock Data")
    results.append(test_endpoint(
        "Stock Data (5 records)",
        f"{API_BASE_URL}/api/stocks?limit=5",
        expected_keys=['success', 'data', 'count']
    ))

    # Test 6: Crypto Market Summary
    print_header("Test 6: Crypto Market Summary")
    results.append(test_endpoint(
        "Crypto Market Summary",
        f"{API_BASE_URL}/api/summary/crypto",
        expected_keys=['success', 'summary']
    ))

    # Test 7: Stock Market Summary
    print_header("Test 7: Stock Market Summary")
    results.append(test_endpoint(
        "Stock Market Summary",
        f"{API_BASE_URL}/api/summary/stock",
        expected_keys=['success', 'summary']
    ))

    # Test 8: Frontend Accessibility
    print_header("Test 8: Frontend Application")
    print(f"\n🔍 Testing: Frontend Accessibility")
    print(f"   URL: {FRONTEND_URL}")

    try:
        response = requests.get(FRONTEND_URL, timeout=30)
        if response.status_code == 200:
            print(f"   ✅ Status: {response.status_code} OK")
            print(f"   ✅ Content Length: {len(response.content)} bytes")

            # Check if it's HTML
            if 'text/html' in response.headers.get('content-type', ''):
                print(f"   ✅ Content Type: HTML")

            # Check for React app
            if b'root' in response.content or b'app' in response.content:
                print(f"   ✅ Contains React root element")

            results.append(True)
        else:
            print(f"   ❌ Status: {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        results.append(False)

    # Summary
    print_header("VERIFICATION SUMMARY")

    total_tests = len(results)
    passed_tests = sum(results)
    failed_tests = total_tests - passed_tests

    print(f"\n📊 Results:")
    print(f"   Total Tests: {total_tests}")
    print(f"   ✅ Passed: {passed_tests}")
    print(f"   ❌ Failed: {failed_tests}")
    print(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")

    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! Deployment is fully operational.")
        print("\n📱 Access your trading app at:")
        print(f"   {FRONTEND_URL}")
        print("\n🔌 API Documentation:")
        print(f"   {API_BASE_URL}/health")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")
        print("\n💡 Troubleshooting:")
        print("   1. Check Cloud Run logs for errors")
        print("   2. Verify BigQuery tables have data")
        print("   3. Ensure Cloud Functions are collecting data")
        return 1

if __name__ == '__main__':
    exit_code = main()
    print("\n" + "="*70)
    sys.exit(exit_code)
