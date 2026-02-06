import yaml
import os
import inspect
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

def is_allowed(module_name: str, caller_file: str = None) -> (bool, str):
    """
    Checks if a module is in the allowlist and hasn't expired.
    REF-009: Also checks if the caller is in a NEW context.
    Returns (allowed, reason).
    """
    # 1. New Context Verification (REF-009 Absolute Rule)
    if caller_file:
        from src.legacy_guard.boundary import is_legacy_context
        if not is_legacy_context(caller_file):
            # Caller is in NEW context. Even if it's in allowlist, we block expansion.
            return False, "NEW_CONTEXT_FORBIDDEN_EXPANSION"

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

def enforce_gate(module_name: str, caller_file: str = None):
    """
    Helper for enforcement.
    """
    from src.ui_logic.guards.warning_mode import get_hard_mode
    
    allowed, reason = is_allowed(module_name, caller_file)
    if get_hard_mode() and not allowed:
        raise RuntimeError(f"[REF-009][CRITICAL] Legacy Access Blocked: {module_name} (Reason: {reason})")
    
    return allowed, reason
