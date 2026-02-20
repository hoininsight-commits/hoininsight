from __future__ import annotations
from datetime import datetime

def collect() -> list[dict]:
    """S3: Flows"""
    # Placeholder for actual crawling/API logic
    return [
        {
            "source": "ETF.com",
            "title": "Massive Inflow into Tech ETFs",
            "url": "https://www.etf.com/news/tech-inflows",
            "published_at": datetime.now().strftime("%Y-%m-%d"),
            "raw_text": "Tech ETFs saw an inflow of $1.2B this week, reversing previous trends.",
            "numbers": [
                { "value": 1.2, "unit": "B", "context": "Weekly Inflow" }
            ]
        }
    ]
