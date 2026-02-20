import os
import re
import sys
from pathlib import Path
from src.legacy_guard.boundary import is_legacy_context

def scan_for_new_legacy():
    print("=== VERIFYING REF-009: No New Legacy (Freeze Check) ===")
    project_root = Path(os.getcwd())
    
    # Patterns to look for
    LEGACY_PATTERNS = [
        re.compile(r"hit_legacy\("),
        re.compile(r"from src\.ui"),
        re.compile(r"import src\.ui")
    ]
    
    violations = []
    
    # Iterate through all python files
    for p in project_root.rglob("*.py"):
        rel_path = str(p.relative_to(project_root))
        
        # Skip legacy context files themselves
        if is_legacy_context(rel_path):
            continue
            
        # Skip tests or internal stuff if needed, but REF-009 says "New files"
        if "venv" in rel_path or ".git" in rel_path or "tests/" in rel_path:
            continue
            
        try:
            content = p.read_text(encoding="utf-8")
            for line in content.splitlines():
                if "def hit_legacy(" in line: continue # Skip definition
                for pattern in LEGACY_PATTERNS:
                    if pattern.search(line):
                        violations.append({
                            "file": rel_path,
                            "reason": f"Pattern {pattern.pattern} found in NEW context"
                        })
                        break
        except Exception as e:
            print(f"Skipping {rel_path}: {e}")

    if violations:
        print("\n❌ [REF-009][BLOCK] New legacy usage detected!")
        for v in violations:
            print(f"- file: {v['file']}")
            print(f"  reason: {v['reason']}")
        return False
        
    print("✅ No new legacy usage detected outside legacy boundaries.")
    return True

if __name__ == "__main__":
    if not scan_for_new_legacy():
        sys.exit(1)
