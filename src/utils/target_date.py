import os
import datetime

def get_target_ymd() -> str:
    """
    Returns the target date (YYYY-MM-DD) string.
    Priority:
    1. HOIN_TARGET_DATE env var
    2. KST Today (UTC+9)
    """
    target = os.environ.get("HOIN_TARGET_DATE")
    if target:
        return target
    # Explicitly calculate KST (UTC+9) 
    # This prevents day-roll issues in environments where TZ is not set to KST
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    now_kst = now_utc + datetime.timedelta(hours=9)
    return now_kst.strftime("%Y-%m-%d")

def get_now_kst():
    """
    Returns the current datetime in KST.
    """
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    return now_utc + datetime.timedelta(hours=9)

def get_target_parts():
    """
    Returns (year, month, day) strings in KST.
    """
    ymd = get_target_ymd()
    parts = ymd.split("-")
    if len(parts) == 3:
        return parts[0], parts[1], parts[2]
    # Fallback if malformed (using KST)
    now_kst = get_now_kst()
    return now_kst.strftime("%Y"), now_kst.strftime("%m"), now_kst.strftime("%d")
