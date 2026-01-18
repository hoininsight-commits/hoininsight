import requests
import json

ids = ["bitcoin", "ethereum", "pax-gold", "kinesis-silver"]
url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(ids)}&vs_currencies=usd"

try:
    print(f"Fetching from: {url}")
    r = requests.get(url, timeout=10)
    print(f"Status: {r.status_code}")
    data = r.json()
    print(json.dumps(data, indent=2))
except Exception as e:
    print(f"Error: {e}")
