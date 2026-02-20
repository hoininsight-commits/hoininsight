import sys
from pathlib import Path
from datetime import datetime
import json

def get_kst_today_ymd():
    # Simple KST approximation: UTC+9
    from datetime import timedelta, timezone
    kst = timezone(timedelta(hours=9))
    return datetime.now(kst).strftime("%Y%m%d")

def check_date_folders(base_path, invalid_tokens=["TEST", "MOCK", "DEMO"]):
    """Check for future dates or invalid tokens in YYYY/MM/DD structure."""
    if not base_path.exists(): return
    
    today_int = int(get_kst_today_ymd())
    
    # Walk distinct years
    for year_dir in base_path.iterdir():
        if not year_dir.is_dir(): continue
        if not year_dir.name.isdigit(): continue
        
        # Walk distinct months
        for month_dir in year_dir.iterdir():
            if not month_dir.is_dir(): continue
            if not month_dir.name.isdigit(): continue
            
            # Walk distinct days
            for day_dir in month_dir.iterdir():
                if not day_dir.is_dir(): continue
                if not day_dir.name.isdigit(): continue
                
                # Check date
                ymd_str = f"{year_dir.name}{month_dir.name}{day_dir.name}"
                try:
                    dir_date_int = int(ymd_str)
                    if dir_date_int > today_int:
                        print(f"[FAIL] Future date directory detected: {day_dir}")
                        sys.exit(1)
                except ValueError: pass
                
                # Check contents
                for item in day_dir.glob("*"):
                    for token in invalid_tokens:
                        if token in item.name.upper():
                            print(f"[FAIL] Invalid token '{token}' in filename: {item}")
                            sys.exit(1)

def check_files_content(path, content_blocklist=["simulate", "mock", "emulate"]):
    """Check file contents for forbidden words."""
    if not path.exists(): return
    
    for file_path in path.glob("**/*"):
        if file_path.is_file() and file_path.suffix.lower() in ['.json', '.yaml', '.yml', '.md']:
            # Skip itself or known scripts
            if "sanity_check" in file_path.name: continue
            
            try:
                text = file_path.read_text(encoding='utf-8').lower()
                for word in content_blocklist:
                    if word in text:
                        # Allow "mock" only if it's explicitly "no_mock" or similar specific exceptions if needed
                        # But strictly enforcing for now.
                        print(f"[FAIL] Forbidden content '{word}' found in {file_path}")
                        # sys.exit(1) # Warning for now as some verified files might have it in comments? 
                        # User requested strict FAIL. But let's check legacy first.
                        # If strict fail requested:
                        sys.exit(1)
            except: pass

def main():
    print("[SANITY] Starting Production Artifact Sanity Check (Strict IS-64)...")
    root = Path(__file__).parent.parent.parent
    
    # [IS-64] Mock/Test Data Ban
    # Scan all 'data/' and 'docs/' directories for files with forbidden patterns
    # Patterns: test_*, *mock*, *sample*
    
    forbidden_roots = [root / "data", root / "docs"]
    forbidden_tokens = ["mock", "sample", "test_"] # "test_" prefix or substring? user said "test_*.json"
    
    # Exceptions (e.g., this script itself or tests/ folder are okay, but data/ shouldn't have them)
    
    for base_dir in forbidden_roots:
        if not base_dir.exists(): continue
        
        for file_path in base_dir.rglob("*"):
            if not file_path.is_file(): continue
            name_lower = file_path.name.lower()
            
            # Skip hidden files
            if name_lower.startswith('.'): continue
            
            # Check for forbidden tokens
            for token in forbidden_tokens:
                if token in name_lower:
                    # Specific exception management
                    # e.g., "latest_run.json" contains "test" -> No
                    # "contest" -> No
                    # Token matching:
                    # User patterns: "test_*.json", "*_mock_*.json", "*sample*"
                    
                    is_violation = False
                    if "mock" in name_lower: is_violation = True
                    if "sample" in name_lower: is_violation = True
                    if name_lower.startswith("test_"): is_violation = True
                    if "_test." in name_lower: is_violation = True # end with _test
                    
                    if is_violation:
                        print(f"[FAIL] Forbidden file pattern detected in production path: {file_path}")
                        sys.exit(1)

    print("[SANITY] Passed. No mock/test/sample artifacts detected in data/ or docs/.")

if __name__ == "__main__":
    main()
