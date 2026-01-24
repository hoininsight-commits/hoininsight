import pandas as pd
import requests
from io import StringIO
from datetime import datetime

url = "https://stooq.com/q/d/l/?s=^kospi&i=d"
print(f"Testing URL: {url}")

try:
    # 1. Try requests with headers (simulating browser)
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    print(f"Status Code: {r.status_code}")
    print(f"Content Start: {r.text[:100]}")
    
    if r.status_code == 200:
        df = pd.read_csv(StringIO(r.text))
        print("Pandas read success!")
        print(df.tail())
    else:
        print("Request failed.")

    # 2. Try raw pandas read (what the collector does)
    print("\nTesting raw pd.read_csv...")
    try:
        df2 = pd.read_csv(url)
        print("Raw pd.read_csv success!")
    except Exception as e:
        print(f"Raw pd.read_csv failed: {e}")

except Exception as e:
    print(f"Debug script error: {e}")
