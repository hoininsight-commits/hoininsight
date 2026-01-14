from __future__ import annotations

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

def _utc_ymd() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d")

def _count_files(base_dir: Path, subpath: str, pattern: str = "*") -> int:
    try:
        p = base_dir / subpath
        if not p.exists():
            return 0
        return len(list(p.glob(pattern)))
    except:
        return 0

def parse_registry(base_dir: Path) -> List[Dict]:
    """
    Parses registry/datasets.yml to get dataset definitions.
    Since we don't have PyYAML installed in the environment guaranteed for this script 
    (though the engine has it, standard lib is safer if possible, but actually 
    the engine runs in an env where requirements are installed. PyYAML is likely there.
    However, to be robust and single-file, I will use simple text parsing or 
    try import yaml).
    """
    # Try importing yaml, if fails, use regex/manual
    try:
        import yaml
        with open(base_dir / "registry/datasets.yml", "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data.get("datasets", [])
    except ImportError:
        # Fallback manual parsing (fragile but works for this structure)
        # Assuming list of dictionaries
        datasets = []
        current_ds = {}
        content = (base_dir / "registry" / "datasets.yml").read_text(encoding="utf-8")
        for line in content.splitlines():
            line = line.strip()
            if line.startswith("- dataset_id:"):
                # Save previous
                if current_ds:
                    datasets.append(current_ds)
                current_ds = {}
                current_ds["dataset_id"] = line.split(":", 1)[1].strip().strip('"')
            elif line.startswith("category:"):
                current_ds["category"] = line.split(":", 1)[1].strip().strip('"')
            elif line.startswith("curated_path:"):
                current_ds["curated_path"] = line.split(":", 1)[1].strip().strip('"')
            # Add other fields if needed, but simplistic
        if current_ds:
            datasets.append(current_ds)
        return datasets

def check_collection_status(base_dir: Path, dataset: Dict, ymd: str) -> Dict:
    ds_id = dataset.get("dataset_id")
    # Infer category
    category = dataset.get("category")
    if not category:
        cpath = dataset.get("curated_path", "")
        parts = cpath.split("/")
        if len(parts) >= 3:
            category = parts[2].upper() # data/curated/CATEGORY/...
        else:
            category = "UNCATEGORIZED"
            
    raw_path = base_dir / "data" / "raw" / ds_id / f"{ymd}.jsonl"
    
    status = "FAIL"
    reason = "File missing"
    
    if raw_path.exists():
        # Check content for mock
        try:
            # Read first line
            with open(raw_path, "r", encoding="utf-8") as f:
                line = f.readline()
                if line:
                    item = json.loads(line)
                    src = item.get("source", "").lower()
                    if "mock" in src:
                        status = "SKIP"
                        reason = f"Mock data used ({src})"
                    else:
                        status = "OK"
                        reason = "Collected"
                else:
                     status = "FAIL"
                     reason = "Empty file"
        except Exception as e:
            status = "FAIL"
            reason = f"Read error: {str(e)}"
    
    return {
        "dataset_id": ds_id,
        "category": category,
        "status": status,
        "reason": reason,
        "last_updated": ymd
    }

def generate_dashboard(base_dir: Path):
    ymd = _utc_ymd()
    
    # 1. Parse Registry
    datasets = parse_registry(base_dir)
    
    # 2. Check Status for each
    collection_health = {} # Category -> Stats
    
    total_ok = 0
    total_skip = 0
    total_fail = 0
    
    for ds in datasets:
        info = check_collection_status(base_dir, ds, ymd)
        cat = info["category"]
        
        if cat not in collection_health:
            collection_health[cat] = {
                "total_datasets": 0, "collected": 0, "skipped": 0, "failed": 0, "datasets": []
            }
        
        entry = collection_health[cat]
        entry["total_datasets"] += 1
        entry["datasets"].append(info)
        
        s = info["status"]
        if s == "OK":
            entry["collected"] += 1
            total_ok += 1
        elif s == "SKIP":
            entry["skipped"] += 1
            total_skip += 1
        else:
            entry["failed"] += 1
            total_fail += 1

    # 3. Gather Engine Outputs (Existing Logic)
    curated_files_count = _count_files(base_dir, "data/curated", "**/*.csv")
    topics_count = _count_files(base_dir, f"data/topics/{ymd.replace('-','/')}", "*.json")
    
    meta_path = base_dir / "data" / "meta_topics" / ymd.replace("-","/") / "meta_topics.json"
    meta_count = 0
    if meta_path.exists():
        try:
            m = json.loads(meta_path.read_text())
            meta_count = len(m)
        except: pass
            
    regime_path = base_dir / "data" / "regimes" / f"regime_{ymd}.json"
    regime_exists = regime_path.exists()
    
    drift_path = base_dir / "data" / "narratives" / "narrative_drift_v1.json"
    drift_count = 0
    if drift_path.exists():
        try:
             d = json.loads(drift_path.read_text())
             if "history" in d and d["history"]:
                 drift_count = len(d["history"][-1].get("drifts", []))
        except: pass

    content_dir = base_dir / "data" / "content"
    script_exists = (content_dir / "insight_script_v1.md").exists()
    shotlist_exists = (content_dir / "insight_shotlist_v1.md").exists()
    
    # Status JSON Logic
    status_data = {
        "run_date": ymd,
        "run_id": os.environ.get("GITHUB_RUN_ID", "local"),
        "status": "SUCCESS" if total_fail == 0 else "PARTIAL" if total_ok > 0 else "FAIL",
        "collection_status": collection_health,
        "engine_outputs": {
             "curated_files": curated_files_count,
             "topics": topics_count,
             "meta_topics": meta_count,
             "regime_exists": regime_exists,
             "drift_count": drift_count,
             "script": script_exists,
             "shotlist": shotlist_exists
        }
    }
    
    # Save Status JSON
    dash_data_dir = base_dir / "data" / "dashboard"
    dash_data_dir.mkdir(parents=True, exist_ok=True)
    status_file = dash_data_dir / "pipeline_status_v1.json"
    
    history = []
    if status_file.exists():
        try:
            content = json.loads(status_file.read_text())
            if isinstance(content, list):
                history = content
            elif isinstance(content, dict):
                history = [content] # migration
        except: pass
    history.append(status_data)
    status_file.write_text(json.dumps(history, indent=2), encoding="utf-8")
    
    
    # 2. Generate HTML (v2 Redesign)
    dash_dir = base_dir / "dashboard"
    dash_dir.mkdir(parents=True, exist_ok=True)
    
    # CSS
    css = """
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #f4f6f8; color: #333; margin: 0; padding: 20px; }
    .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    h1 { margin-top: 0; color: #1a202c; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; }
    h2 { color: #2d3748; margin-top: 30px; font-size: 1.2em; border-left: 4px solid #3182ce; padding-left: 10px; }
    
    .status-card { display: flex; align-items: center; justify-content: space-between; background: #ebf8ff; padding: 15px; border-radius: 6px; margin-bottom: 20px;}
    
    /* Collection Health Table */
    .health-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 15px; }
    .cat-card { border: 1px solid #e2e8f0; border-radius: 6px; padding: 15px; background: #fff; }
    .cat-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; font-weight: bold; border-bottom: 1px solid #edf2f7; padding-bottom: 5px; }
    
    .dataset-row { display: flex; justify-content: space-between; font-size: 0.9em; padding: 3px 0; border-bottom: 1px dashed #edf2f7; }
    .dataset-row:last-child { border-bottom: none; }
    
    .badge { padding: 2px 6px; border-radius: 4px; font-size: 0.8em; font-weight: bold; }
    .badge-OK { background: #c6f6d5; color: #22543d; }
    .badge-SKIP { background: #edf2f7; color: #4a5568; }
    .badge-FAIL { background: #fed7d7; color: #822727; }
    
    .summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin-top: 10px; }
    .mini-metric { background: #f7fafc; padding: 10px; border-radius: 4px; text-align: center; }
    .mini-metric strong { display: block; font-size: 1.2em; color: #2b6cb0; }
    .mini-metric span { font-size: 0.8em; color: #718096; }
    
    footer { margin-top: 40px; text-align: center; color: #aaa; font-size: 12px; }
    """
    
    # Build Collection HTML
    collection_html = '<div class="health-grid">'
    # Sort categories
    for cat in sorted(collection_health.keys()):
        data = collection_health[cat]
        # Summary for card header
        ok = data["collected"]
        skip = data["skipped"]
        fail = data["failed"]
        total = data["total_datasets"]
        
        # Color coding header
        header_color = "black"
        if fail > 0: header_color = "#e53e3e"; # red
        elif skip > 0 and ok == 0: header_color = "#718096"; # gray
        elif ok == total: header_color = "#38a169"; # green
        
        card = f"""
        <div class="cat-card">
            <div class="cat-header" style="color: {header_color}">
                <span>{cat}</span>
                <span style="font-size: 0.8em">{ok} OK / {skip} SKIP / {fail} FAIL</span>
            </div>
            <div>
        """
        
        for ds in data["datasets"]:
             status = ds["status"]
             badge_class = f"badge-{status}"
             # For SKIP/FAIL, show reason tooltip or text
             extra = ""
             if status != "OK":
                 extra = f" title='{ds['reason']}'"
             
             card += f"""
             <div class="dataset-row" {extra}>
                 <span style="overflow:hidden; text-overflow:ellipsis; white-space:nowrap; max-width: 180px;">{ds['dataset_id']}</span>
                 <span class="badge {badge_class}">{status}</span>
             </div>
             """
        card += "</div></div>"
        collection_html += card
    collection_html += "</div>"
    
    html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="utf-8">
        <title>Hoin Insight 데이터 수집 대시보드</title>
        <style>{css}</style>
    </head>
    <body>
        <div class="container">
            <h1>Hoin Insight 데이터 상태 대시보드 (v2)</h1>
            
            <div class="status-card">
                <div>
                    <strong>실행 일자:</strong> {ymd}
                </div>
                <div>
                    <strong>전체 상태:</strong> {status_data['status']} (Run ID: {status_data['run_id']})
                </div>
            </div>
            
            <h2>데이터 수집 상태 (Data Collection Health)</h2>
            {collection_html}
            
            <h2>엔진 산출물 요약 (Engine Outputs)</h2>
             <div class="summary-grid">
                <div class="mini-metric">
                    <strong>{topics_count}</strong>
                    <span>Topics</span>
                </div>
                <div class="mini-metric">
                    <strong>{meta_count}</strong>
                    <span>Meta Topics</span>
                </div>
                 <div class="mini-metric">
                    <strong>{ "O" if regime_exists else "X" }</strong>
                    <span>Regime</span>
                </div>
                <div class="mini-metric">
                    <strong>{drift_count}</strong>
                    <span>Drifts</span>
                </div>
                <div class="mini-metric">
                    <strong>{ "READY" if script_exists else "-" }</strong>
                    <span>Script</span>
                </div>
            </div>
            
            <footer>
                생성 시각: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")} | Hoin Insight Engine
            </footer>
        </div>
    </body>
    </html>
    """
    
    (dash_dir / "index.html").write_text(html, encoding="utf-8")
    print(f"Data collection health dashboard generated at {dash_dir}/index.html")

if __name__ == "__main__":
    generate_dashboard(Path("."))
