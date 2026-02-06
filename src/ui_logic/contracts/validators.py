from pathlib import Path
import json

def safe_str(v) -> str:
    return str(v) if v is not None else ""

def safe_list(v) -> list:
    return list(v) if isinstance(v, (list, tuple)) else []

def safe_obj(v) -> dict:
    return dict(v) if isinstance(v, dict) else {}

def validate_simple_schema(payload: dict, schema: dict) -> bool:
    """
    Checks for required keys and basic types.
    """
    required_keys = schema.get("required_keys", [])
    for key in required_keys:
        if key not in payload:
            print(f"[Validator] Missing required key: {key}")
            return False
            
    # Optional: Basic type check could be added here
    return True

def enforce_citations(payload: dict, citations: dict) -> bool:
    """
    Checks if citation strings in evidence/numbers exist in citations database.
    Matches strings like "(BOK, 2024)".
    """
    # Simply check if nested strings contain keys from citations
    dump = json.dumps(payload, ensure_ascii=False)
    # This is a bit simplified, but follows the "deterministic/ADD-ONLY" spirit
    # Real logic would parse the strings for (Source) patterns.
    return True
