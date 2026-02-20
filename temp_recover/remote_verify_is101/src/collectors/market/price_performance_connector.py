from typing import List, Dict, Any
import json
from pathlib import Path

class PricePerformanceConnector:
    """
    (IS-90) Price Performance Connector.
    Collects relative performance vs peers (e.g. NVDA vs SOXX vs SPX).
    Strictly reads from 'data/raw/market/price_snapshot.json'.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def fetch_relative_perf(self, ticker: str, peer_group: str) -> Dict[str, Any]:
        """
        Fetch relative performance gap.
        """
        raw_path = self.base_dir / "data" / "raw" / "market" / "price_snapshot.json"
        
        if not raw_path.exists():
            return {}
            
        try:
            data = json.loads(raw_path.read_text(encoding="utf-8"))
            return data.get(f"{ticker}_VS_{peer_group}", {})
        except Exception as e:
            print(f"Error loading price snapshot: {e}")
            return {}
