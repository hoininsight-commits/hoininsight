#!/usr/bin/env python3
import sys
import subprocess
from pathlib import Path

# Config: Authorized vs Deprecated
AUTHORIZED_PATH = "src/engine/collectors/"
DEPRECATED_PATHS = ["src/collectors/", "src/events/collectors/"]

def main():
    print("[CI Guard] Verifying Collector SSOT Policy...")
    
    # 1. Get list of tracked files in deprecated paths
    try:
        violation = False
        for dep_path in DEPRECATED_PATHS:
            result = subprocess.run(
                ["git", "ls-files", dep_path],
                capture_output=True, text=True, check=True
            )
            files = [f for f in result.stdout.splitlines() if not f.endswith("__init__.py")]
            
            # Since we allowed existing files in Phase 20, we need to check for "new" files
            # or simply enforce that no new files should EVER be added.
            # In Phase 20, we just want to ensure that any FUTURE collectors go to the authorized path.
            # For this guard, we will fail if we see any non-sanctioned collectors in deprecated paths.
            
            for f in files:
                # We'll maintain an 'Existing_Allow_List' if needed, but for now
                # the policy says "Existing files are maintained, but new additions fail".
                # A simple way to check "new" in CI is to check 'git status' or similar.
                pass
                
        # Simpler rule: Fail if ANY file in DEPRECATED_PATHS is not also in a "historical_allow_list"
        # However, Phase 20 policy specifically says: "신규 파일 추가 시 CI Guard에 의해 차단"
        # We'll use git to check for files added in the current commit/index.
        
        result_new = subprocess.run(
            ["git", "diff", "--name-only", "--cached", "--diff-filter=A"],
            capture_output=True, text=True, check=True
        )
        added_files = result_new.stdout.splitlines()
        
        for f in added_files:
            for dep_path in DEPRECATED_PATHS:
                if f.startswith(dep_path) and not f.endswith("__init__.py"):
                    print(f"❌ ERROR: [SSOT-VIOLATION] New collector '{f}' added to deprecated path.")
                    print(f"   Please move it to {AUTHORIZED_PATH}")
                    violation = True
                    
        if violation:
            sys.exit(1)
            
        print("✅ [OK] No new collectors in deprecated paths.")
        sys.exit(0)
        
    except Exception as e:
        print(f"Error executing policy check: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
