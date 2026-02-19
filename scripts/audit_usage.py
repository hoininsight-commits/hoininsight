
import os
import json
from pathlib import Path

def scan_repository(root_path):
    audit_results = {
        "ui_entrypoints": [],
        "workflow_references": [],
        "code_references": {},
        "deprecated_paths_found": []
    }
    
    deprecated_patterns = [
        "docs/data/ui", "data/ui", "data_outputs/ui", "exports", "docs/data/decision"
    ]
    
    # Initialize code references
    for pattern in deprecated_patterns:
        audit_results["code_references"][pattern] = []

    for root, dirs, files in os.walk(root_path):
        if ".git" in root or "__pycache__" in root:
            continue
            
        rel_root = os.path.relpath(root, root_path)
        
        # Check UI Entrypoints based on directory/file existence
        if rel_root == "docs" and "index.html" in files:
            audit_results["ui_entrypoints"].append("docs/index.html")
        if rel_root == "docs/ui" and "index.html" in files:
            audit_results["ui_entrypoints"].append("docs/ui/index.html")
        if rel_root == "ui" and "index.html" in files:
            audit_results["ui_entrypoints"].append("ui/index.html")
        if rel_root == "dashboard" and "index.html" in files:
            audit_results["ui_entrypoints"].append("dashboard/index.html")

        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    
                    # specific check for workflow files
                    if ".github/workflows" in file_path:
                         for pattern in deprecated_patterns:
                            if pattern in content:
                                audit_results["workflow_references"].append({
                                    "file": os.path.relpath(file_path, root_path),
                                    "pattern": pattern
                                })

                    # General code scan
                    for pattern in deprecated_patterns:
                        if pattern in content:
                            audit_results["code_references"][pattern].append(os.path.relpath(file_path, root_path))
                            if pattern not in audit_results["deprecated_paths_found"]:
                                audit_results["deprecated_paths_found"].append(pattern)
            except Exception:
                pass # Binary or unreadable

    return audit_results

def generate_report(results, output_json, output_md):
    # JSON
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        
    # Markdown
    with open(output_md, "w", encoding="utf-8") as f:
        f.write("# Repository Usage Audit Report\n\n")
        f.write("## UI Entrypoints Found\n")
        for entry in results["ui_entrypoints"]:
            f.write(f"- {entry}\n")
        
        f.write("\n## Deprecated Path Usage\n")
        for pattern, files in results["code_references"].items():
            f.write(f"### {pattern} ({len(files)} files)\n")
            # Limit list in MD to avoid noise
            for file in files[:5]: 
                f.write(f"- {file}\n")
            if len(files) > 5:
                f.write(f"- ... and {len(files)-5} more\n")

if __name__ == "__main__":
    root = os.getcwd()
    print(f"Scanning repository at {root}...")
    results = scan_repository(root)
    
    out_dir = Path("data_outputs/ops")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    generate_report(
        results, 
        out_dir / "usage_audit.json", 
        out_dir / "usage_audit.md"
    )
    print("Audit complete. Reports generated in data_outputs/ops/")
