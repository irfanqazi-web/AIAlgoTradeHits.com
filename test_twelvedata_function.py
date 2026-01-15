"""
Test TwelveData Fetcher Cloud Function
"""
import subprocess
import requests
import json
import sys
import os

# Get identity token - use shell=True on Windows
result = subprocess.run('gcloud auth print-identity-token', capture_output=True, text=True, shell=True)
token = result.stdout.strip()

if not token:
    print("Failed to get identity token")
    print(f"Error: {result.stderr}")
    sys.exit(1)

print(f"Got token: {token[:20]}...")

# Test the function
url = "https://us-central1-aialgotradehits.cloudfunctions.net/twelvedata-fetcher"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Test with stocks daily - limited to 3 symbols in test mode
params = {
    "asset_type": "stocks",
    "timeframe": "daily",
    "limit": "3",
    "test": "true"
}

print(f"\nTesting: {url}")
print(f"Params: {params}")
print()

try:
    response = requests.get(url, params=params, headers=headers, timeout=300)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)[:2000]}")
except Exception as e:
    print(f"Error: {e}")
