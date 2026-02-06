import yaml
import os
from pathlib import Path
from datetime import datetime

ALLOWLIST_PATH = "registry/ops/legacy_allowlist_v1.yml"

def load_allowlist():
    """Loads the legacy allowlist from the registry."""
    project_root = Path(os.getcwd())
    path = project_root / ALLOWLIST_PATH
    if not path.exists():
        return {"allow": []}
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {"allow": []}
    except Exception as e:
        print(f"[HardGate] Failed to load allowlist: {e}")
        return {"allow": []}

def is_allowed(module_name: str) -> (bool, str):
    """
    Checks if a module is in the allowlist and hasn't expired.
    Returns (allowed, reason).
    """
    config = load_allowlist()
    if not config.get("enabled", True):
        return False, "ALLOWLIST_DISABLED"

    now = datetime.now().strftime("%Y-%m-%d")
    
    for entry in config.get("allow", []):
        pattern = entry.get("module", "")
        if module_name == pattern or module_name.startswith(pattern + "."):
            expires = entry.get("expires", "1900-01-01")
            if now <= expires:
                return True, f"ALLOWLIST_MATCH({entry.get('reason', 'N/A')})"
            else:
                return False, f"EXPIRED({expires})"
                
    return False, "NOT_IN_ALLOWLIST"
