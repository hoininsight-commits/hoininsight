import os
import re
from pathlib import Path

def test_ref013_architecture_boundaries():
    print("=== VERIFYING REF-013: Architecture Boundaries ===")
    project_root = Path(os.getcwd())
    
    # 1. Engine Layer Guard: No docs/ or docs/ui/ strings in Engine code
    engine_roots = ["src/engine", "src/collectors", "src/anomaly", "src/topics"]
    forbidden_engine_strings = ["docs/", "docs/ui", "render.js", "styles.css"]
    
    violations = []
    for root in engine_roots:
        p_root = project_root / root
        if not p_root.exists(): continue
        for p in p_root.rglob("*.py"):
            # Skip common utils if any
            content = p.read_text(encoding="utf-8")
            for fs in forbidden_engine_strings:
                if fs in content:
                    # Basic heuristic: ignore comments or long strings that aren't path-like
                    # But for REF-013, we are strict.
                    violations.append(f"Engine Leak: {p.relative_to(project_root)} contains '{fs}'")

    # 2. UI Layer Guard: No Python logic/src references in JS
    ui_root = project_root / "docs/ui"
    forbidden_ui_strings = ["src/", "import ... from", "pipeline", "anomaly", "scoring"]
    # We relax keywords but block "src/" paths strictly
    for p in ui_root.rglob("*.js"):
        content = p.read_text(encoding="utf-8")
        if "src/" in content:
            # Allow strings like 'src=' in HTML/IMG tags if we were checking HTML, 
            # but in JS 'src/' usually implies a path to source.
            if re.search(r"['\"]src/", content):
                violations.append(f"UI Leak: {p.relative_to(project_root)} attempts to access src/")

    # 3. Interpreter Boundary (Scaffold check)
    interpreter_root = project_root / "src/interpreters"
    assert interpreter_root.exists(), "Interpreter layer directory missing"
    assert (interpreter_root / "base.py").exists(), "Interpreter base interface missing"

    if violations:
        print("\n".join(violations))
        assert False, f"Architecture boundary violations found: {len(violations)}"

    print("\n=== REF-013 BOUNDARY SUCCESS ===")

if __name__ == "__main__":
    test_ref013_architecture_boundaries()
