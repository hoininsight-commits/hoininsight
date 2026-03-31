from pathlib import Path
import json

class HoinAdapter:
    """
    (IS-4) Read-only bridge to HoinEngine data.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def get_structural_evidence(self, keyword: str) -> dict:
        """
        Pull evidence from HoinEngine's deep analysis results.
        """
        analysis_path = self.base_dir / "data" / "analysis" / "deep_logic_results.json"
        if not analysis_path.exists():
            return {}
            
        try:
            with open(analysis_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Simple keyword search in analysis results
                for item in data:
                    if keyword.lower() in str(item).lower():
                        return item
        except:
            pass
        return {}
