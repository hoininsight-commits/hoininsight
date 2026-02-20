from __future__ import annotations
from datetime import datetime

def collect() -> list[dict]:
    """S2: Policy/Regulation"""
    # Placeholder for actual crawling/API logic
    return [
        {
            "source": "Federal Reserve",
            "title": "FOMC Maintains Interest Rates",
            "url": "https://www.federalreserve.gov/newsevents/pressreleases",
            "published_at": datetime.now().strftime("%Y-%m-%d"),
            "raw_text": "The Committee decided to maintain the target range for the federal funds rate at 5.25 to 5.5 percent.",
            "numbers": [
                { "value": 5.25, "unit": "%", "context": "Lower bound" },
                { "value": 5.5, "unit": "%", "context": "Upper bound" }
            ]
        }
    ]
