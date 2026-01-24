import os
import datetime

def get_target_ymd() -> str:
    """
    Returns the target date (YYYY-MM-DD) string.
    Priority:
    1. HOIN_TARGET_DATE env var
    2. UTC Today
    """
    target = os.environ.get("HOIN_TARGET_DATE")
    if target:
        return target
    return datetime.datetime.utcnow().strftime("%Y-%m-%d")

def get_target_parts():
    """
    Returns (year, month, day) strings.
    """
    ymd = get_target_ymd()
    parts = ymd.split("-")
    if len(parts) == 3:
        return parts[0], parts[1], parts[2]
    # Fallback if malformed
    now = datetime.datetime.utcnow()
    return now.strftime("%Y"), now.strftime("%m"), now.strftime("%d")
