from typing import List, Dict, Any
import json
from pathlib import Path

class SECFinancialsConnector:
    """
    (IS-89) SEC Financials Connector.
    Collects numeric evidence (Revenue, Margin, Segment Growth) from official reports.
    Strictly reads from 'data/raw/financials/sec_snapshot.json' for MVP.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def fetch_snapshot(self, ticker: str) -> Dict[str, Any]:
        """
        Fetch segment Snapshot for a ticker.
        """
        raw_path = self.base_dir / "data" / "raw" / "financials" / "sec_snapshot.json"
        if not raw_path.exists():
            return {}
            
        try:
            data = json.loads(raw_path.read_text(encoding="utf-8"))
            return data.get(ticker, {})
        except Exception as e:
            print(f"Error loading SEC snapshot: {e}")
            return {}
