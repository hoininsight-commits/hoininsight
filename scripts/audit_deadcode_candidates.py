#!/usr/bin/env python3
import os
import re
import glob
from pathlib import Path

def get_runtime_files(project_root):
    # entrypoints from audit_runtime (manually simplified for this script)
    entrypoints = [
        "src/engine",
        "src/issuesignal/run_issuesignal.py",
        "src/ops/narrative_intelligence_layer.py",
        "src/ops/video_intelligence_layer.py",
        "src/ui/run_publish_ui_decision_assets.py",
        "src/dashboard/dashboard_generator.py",
        "src/reporting/telegram_daily_summary.py"
    ]
    # Expand specialized collectors
    entrypoints.extend(glob.glob("src/collectors/*.py"))
    entrypoints.extend(glob.glob("src/ops/*.py"))
    entrypoints.extend(glob.glob("src/pipeline/*.py"))
    
    runtime_files = set()
    for ep in entrypoints:
        p = project_root / ep
        if p.exists():
            runtime_files.add(str(p.relative_to(project_root)))
            
    return runtime_files

def get_imported_files(project_root, runtime_files):
    all_imports = set(runtime_files)
    to_scan = list(runtime_files)
    
    seen = set()
    
    while to_scan:
        current = to_scan.pop()
        if current in seen: continue
        seen.add(current)
        
        path = project_root / current
        if not path.is_file() or path.suffix != ".py": continue
        
        content = path.read_text(errors='ignore')
        # Simple regex for from src... import or import src...
        imports = re.findall(r'(?:from|import)\s+src\.([\w\.]+)', content)
        for imp in imports:
            rel_path = imp.replace(".", "/") + ".py"
            if (project_root / rel_path).exists():
                all_imports.add(rel_path)
                to_scan.append(rel_path)
            elif (project_root / (imp.replace(".", "/") + "/__init__.py")).exists():
                init_path = imp.replace(".", "/") + "/__init__.py"
                all_imports.add(init_path)
                to_scan.append(init_path)
                
    return all_imports

def audit_deadcode():
    project_root = Path(__file__).parent.parent
    src_files = set()
    for root, dirs, files in os.walk(project_root / "src"):
        for f in files:
            if f.endswith(".py"):
                src_files.add(str(Path(root) / f).replace(str(project_root) + "/", ""))

    runtime_files = get_runtime_files(project_root)
    imported_files = get_imported_files(project_root, runtime_files)
    
    # Files called by UI (fetch)
    ui_js_files = glob.glob(str(project_root / "docs/ui/**/*.js"), recursive=True)
    fetched_data = set()
    for js in ui_js_files:
        content = Path(js).read_text(errors='ignore')
        matches = re.findall(r'fetch\([\'"]([\w\/\-\.]+)[\'"]\)', content)
        for m in matches:
            fetched_data.add(m)

    dead_candidates = src_files - imported_files
    
    print("## Dead Code Candidates Audit\n")
    print(f"Total Python files in src/: {len(src_files)}")
    print(f"Files in Runtime/Import Graph: {len(imported_files)}")
    print(f"Potential Dead Candidates: {len(dead_candidates)}\n")
    
    for dc in sorted(list(dead_candidates)):
        reason = "No direct entrypoint or import found."
        # Extra safety: Check if it's a shim mentioned in Phase 19B
        if "shim" in dc.lower():
            print(f"- [KEEP] {dc} (Identified as Shim)")
        else:
            print(f"- [ARCHIVE] {dc} ({reason})")

if __name__ == "__main__":
    audit_deadcode()
