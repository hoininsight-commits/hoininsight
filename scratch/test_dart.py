import os
import OpenDartReader
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

def test_dart():
    api_key = os.getenv('OPENDART_API_KEY')
    if not api_key:
        print("OPENDART_API_KEY not found")
        return
    
    print(f"Testing DART API with key: {api_key[:5]}...")
    try:
        dart = OpenDartReader(api_key)
        today = datetime.now()
        bgn_de = (today - timedelta(days=1)).strftime("%Y%m%d")
        df = dart.list(start=bgn_de)
        if df is not None and not df.empty:
            print(f"Success! Found {len(df)} disclosures since {bgn_de}")
            print(df.head())
        else:
            print(f"Success (empty results). No disclosures found since {bgn_de}")
    except Exception as e:
        print(f"DART API failed: {e}")

if __name__ == "__main__":
    test_dart()
