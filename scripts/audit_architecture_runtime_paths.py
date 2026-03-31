#!/usr/bin/env python3
import re
import yaml
from pathlib import Path

def audit_runtime():
    project_root = Path(__file__).parent.parent
    pipeline_file = project_root / ".github" / "workflows" / "full_pipeline.yml"
    
    print("## Phase 20: Runtime Architecture Audit\n")
    
    if not pipeline_file.exists():
        print("Error: full_pipeline.yml not found.")
        return

    with open(pipeline_file, "r") as f:
        pipeline = yaml.safe_load(f)

    # 1. Extract Entrypoints from YAML
    print("### 1. Active Entrypoints (from full_pipeline.yml)")
    entrypoints = []
    
    # Simple regex to find python -m or python path commands in the yaml
    content = pipeline_file.read_text()
    py_commands = re.findall(r'python\s+(?:-m\s+)?([\w\.\-/]+)', content)
    
    unique_commands = sorted(list(set(py_commands)))
    for cmd in unique_commands:
        if cmd.startswith("src.") or cmd.startswith("scripts/"):
            print(f"- [RUN] {cmd}")
            entrypoints.append(cmd)
    
    # 2. Trace Key Data Paths
    print("\n### 2. Primary Data Flow Agents")
    
    # Map commands to their likely "Layer" based on user requirements
    layers = {
        "ENGINE": [],
        "OPS": [],
        "PUBLISHER": [],
        "REPORTER": [],
        "SCRIPTS": []
    }
    
    for ep in entrypoints:
        if "collector" in ep or "engine" in ep or "anomaly" in ep:
            layers["ENGINE"].append(ep)
        elif "narrative" in ep or "video" in ep or "conflict" in ep:
            layers["OPS"].append(ep)
        elif "publish" in ep:
            layers["PUBLISHER"].append(ep)
        elif "report" in ep or "dashboard" in ep:
            layers["REPORTER"].append(ep)
        else:
            layers["SCRIPTS"].append(ep)

    for layer, eps in layers.items():
        if eps:
            print(f"\n#### {layer}")
            for ep in eps:
                print(f"- {ep}")

    # 3. Output locations for Docs Data
    print("\n### 3. Docs Data Output Contract (SSOT)")
    docs_data = project_root / "docs" / "data"
    if docs_data.exists():
        subdirs = [d.name for d in docs_data.iterdir() if d.is_dir()]
        for sd in sorted(subdirs):
            print(f"- docs/data/{sd}/")

if __name__ == "__main__":
    audit_runtime()
