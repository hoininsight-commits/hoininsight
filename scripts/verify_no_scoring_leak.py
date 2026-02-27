#!/usr/bin/env python3
import sys
import re
import glob
from pathlib import Path

# Config: Targets and Forbidden Patterns
TARGET_PATHS = [
    "src/ui/run_publish_ui_decision_assets.py",
    "src/reporters/*.py",
    "docs/ui/**/*.js"
]

FORBIDDEN_PATTERNS = [
    r'Math\.random',
    r'random\.random',
    r'sum\(ord\(c\)', # Salt generation pattern
    r'charCodeAt',
    r'\*\s*0\.\d+',   # Multiplication by float (weighting logic)
    r'\*\s*1\.\d+',   # Multiplier logic
    r'\+\s*float\(salt\)',
    r'\(base_val\s*\*\s*0\.75\)'
]

def main():
    print("[CI Guard] Checking for scoring leaks (Logic Leakage)...")
    
    violation = False
    
    for pattern_path in TARGET_PATHS:
        files = glob.glob(pattern_path, recursive=True)
        for f_path in files:
            path = Path(f_path)
            content = path.read_text(encoding="utf-8", errors='ignore')
            
            for pattern in FORBIDDEN_PATTERNS:
                if re.search(pattern, content):
                    # Report context
                    lines = content.splitlines()
                    for i, line in enumerate(lines, 1):
                        if re.search(pattern, line):
                             print(f"❌ ERROR: [LOGIC-LEAK] Forbidden pattern '{pattern}' found in {f_path}:L{i}")
                             print(f"   > {line.strip()}")
                             violation = True
    
    if violation:
        print("\n❌ CI GUARD FAILED: Score generation or multiplier logic found in non-engine layer.")
        sys.exit(1)
        
    print("✅ [OK] Layer responsibility validated. No scoring leaks found.")
    sys.exit(0)

if __name__ == "__main__":
    main()
