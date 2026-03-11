import json
from pathlib import Path

class HumanInterrupt:
    """
    (IS-18) Allows manual pause of Decision Card emissions.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.config_path = base_dir / "data" / "issuesignal" / "control_config.json"
        self._ensure_config()
        
    def _ensure_config(self):
        if not self.config_path.exists():
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w") as f:
                json.dump({"hold": False}, f)

    def is_held(self) -> bool:
        """
        Returns True if the human has set a manual HOLD.
        """
        try:
            with open(self.config_path, "r") as f:
                config = json.load(f)
            return config.get("hold", False)
        except:
            return False

    def set_hold(self, status: bool):
        """
        Manually sets or releases the HOLD status.
        """
        with open(self.config_path, "r") as f:
            config = json.load(f)
            
        config["hold"] = status
        with open(self.config_path, "w") as f:
            json.dump(config, f, indent=2)
