import yaml
from pathlib import Path
from datetime import datetime

class ContentPack:
    """
    (IS-5) Generates the final YAML content pack.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.pack_dir = base_dir / "data" / "issuesignal" / "packs"
        self.pack_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, data: dict):
        issue_id = data.get("id", "IS-UNKNOWN")
        file_path = self.pack_dir / f"{issue_id}.yaml"
        
        pack = {
            "header": {
                "issue_id": issue_id,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "PUBLISHED"
            },
            "narrative": {
                "one_liner": data.get("one_liner", ""),
                "long_form": data.get("long_form", ""),
                "shorts_ready": data.get("shorts_ready", [])
            },
            "ticker_card": data.get("tickers", []),
            "safety": {
                "kill_switch": False,
                "confidence": data.get("confidence", 0)
            },
            "trigger_quote": data.get("trigger_quote")
        }
        
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(pack, f, allow_unicode=True)
            
        return file_path
