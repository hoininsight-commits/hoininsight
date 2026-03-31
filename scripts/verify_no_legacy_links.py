#!/usr/bin/env python3
"""
[LEGACY-LINK-GUARD] CI Guard: Prevent legacy UI links in the new operator dashboard.
Scans docs/index.html and docs/ui/**/*.js for "legacy" strings.
"""
import sys
import os
import glob
from pathlib import Path

# Config: Files to scan
SCAN_TARGETS = [
    "docs/index.html",
    "docs/ui/**/*.js"
]

# Exceptions: Strings that are allowed to contain 'legacy' (e.g. comments, specific sanctioned refs)
# For now, we enforce a strict zero-tolerance for "legacy" in these files.
EXCLUSIONS = []

def main():
    print("[CI Guard] Scanning for legacy links/references...")
    
    found_any = False
    
    for pattern in SCAN_TARGETS:
        files = glob.glob(pattern, recursive=True)
        for f_path in files:
            path = Path(f_path)
            content = path.read_text(encoding="utf-8")
            
            # Simple case-insensitive check for "legacy"
            if "legacy" in content.lower():
                # Report context
                lines = content.splitlines()
                for i, line in enumerate(lines, 1):
                    if "legacy" in line.lower():
                         print(f"❌ ERROR: Legacy reference found in {f_path}:L{i}")
                         print(f"   > {line.strip()}")
                         found_any = True
    
    if found_any:
        print("\n❌ CI GUARD FAILED: Legacy UI references detected in the new dashboard.")
        sys.exit(1)
        
    print("✅ [OK] No legacy links detected in target files.")
    sys.exit(0)

if __name__ == "__main__":
    main()
