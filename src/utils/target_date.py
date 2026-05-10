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

def get_current_round():
    """
    Determines round based on current hour in KST:
    23, 0-4  -> Round 1 (Prep for 00:00)
    5-10     -> Round 2 (Prep for 06:00)
    11-16    -> Round 3 (Prep for 12:00)
    17-22    -> Round 4 (Prep for 18:00)
    """
    now = get_now_kst()
    hour = now.hour
    if hour >= 23 or hour < 5:
        return 1
    elif 5 <= hour < 11:
        return 2
    elif 11 <= hour < 17:
        return 3
    else:
        return 4

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

def get_standard_path_prefix() -> str:
    """
    Returns the standardized path prefix (YYYY/MM/DD).
    [v24.0] Round_N hierarchy has been deprecated for Topic_N isolation.
    """
    y, m, d = get_target_parts()
    return f"{y}/{m}/{d}"
