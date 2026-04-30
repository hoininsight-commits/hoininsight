
import os
import OpenDartReader
from dotenv import load_dotenv

load_dotenv()

def test_dart():
    api_key = os.getenv('OPENDART_API_KEY')
    print(f"Testing DART with key: {api_key[:5]}...")
    try:
        dart = OpenDartReader(api_key)
        df = dart.list(start='20260428')
        if df is not None and not df.empty:
            print(f"✅ DART Success: Found {len(df)} records")
            print(df.head(3))
        else:
            print("❌ DART Empty response")
    except Exception as e:
        print(f"❌ DART Failure: {e}")

if __name__ == "__main__":
    test_dart()
