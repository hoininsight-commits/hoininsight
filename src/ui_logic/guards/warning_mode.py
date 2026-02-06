import os

def get_warn_mode():
    """Returns True if legacy warnings should be shown."""
    return os.getenv("HOIN_LEGACY_WARN", "1") == "1"

def get_hard_mode():
    """Returns True if legacy usage should raise an exception."""
    return os.getenv("HOIN_LEGACY_HARD", "0") == "1"
