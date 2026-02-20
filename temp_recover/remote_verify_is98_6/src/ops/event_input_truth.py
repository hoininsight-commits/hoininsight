import json
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

def diagnose(run_ymd: str, base_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    Diagnoses why events_count might be 0.
    Returns:
    {
      "run_date": "YYYY-MM-DD",
      "events_count": int,
      "root_cause_code": str or None,
      "details": { "missing_paths": [...], "exceptions": [...] }
    }
    """
    if base_dir is None:
        base_dir = Path.cwd()
        
    run_date_path = run_ymd.replace("-", "/")
    events_json_path = base_dir / "data" / "events" / run_date_path / "events.json"
    registry_path = base_dir / "registry" / "sources.yml" # This is for narrative events if applicable
    datasets_registry_path = base_dir / "registry" / "datasets.yml"
    
    result = {
        "run_date": run_ymd,
        "events_count": 0,
        "root_cause_code": None,
        "details": {
            "missing_paths": [],
            "exceptions": []
        }
    }
    
    # 1. Check Output File
    if not events_json_path.exists():
        result["root_cause_code"] = "OUTPUT_PATH_MISSING"
        result["details"]["missing_paths"].append(str(events_json_path))
        
        # Investigate deeper if output is missing
        # Check if registries exist
        if not datasets_registry_path.exists():
            result["root_cause_code"] = "SOURCE_REGISTRY_MISSING"
            result["details"]["missing_paths"].append(str(datasets_registry_path))
            return result
            
        try:
            # If we reach here and output is missing, check if registry has any sources
            has_sources = False
            if registry_path.exists():
                with open(registry_path, "r", encoding="utf-8") as f:
                    src_data = yaml.safe_load(f) or {}
                    if src_data.get("sources"):
                        has_sources = True
            
            # Check datasets registry for enabled sources
            if not has_sources and datasets_registry_path.exists():
                 # Minimal check: does it have any lines that look like a dataset entry?
                 content = datasets_registry_path.read_text(encoding="utf-8")
                 if "dataset_id" in content or "enabled: true" in content:
                     has_sources = True
            
            if has_sources:
                result["root_cause_code"] = "FETCH_FAILED"
            else:
                result["root_cause_code"] = "OUTPUT_PATH_MISSING"
                
        except Exception as e:
            result["details"]["exceptions"].append(str(e))
            result["root_cause_code"] = "PARSE_FAILED"
            
        return result

    # 2. Extract Count from events.json
    try:
        content = json.loads(events_json_path.read_text(encoding="utf-8"))
        events = content.get("events", [])
        result["events_count"] = len(events)
        
        if result["events_count"] == 0:
            result["root_cause_code"] = "OUTPUT_EMPTY_VALID"
        else:
            result["root_cause_code"] = None # SUCCESS
            
    except Exception as e:
        result["root_cause_code"] = "PARSE_FAILED"
        result["details"]["exceptions"].append(str(e))
        
    return result

if __name__ == "__main__":
    import sys
    ymd = sys.argv[1] if len(sys.argv) > 1 else "2026-01-26"
    print(json.dumps(diagnose(ymd), indent=2))
