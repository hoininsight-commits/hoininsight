import os
import sys
import logging

def check_learning_enabled():
    """
    Checks if Phase 31 (Learning/Narrative) is enabled via ENABLE_LEARNING env var.
    If not 'true', it prints a message and exits the process silently (exit 0).
    """
    is_enabled = os.environ.get("ENABLE_LEARNING", "false").lower() == "true"
    
    if not is_enabled:
        # Using print instead of logger to ensure visibility in standard workflow output 
        # without requiring logging configuration in every module.
        print("[GUARD] ENABLE_LEARNING is false or unset. Phase 31 execution skipped.")
        sys.exit(0)
    
    print("[GUARD] ENABLE_LEARNING is true. Proceeding with Phase 31 execution.")
