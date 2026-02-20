import yaml
import os
import re
import json
from pathlib import Path
from datetime import datetime, timedelta

MAP_PATH = "registry/refactor/legacy_map_v1.yml"
LEDGER_PATH = "data_outputs/ops/deprecation_ledger.json"

def load_legacy_map():
    project_root = Path(os.getcwd())
    path = project_root / MAP_PATH
    if not path.exists():
        return {"legacy_items": []}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {"legacy_items": []}

def scan_codebase():
    print("=== REF-010 Legacy Deprecation Scanner ===")
    config = load_legacy_map()
    items = config.get("legacy_items", [])
    defaults = config.get("defaults", {"sunset_days": 21})
    
    hits = []
    project_root = Path(os.getcwd())
    
    now = datetime.now()
    sunset_date = (now + timedelta(days=defaults["sunset_days"])).strftime("%Y-%m-%d")
    
    for item in items:
        key = item.get("legacy_key")
        target_paths = item.get("paths", [])
        detect_rules = item.get("detect", [])
        replacement = item.get("replacement", "N/A")
        severity = item.get("severity", "LOW")
        
        for p_str in target_paths:
            p = project_root / p_str
            if not p.exists():
                continue
                
            content = p.read_text(encoding="utf-8")
            hit_found = False
            
            for rule in detect_rules:
                if rule.startswith("string_contains:"):
                    target = rule[len("string_contains:"):]
                    if target in content:
                        hit_found = True
                        break
                elif rule.startswith("regex:"):
                    pattern = rule[len("regex:"):]
                    if re.search(pattern, content):
                        hit_found = True
                        break
            
            if hit_found:
                hits.append({
                    "legacy_key": key,
                    "path": p_str,
                    "reason": f"Matched rule in {p_str}",
                    "replacement": replacement,
                    "sunset": sunset_date,
                    "severity": severity
                })
    
    # Build Ledger
    summary = {
        "total_hits": len(hits),
        "high": len([h for h in hits if h["severity"] == "HIGH"]),
        "med": len([h for h in hits if h["severity"] == "MED"]),
        "low": len([h for h in hits if h["severity"] == "LOW"])
    }
    
    status = "OK"
    if summary["high"] > 0: status = "FAIL" if os.getenv("HOIN_LEGACY_ENFORCE") == "1" else "WARN"
    elif summary["total_hits"] > 0: status = "WARN"
    
    ledger = {
        "date": now.strftime("%Y-%m-%d"),
        "status": status,
        "legacy_hits": hits,
        "summary": summary
    }
    
    # Save to data_outputs (Standard) and mirror to data/ops if needed
    out_path = project_root / LEDGER_PATH
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(ledger, f, indent=2, ensure_ascii=False)
        
    print(f"[Scanner] Created ledger with {len(hits)} hits at {LEDGER_PATH}")
    return ledger

if __name__ == "__main__":
    scan_codebase()
