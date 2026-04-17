import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


api_key = os.getenv('ECOS_API_KEY')
base_url = "https://ecos.bok.or.kr/api/StatisticSearch"

today = datetime.now()
ym = today.strftime("%Y%m")
ym_prev = f"{today.year - 1}{today.strftime('%m')}"

targets = [
    ("kr_m2",           "161Y005", "M", "BBHS00"),
    ("kr_unemployment", "901Y027", "M", "I61BC"),
    ("kr_export",       "901Y118", "M", "T002"),
    ("kr_import",       "901Y118", "M", "T004"),
]

for name, stat, cycle, item in targets:
    try:
        url = f"{base_url}/{api_key}/json/kr/1/1/{stat}/{cycle}/{ym_prev}/{ym}/{item}"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if "StatisticSearch" in data:
            rows = data["StatisticSearch"]["row"]
            val = rows[-1]["DATA_VALUE"]
            date = rows[-1]["TIME"]
            print(f"✅ {name}: {val} ({date})")
        elif "RESULT" in data:
            print(f"❌ {name}: {data['RESULT']['MESSAGE']}")
        else:
            print(f"❌ {name}: 알 수 없는 응답")
    except Exception as e:
        print(f"❌ {name}: {e}")
