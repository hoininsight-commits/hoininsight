import os
import sys
from pathlib import Path
from src.legacy_guard.boundary import is_allowed

# This is a cross-check logic for REF-009
# We extend the existing is_allowed logic in guards if necessary,
# but the primary constraint is checking the CALLER'S context.

def check_new_context_violation(module_name: str, caller_file_path: str) -> (bool, str):
    """
    Checks if a legacy module is being called from a NEW (non-legacy) context.
    Returns (is_violation, reason).
    """
    from src.legacy_guard.boundary import is_legacy_context
    
    if is_legacy_context(caller_file_path):
        return False, "LEGACY_CONTEXT_ALLOWED"
    
    # If we are here, caller is in NEW context.
    # New context is NEVER allowed to use legacy modules, even if they are in the allowlist for old code.
    return True, "NEW_CONTEXT_FORBIDDEN"
