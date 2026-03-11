from __future__ import annotations
from datetime import datetime

def collect() -> list[dict]:
    """S1: Earnings/IR releases"""
    # Placeholder for actual crawling/API logic
    events = [
        {
            "source": "Yahoo Finance",
            "title": "NVIDIA (NVDA) Earnings Beat Expectations",
            "url": "https://finance.yahoo.com/news/nvda-earnings",
            "published_at": datetime.now().strftime("%Y-%m-%d"),
            "raw_text": "NVIDIA reported revenue of $26B, up 262% YoY. EPS was $6.12 vs $5.59 expected.",
            "numbers": [
                { "value": 26.0, "unit": "B", "context": "Revenue" },
                { "value": 6.12, "unit": "USD", "context": "EPS Actual" },
                { "value": 5.59, "unit": "USD", "context": "EPS Expected" }
            ]
        }
    ]
    return events
