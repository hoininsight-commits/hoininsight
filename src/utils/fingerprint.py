from __future__ import annotations

import hashlib

def make_fingerprint(entity: str, ts_utc: str, unit: str, source: str, metric_name: str) -> str:
    key = f"{entity}|{ts_utc}|{unit}|{source}|{metric_name}".encode("utf-8")
    return hashlib.sha256(key).hexdigest()[:16]
