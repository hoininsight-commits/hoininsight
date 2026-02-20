from __future__ import annotations
from datetime import datetime

def collect() -> list[dict]:
    """S4: Contracts"""
    # Placeholder for actual crawling/API logic
    return [
        {
            "source": "DART",
            "title": "[공시] 삼성전자, 5000억 규모 공급 계약 체결",
            "url": "https://dart.fss.or.kr/dsaf001/main.do",
            "published_at": datetime.now().strftime("%Y-%m-%d"),
            "raw_text": "삼성전자가 고객사와 5,000억원 규모의 통신 장비 공급 계약을 체결했습니다. 기간은 24개월입니다.",
            "numbers": [
                { "value": 5000.0, "unit": "KRW_100M", "context": "Contract Amount" },
                { "value": 24.0, "unit": "months", "context": "Duration" }
            ]
        }
    ]
