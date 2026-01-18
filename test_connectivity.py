import requests
import yfinance as yf

print(f"yfinance version: {yf.__version__}")

url = "https://query2.finance.yahoo.com/v8/finance/chart/AAPL?range=1d&interval=1d"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print(f"Testing direct connection to: {url}")
try:
    r = requests.get(url, headers=headers, timeout=10)
    print(f"Status Code: {r.status_code}")
    print(f"Content Start: {r.text[:200]}")
except Exception as e:
    print(f"Direct connection failed: {e}")

print("\nTesting yfinance with default session:")
try:
    dat = yf.download("AAPL", period="1d")
    print(dat)
except Exception as e:
    print(f"yfinance download failed: {e}")
