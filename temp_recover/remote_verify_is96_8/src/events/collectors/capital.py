from __future__ import annotations
from datetime import datetime

def collect() -> list[dict]:
    """S5: Capital Market (M&A, Buybacks)"""
    # Placeholder for actual crawling/API logic
    return [
        {
            "source": "Reuters",
            "title": "Apple Announces $110B Buyback Program",
            "url": "https://www.reuters.com/technology/apple-buyback",
            "published_at": datetime.now().strftime("%Y-%m-%d"),
            "raw_text": "Apple's board has authorized an additional $110 billion for share repurchases.",
            "numbers": [
                { "value": 110.0, "unit": "B", "context": "Buyback Authorized" }
            ]
        }
    ]
