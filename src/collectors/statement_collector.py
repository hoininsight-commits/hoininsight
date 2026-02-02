import json
from pathlib import Path
from typing import List, Dict, Any

class StatementCollector:
    """
    [IS-93] Data Supply for Statement/Document Layer
    Loads narrative materials from data/raw/statements/
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.data_dir = base_dir / "data" / "raw" / "statements"
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def collect(self) -> List[Dict[str, Any]]:
        # In a real scenario, this would scrape X, News, IR pages.
        # For now, we load from JSON files or provide default high-quality mocks.
        results = []
        
        # 1. Load from files if they exist
        for f in self.data_dir.glob("*.json"):
            try:
                results.extend(json.loads(f.read_text(encoding="utf-8")))
            except:
                pass
                
        # 2. If no data, provide MOCKs as requested in IS-93 specs
        if not results:
            results = self._get_default_mocks()
            
        return results

    def _get_default_mocks(self) -> List[Dict[str, Any]]:
        return [
            {
                "entity": "Elon Musk",
                "organization": "xAI / Tesla",
                "source_type": "Person (Social)",
                "content": "We decided to prioritize the massive GPU cluster immediately. This year, we will build the most significant AI infrastructure from 2026. This is a supply constraint challenge, but our platform is unbeatable.",
                "linked_assets": ["LS ELECTRIC", "HD HYUNDAI ELECTRIC"]
            },
            {
                "entity": "Jensen Huang",
                "organization": "NVIDIA",
                "source_type": "Person (Interview)",
                "content": "The demand for Blackwell is record-breaking. We are focused on increasing capacity to resolve the bottleneck in the global supply chain. This trillion-dollar cycle is now just beginning.",
                "linked_assets": ["SK HYNIX", "HANMI SEMI"]
            },
            {
                "entity": "SEC / Government",
                "organization": "U.S. Government",
                "source_type": "Document (Policy)",
                "content": "The new regulatory framework for AI safety will be applied immediately. Significant market share players must disclose infrastructure investments to avoid monopoly charges.",
                "linked_assets": ["NAVER", "KAKAO"]
            }
        ]
