
import requests
from datetime import datetime

url = "https://cdn.cboe.com/api/global/us_indices/market_statistics/market_statistics_v2.json"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Referer": "https://www.cboe.com/",
    "Origin": "https://www.cboe.com",
    "Accept": "application/json, text/plain, */*"
}

print(f"Testing PutCall URL: {url}")
resp = requests.get(url, headers=headers, timeout=15)
print(f"Status Code: {resp.status_code}")
if resp.status_code == 200:
    print(f"Success! Data found.")
    data = resp.json()
    print(f"Latest: {data['ratios'][-1]}")
else:
    print(f"Failed with Status: {resp.status_code}")
    print(f"Response: {resp.text[:500]}")
