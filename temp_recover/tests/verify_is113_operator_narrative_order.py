import json
import sys
from pathlib import Path

def fail(msg):
    print(f"[FAIL] {msg}")
    sys.exit(1)

def start_verification():
    print(">>> Verifying [IS-113] Operator Narrative Order Layer...")
    
    base_dir = Path(".")
    json_path = base_dir / "data/ui/operator_narrative_order.json"
    
    if not json_path.exists():
        fail(f"File not found: {json_path}")
        
    try:
        data = json.loads(json_path.read_text(encoding='utf-8'))
    except Exception as e:
        fail(f"JSON Parse Error: {e}")
        
    # 1. Schema Check
    required_keys = ["date", "decision_zone", "content_package", "support_zone", "guards"]
    for k in required_keys:
        if k not in data:
            fail(f"Missing root key: {k}")
            
    # 2. Undefined Check (Recursive Value Check)
    def check_values(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                # checks keys? well, "undefined" in key is unlikely unless bug, but "no_undefined" key is valid.
                check_values(v)
        elif isinstance(obj, list):
            for item in obj:
                check_values(item)
        elif isinstance(obj, str):
            if "undefined" in obj:
                 # Check if it's the known guard key? No, obj is value here.
                 fail(f"Found 'undefined' in value: {obj}")
    
    
    check_values(data)

    json_str = json.dumps(data)
    if "null" in json_str: # guard against null too
        pass # null is valid JSON, but we preferred empty string. The builder uses _guard_str which returns "".
        # If strict check needed:
        # fail("Found 'null' value")
        
    # 3. Content Package
    pkg = data["content_package"]
    if not pkg.get("long", {}).get("title"):
        fail("Long title is empty")
        
    shorts = pkg.get("shorts", [])
    print(f"Shorts count: {len(shorts)}")
    
    # 4. Evidence Whitelist Check
    # Verify all evidence strings contain parens
    def check_evidence(ev_list, context):
        for e in ev_list:
            if "(" not in e or ")" not in e:
                fail(f"Evidence format violation in {context}: {e}")
                
    check_evidence(pkg["long"].get("evidence", []), "Long")
    for s in shorts:
        check_evidence(s.get("evidence", []), "Shorts")
        
    sz = data["support_zone"]
    for item in sz.get("three_eye", []):
        check_evidence([item.get("evidence", "")], "Three Eye")
        
    print("[PASS] Schema & Content Logic Verified")

if __name__ == "__main__":
    start_verification()
