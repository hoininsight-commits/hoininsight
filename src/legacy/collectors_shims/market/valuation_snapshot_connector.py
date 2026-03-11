from typing import List, Dict, Any
import json
from pathlib import Path

class ValuationSnapshotConnector:
    """
    (IS-90) Valuation Snapshot Connector.
    Collects P/E, P/B bands and historical averages.
    Strictly reads from 'data/raw/market/valuation_snapshot.json'.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def fetch_valuation(self, ticker: str) -> Dict[str, Any]:
        """
        Fetch valuation metrics.
        """
        raw_path = self.base_dir / "data" / "raw" / "market" / "valuation_snapshot.json"
        
        if not raw_path.exists():
            return {}
            
        try:
            data = json.loads(raw_path.read_text(encoding="utf-8"))
            return data.get(ticker, {})
        except Exception as e:
            print(f"Error loading valuation snapshot: {e}")
            return {}
