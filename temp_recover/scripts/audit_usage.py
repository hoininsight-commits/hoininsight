
import os
import json
from pathlib import Path

def get_file_category(file_path):
    if "tests/" in file_path: return "tests"
    if "scripts/" in file_path: return "scripts"
    if "docs/" in file_path: return "docs"
    if ".github/workflows" in file_path: return "workflows"
    return "runtime"

def scan_repository(root_path):
    audit_results = {
        "ui_entrypoints": [],
        "workflow_references": [],
        "code_references": {},
        "deprecated_paths_found": [],
        "quantification": {} 
    }
    
    deprecated_patterns = [
        "docs/data/ui", "data/ui", "data_outputs/ui", "exports", "docs/data/decision"
    ]
    
    # Initialize structures
    for pattern in deprecated_patterns:
        audit_results["code_references"][pattern] = []
        audit_results["quantification"][pattern] = {
            "total_reference_count": 0,
            "runtime_reference_count": 0,
            "test_reference_count": 0,
            "verify_copy_reference_count": 0,
            "top_runtime_referrers": [], # Will store tuples (file, count)
            # We keep the old breakdown for compatibility but prioritize new metrics
            "reference_type_breakdown": {
                "tests": 0, "scripts": 0, "docs": 0, "workflows": 0, "runtime": 0
            }
        }

    # Helper to track referrer counts
    referrer_counts = {p: {} for p in deprecated_patterns} # For total top referrers
    runtime_referrer_counts = {p: {} for p in deprecated_patterns} # For RUNTIME top referrers

    for root, dirs, files in os.walk(root_path):
        if ".git" in root or "__pycache__" in root:
            continue
            
        rel_root = os.path.relpath(root, root_path)
        
        # EXCLUSION RULE: Skip data_outputs/ops/ entirely (self-artifacts)
        if rel_root.startswith("data_outputs/ops"):
            continue

        # Check UI Entrypoints
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
            rel_path = os.path.relpath(file_path, root_path)
            
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    
                    # Workflow check
                    if ".github/workflows" in file_path:
                         for pattern in deprecated_patterns:
                            if pattern in content:
                                audit_results["workflow_references"].append({
                                    "file": rel_path,
                                    "pattern": pattern
                                })

                    # General code scan & Quantification
                    for pattern in deprecated_patterns:
                        count = content.count(pattern)
                        if count > 0:
                            # 1. Add to code_references
                            if rel_path not in audit_results["code_references"][pattern]:
                                audit_results["code_references"][pattern].append(rel_path)
                            
                            # 2. Track deprecated paths found
                            if pattern not in audit_results["deprecated_paths_found"]:
                                audit_results["deprecated_paths_found"].append(pattern)
                                
                            # 3. Quantify Total
                            audit_results["quantification"][pattern]["total_reference_count"] += count
                            
                            # 4. Domain Separation
                            if "remote_verify_" in rel_path:
                                audit_results["quantification"][pattern]["verify_copy_reference_count"] += count
                            elif "tests/" in rel_path:
                                audit_results["quantification"][pattern]["test_reference_count"] += count
                            else:
                                # Treat as runtime (includes scripts/docs unless specific filter needed)
                                # But we want strict "runtime code" vs "docs".
                                # Let's stick to the prompt categories: runtime_refs, test_refs, verify_copy_refs
                                # Ideally, runtime_refs = src/* + scripts/* + docs/* excluding tests/verify
                                audit_results["quantification"][pattern]["runtime_reference_count"] += count
                                runtime_referrer_counts[pattern][rel_path] = count

                            # Category breakdown (Legacy)
                            cat = get_file_category(rel_path)
                            audit_results["quantification"][pattern]["reference_type_breakdown"][cat] += count
                            
            except Exception:
                pass # Binary or unreadable

    # Finalize Top Referrers (only runtime interesting ones)
    for pattern in deprecated_patterns:
        # Sort runtime files by count descending
        sorted_referrers = sorted(runtime_referrer_counts[pattern].items(), key=lambda item: item[1], reverse=True)
        # Take top 10
        audit_results["quantification"][pattern]["top_runtime_referrers"] = sorted_referrers[:10]

    return audit_results

def generate_report(results, output_json, output_md):
    # JSON
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        
    # Markdown
    with open(output_md, "w", encoding="utf-8") as f:
        f.write("# Repository Usage Audit Report (Sanitized)\n\n")
        f.write("> **Note**: Self-references (`data_outputs/ops/`) are excluded.\n\n")
        
        f.write("## UI Entrypoints\n")
        for entry in results["ui_entrypoints"]:
            f.write(f"- {entry}\n")
        
        f.write("\n## Deprecated Path Quantification\n")
        
        for pattern, data in results["quantification"].items():
            if data["total_reference_count"] == 0:
                continue
                
            f.write(f"\n### `{pattern}`\n")
            f.write(f"- **Total References**: {data['total_reference_count']}\n")
            f.write(f"  - **Runtime**: {data['runtime_reference_count']}\n")
            f.write(f"  - **Tests**: {data['test_reference_count']}\n")
            f.write(f"  - **Verify Copies**: {data['verify_copy_reference_count']}\n")
            
            f.write("- **Top Runtime Referrers**:\n")
            for file, count in data["top_runtime_referrers"]:
                f.write(f"  - `{file}`: {count} refs\n")

if __name__ == "__main__":
    root = os.getcwd()
    print(f"Scanning repository at {root} (Sanitized)...")
    results = scan_repository(root)
    
    out_dir = Path("data_outputs/ops")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    generate_report(
        results, 
        out_dir / "usage_audit.json", 
        out_dir / "usage_audit.md"
    )
    print("Audit complete. Reports generated in data_outputs/ops/")
