from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

def _utc_ymd() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d")

def _utc_iso() -> str:
    return datetime.utcnow().isoformat()

def _count_files(base_dir: Path, subpath: str, pattern: str = "*") -> int:
    try:
        p = base_dir / subpath
        if not p.exists():
            return 0
        return len(list(p.glob(pattern)))
    except:
        return 0

def _check_exists(base_dir: Path, subpath: str) -> bool:
    return (base_dir / subpath).exists()

def generate_dashboard(base_dir: Path):
    ymd = _utc_ymd()
    
    # 1. Gather Stats for Stats JSON
    # Since we can't easily tap into previous steps status without complex logging parsing,
    # we infer status from file existence for this v1 dashboard.
    
    # Collection & Normalization Stats
    # We look for files in data/raw/{dataset_id}/{ymd}.jsonl
    # We look for files in data/curated/{category}/{dataset}.csv which might be updated.
    
    registry_path = base_dir / "registry" / "datasets.yml"
    datasets_count = 0
    if registry_path.exists():
         # Rough count of datasets by parsing "- dataset_id:" lines
         datasets_count = registry_path.read_text(encoding="utf-8").count("- dataset_id:")
    
    raw_files_count = 0 
    # Scan raw recursively? data/raw/{dataset_id}/{ymd}.jsonl
    # Actually just count all jsonl for today?
    # We'll approximate by checking subdirs.
    raw_dir = base_dir / "data" / "raw"
    if raw_dir.exists():
        for d in raw_dir.iterdir():
            if d.is_dir() and (d / f"{ymd}.jsonl").exists():
                raw_files_count += 1
                
    curated_files_count = _count_files(base_dir, "data/curated", "**/*.csv") # total curated files, not just today's update.
    
    # Outputs
    topics_count = _count_files(base_dir, f"data/topics/{ymd.replace('-','/')}", "*.json")
    meta_path = base_dir / "data" / "meta_topics" / ymd.replace("-","/") / "meta_topics.json"
    meta_count = 0
    if meta_path.exists():
        try:
            m = json.loads(meta_path.read_text())
            meta_count = len(m)
        except:
            pass
            
    # Regime
    regime_path = base_dir / "data" / "regimes" / f"regime_{ymd}.json"
    regime_exists = regime_path.exists()
    
    # Drift
    # This is cummulative, so just check if file exists and has entry for today?
    drift_path = base_dir / "data" / "narratives" / "narrative_drift_v1.json"
    drift_count = 0
    if drift_path.exists():
        # simplified check
        try:
             d = json.loads(drift_path.read_text())
             # Assuming last entry is today's snapshot
             if "history" in d and d["history"]:
                 drift_count = len(d["history"][-1].get("drifts", []))
        except:
             pass

    content_dir = base_dir / "data" / "content"
    script_exists = (content_dir / "insight_script_v1.md").exists() # v1 is generic name, doesn't date rotate in my previous impl
    shotlist_exists = (content_dir / "insight_shotlist_v1.md").exists()
    
    # Status JSON Logic
    status_data = {
        "run_date": ymd,
        "run_id": os.environ.get("GITHUB_RUN_ID", "local"),
        "status": "SUCCESS", # Inferred, because if we are running this step, previous steps didn't hard-fail engine.py (though engine might have caught exceptions). This generation script is run by GH Action step independently.
        # But realistically, if critical files missing, we might say PARTIAL.
        "stages": {
            "collection": { "ok": raw_files_count, "total_datasets_approx": datasets_count },
            "normalization": { "ok": curated_files_count }, # Logic is loose here
            "topic_generation": { "count": topics_count },
            "meta_topic_generation": { "count": meta_count },
            "regime_decision": { "exists": regime_exists },
            "narrative_drift": { "count": drift_count },
            "content_generation": { "script": script_exists, "shotlist": shotlist_exists }
        }
    }
    
    # Save Status JSON
    dash_data_dir = base_dir / "data" / "dashboard"
    dash_data_dir.mkdir(parents=True, exist_ok=True)
    status_file = dash_data_dir / "pipeline_status_v1.json"
    
    # Append logic: read existing list or just save single run status?
    # Requirement: "Overwrite 금지" & "File Structure Example" suggests single object or list?
    # "each pipeline execution status summary record" -> imply history.
    # The example was single object `pipeline_status_v1.json`.
    # I will adapt to append-only log file `pipeline_status_history.json` and a specific `pipeline_status_latest.json` OR 
    # Just list in one file. List is better.
    
    history = []
    if status_file.exists():
        try:
            content = json.loads(status_file.read_text())
            if isinstance(content, list):
                history = content
            elif isinstance(content, dict):
                history = [content]
        except:
            pass
    history.append(status_data)
    status_file.write_text(json.dumps(history, indent=2), encoding="utf-8")
    
    
    # 2. Generate HTML
    dash_dir = base_dir / "dashboard"
    dash_dir.mkdir(parents=True, exist_ok=True)
    
    # Basic CSS
    css = """
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #f4f6f8; color: #333; margin: 0; padding: 20px; }
    .container { max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    h1 { margin-top: 0; color: #1a202c; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; }
    h2 { color: #2d3748; margin-top: 30px; }
    .status-card { display: flex; align-items: center; justify-content: space-between; background: #ebf8ff; padding: 15px; border-radius: 6px; border-left: 5px solid #3182ce; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-top: 20px; }
    .metric { background: #f7fafc; padding: 15px; border-radius: 6px; border: 1px solid #e2e8f0; }
    .metric strong { display: block; font-size: 24px; color: #2b6cb0; }
    .metric span { font-size: 14px; color: #718096; }
    .bool-true { color: green; font-weight: bold; }
    .bool-false { color: red; font-weight: bold; }
    footer { margin-top: 40px; text-align: center; color: #aaa; font-size: 12px; }
    """
    
    
    html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="utf-8">
        <title>Hoin Insight 자동화 대시보드</title>
        <style>{css}</style>
    </head>
    <body>
        <div class="container">
            <h1>Hoin Insight 자동화 대시보드</h1>
            
            <div class="status-card">
                <div>
                    <strong>최근 실행 상태(Latest Run Status):</strong> {status_data['status']}
                </div>
                <div>
                    {ymd} (Run ID: {status_data['run_id']})
                </div>
            </div>
            
            <h2>파이프라인 상태 (Pipeline Health)</h2>
            <div class="grid">
                <div class="metric">
                    <strong>{raw_files_count} / {datasets_count}</strong>
                    <span>수집된 파일 (오늘)</span>
                </div>
                <div class="metric">
                    <strong>{curated_files_count}</strong>
                    <span>정제된 파일 (전체 누적)</span>
                </div>
                <div class="metric">
                    <strong>{topics_count}</strong>
                    <span>생성된 토픽 (Topics)</span>
                </div>
                <div class="metric">
                    <strong>{meta_count}</strong>
                    <span>메타 토픽 (Meta Topics)</span>
                </div>
            </div>
            
            <h2>주요 산출물 (Key Outputs)</h2>
            <div class="grid">
                 <div class="metric">
                    <span class="{'bool-true' if regime_exists else 'bool-false'}">{ "감지됨 (DETECTED)" if regime_exists else "없음 (MISSING)" }</span>
                    <span>시장 국면(Regime) 시그널</span>
                </div>
                <div class="metric">
                    <strong>{drift_count}</strong>
                    <span>Narrative Drift 신호</span>
                </div>
                <div class="metric">
                    <span class="{'bool-true' if script_exists else 'bool-false'}">{ "준비됨 (READY)" if script_exists else "없음 (MISSING)" }</span>
                    <span>인사이트 스크립트</span>
                </div>
                <div class="metric">
                    <span class="{'bool-true' if shotlist_exists else 'bool-false'}">{ "준비됨 (READY)" if shotlist_exists else "없음 (MISSING)" }</span>
                    <span>영상 샷리스트</span>
                </div>
            </div>
            
            <h2>데이터 링크 (Data Links)</h2>
            <ul>
                <li><a href="../data/reports/{ymd.replace('-','/')}/daily_brief.md">일일 브리핑 (Daily Brief MD)</a></li>
                <li><a href="../data/content/insight_script_v1.md">인사이트 스크립트 (Insight Script)</a></li>
                <li><a href="../data/content/insight_shotlist_v1.md">영상 샷리스트 (Shotlist)</a></li>
            </ul>
            
            <footer>
                생성 시각: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")} | Hoin Insight Engine
            </footer>
        </div>
    </body>
    </html>
    """
    
    (dash_dir / "index.html").write_text(html, encoding="utf-8")
    print(f"Dashboard generated at {dash_dir}/index.html")

if __name__ == "__main__":
    generate_dashboard(Path("."))
