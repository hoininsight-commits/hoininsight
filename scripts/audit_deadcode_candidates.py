#!/usr/bin/env python3
import os
import re
import glob
from pathlib import Path

def get_runtime_files(project_root):
    pipeline_file = project_root / ".github" / "workflows" / "full_pipeline.yml"
    if not pipeline_file.exists():
        print("Error: full_pipeline.yml not found.")
        return set()

    content = pipeline_file.read_text()
    # Find all python -m xxx.yyy or python xxx/yyy.py
    # Allowing for python, python3, or any variation followed by optional -m
    py_modules = re.findall(r'python3?\s+-m\s+([a-zA-Z0-9\._]+)', content)
    py_files = re.findall(r'python3?\s+([a-zA-Z0-9\._\-/]+\.py)', content)
    
    runtime_files = set()
    for mod in py_modules:
        # handle src.xxx or tests.xxx
        rel_path = mod.replace(".", "/") + ".py"
        if (project_root / rel_path).exists():
            runtime_files.add(rel_path)
        elif (project_root / mod.replace(".", "/") / "__init__.py").exists():
            runtime_files.add(mod.replace(".", "/") + "/__init__.py")

    for f in py_files:
        if (project_root / f).exists():
            runtime_files.add(f)
            
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
        # Find imports from src or tests
        # from src.xxx import yyy
        # import src.xxx
        imports = re.findall(r'(?:from|import)\s+(src|tests)\.([\w\.]+)', content)
        for prefix, imp in imports:
            base = f"{prefix}/{imp.replace('.', '/')}"
            py_path = f"{base}.py"
            init_path = f"{base}/__init__.py"
            
            if (project_root / py_path).exists():
                all_imports.add(py_path)
                to_scan.append(py_path)
            elif (project_root / init_path).exists():
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
