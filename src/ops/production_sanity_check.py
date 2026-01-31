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
    print("[SANITY] Starting Production Artifact Sanity Check...")
    root = Path(__file__).parent.parent.parent
    
    # 1. Check Date Folders
    check_date_folders(root / "data/decision")
    check_date_folders(root / "data/dashboard")
    
    # 2. Check Decision Files
    # (Covered by check_date_folders for filename tokens, but let's check packs specially)
    pack_dir = root / "data/issuesignal/packs"
    if pack_dir.exists():
        for item in pack_dir.glob("*"):
            # Refined check to avoid 'laTEST' matches
            upper_name = item.name.upper()
            is_mock = False
            
            # Split filename by common delimiters to check exact tokens
            import re
            tokens = re.split(r'[_\-\.]', upper_name)
            
            for token in ["MOCK", "TEST", "DEMO"]:
                if token in tokens:
                    is_mock = True
                    break
            
            if is_mock:
                print(f"[FAIL] Mock pack detected: {item}")
                sys.exit(1)
            
        # Content check for packs (Optimized: call once outside loop)
        check_files_content(pack_dir)

    print("[SANITY] Passed. No mock/future artifacts detected.")

if __name__ == "__main__":
    main()
