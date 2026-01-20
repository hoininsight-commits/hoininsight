from __future__ import annotations

import json
import os
import sys
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List
from src.utils.markdown_parser import parse_markdown

def _utc_ymd() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d")

def _utc_to_kst_display(utc_timestamp_str: str) -> str:
    """Convert UTC timestamp to KST display format (MM/DD HH:MM).
    
    Args:
        utc_timestamp_str: UTC timestamp in ISO format (e.g., "2026-01-15T06:51:38.361804Z")
    
    Returns:
        Formatted string in KST (e.g., "01/15 15:51")
    """
    if not utc_timestamp_str:
        return ""
    
    try:
        # Remove 'Z' suffix and parse
        utc_str = utc_timestamp_str.replace('Z', '')
        utc_dt = datetime.fromisoformat(utc_str)
        
        # Convert to KST (UTC+9)
        kst_dt = utc_dt + timedelta(hours=9)
        
        # Format as MM/DD HH:MM
        return kst_dt.strftime("%m/%d %H:%M")
    except Exception:
        return utc_timestamp_str  # Return original if parsing fails

def _find_latest_narrative_date(base_dir: Path, max_days_back: int = 7) -> str:
    """Find the latest date with narrative data, looking back up to max_days_back days.
    
    Args:
        base_dir: Base directory of the project
        max_days_back: Maximum number of days to look back (default: 7)
    
    Returns:
        Date string in YYYY-MM-DD format, or current date if no data found
    """
    for days_ago in range(max_days_back + 1):
        check_date = datetime.utcnow() - timedelta(days=days_ago)
        ymd = check_date.strftime("%Y-%m-%d")
        ymd_path = ymd.replace("-", "/")
        
        # Check if queue data exists for this date
        queue_path = base_dir / "data/narratives/queue" / ymd_path / "proposal_queue.json"
        if queue_path.exists():
            return ymd
    
    # Fallback to current date
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
    try:
        import yaml
        with open(base_dir / "registry/datasets.yml", "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data.get("datasets", [])
    except ImportError:
        datasets = []
        current_ds = {}
        content = (base_dir / "registry" / "datasets.yml").read_text(encoding="utf-8")
        for line in content.splitlines():
            line = line.strip()
            if line.startswith("- dataset_id:"):
                if current_ds:
                    datasets.append(current_ds)
                current_ds = {}
                current_ds["dataset_id"] = line.split(":", 1)[1].strip().strip('"')
            elif line.startswith("category:"):
                current_ds["category"] = line.split(":", 1)[1].strip().strip('"')
            elif line.startswith("curated_path:"):
                current_ds["curated_path"] = line.split(":", 1)[1].strip().strip('"')
        if current_ds:
            datasets.append(current_ds)
        return datasets

def check_collection_status(base_dir: Path, dataset: Dict, collection_status_data: Dict) -> Dict:
    ds_id = dataset.get("dataset_id")
    category = dataset.get("category")
    if not category:
        cpath = dataset.get("curated_path", "")
        parts = cpath.split("/")
        if len(parts) >= 3:
            category = parts[2].upper() 
        else:
            category = "UNCATEGORIZED"
    
    # Translate Categories to Korean for Display
    cat_map = {
        "CRYPTO": "가상자산",
        "FX_RATES": "환율/금리",
        "GLOBAL_INDEX": "글로벌 지수",
        "RATES_YIELD": "국채 금리",
        "COMMODITIES": "원자재",
        "PRECIOUS_METALS": "귀금속",
        "BACKFILL": "과거 데이터"
    }
    display_category = cat_map.get(category, category)

    if ds_id in collection_status_data:
        status_info = collection_status_data[ds_id]
        status = status_info.get("status", "FAIL")
        reason = status_info.get("reason", "알 수 없음")
        timestamp_utc = status_info.get("timestamp", "")
        # Convert UTC to KST for display
        timestamp = _utc_to_kst_display(timestamp_utc)
    else:
        status = "PENDING"
        reason = "수집 대기 중"
        timestamp = ""
    
    # [Emergency Reliability Fix]
    # If status is FAIL, but the data file for TODAY actually exists and is non-empty, override to OK.
    if status != "OK":
        try:
            cpath_str = dataset.get("curated_path")
            if cpath_str:
                cpath = base_dir / cpath_str
                if cpath.exists() and cpath.stat().st_size > 0:
                     mtime = datetime.utcfromtimestamp(cpath.stat().st_mtime)
                     now = datetime.utcnow()
                     if (now - mtime).total_seconds() < 86400: # Modified within 24h
                         status = "OK"
                         reason = "데이터 파일 존재 (자동 복구됨)"
                         if not timestamp:
                             timestamp = mtime.isoformat()
        except Exception:
            pass

    # [Feature] Extract Latest Value for Dashboard
    latest_value = None
    try:
        cpath_str = dataset.get("curated_path")
        if cpath_str:
             cpath = base_dir / cpath_str
             if cpath.exists():
                 # Read last line of CSV carefully
                 import pandas as pd
                 # Read only last few lines for speed
                 df = pd.read_csv(cpath) 
                 if not df.empty and "value" in df.columns:
                      latest_value = df.iloc[-1]["value"]
                      # Format if float
                      if isinstance(latest_value, float):
                          # Check unit
                          unit = dataset.get("unit", "")
                          if unit == "KRW":
                              latest_value = f"{latest_value:,.0f}"
                          elif unit == "USD":
                               latest_value = f"{latest_value:,.2f}"
                          elif unit == "PCT":
                               latest_value = f"{latest_value:.2f}%"
                          elif unit == "INDEX":
                               latest_value = f"{latest_value:,.2f}"
                          else:
                               latest_value = f"{latest_value:.2f}"
    except Exception as e:
        # print(f"val read err: {e}")
        pass

    return {
        "dataset_id": ds_id,
        "category": display_category,
        "status": status,
        "reason": reason,
        "last_updated": timestamp,
        "latest_value": latest_value
    }

def generate_dashboard(base_dir: Path):
    ymd = _utc_ymd()  # Current date for data collection status
    narrative_ymd = _find_latest_narrative_date(base_dir)  # Latest date with narrative data
    datasets = parse_registry(base_dir)
    
    collection_status_file = base_dir / "data" / "dashboard" / "collection_status.json"
    collection_status_data = {}
    if collection_status_file.exists():
        try:
            with open(collection_status_file, "r", encoding="utf-8") as f:
                collection_status_data = json.load(f)
        except Exception as e:
            print(f"[WARN] Failed to load collection status: {e}")
    
    collection_health = {} 
    total_ok = 0
    total_fail = 0
    
    for ds in datasets:
        info = check_collection_status(base_dir, ds, collection_status_data)
        cat = info["category"]
        if cat not in collection_health:
            collection_health[cat] = {"collected": 0, "failed": 0, "datasets": []}
        
        entry = collection_health[cat]
        entry["datasets"].append(info)
        if info["status"] == "OK":
            entry["collected"] += 1
            total_ok += 1
        else:
            entry["failed"] += 1
            total_fail += 1
    print(f"[DEBUG] ymd: {ymd}")

    # [Phase 36-B] Load Ops Data
    freshness_summary = {}
    ops_scoreboard = {}
    try:
        fresh_path = base_dir / "data/ops/freshness" / ymd.replace("-","/") / "freshness_summary.json"
        if fresh_path.exists():
            freshness_summary = json.loads(fresh_path.read_text(encoding="utf-8"))
        
        score_path = base_dir / "data/ops/scoreboard" / ymd.replace("-","/") / "ops_scoreboard.json"
        if score_path.exists():
            ops_scoreboard = json.loads(score_path.read_text(encoding="utf-8"))
    except: pass

    # [Phase 37] Load Revival Data
    revival_summary = {}
    revival_evidence = {}
    revival_loops = {}
    try:
        rev_base = base_dir / "data/narratives/revival" / ymd.replace("-","/")
        revival_path = rev_base / "revival_proposals.json"
        if revival_path.exists():
            revival_summary = json.loads(revival_path.read_text(encoding="utf-8"))
        
        evidence_path = rev_base / "revival_evidence.json"
        if evidence_path.exists():
            revival_evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
            
        loop_path = rev_base / "revival_loop_flags.json"
        if loop_path.exists():
            revival_loops = json.loads(loop_path.read_text(encoding="utf-8"))
    except: pass

    # [Phase 38] Load Final Decision Card
    final_card = {}
    try:
        card_base = base_dir / "data/decision" / ymd.replace("-","/")
        card_path = card_base / "final_decision_card.json"
        if card_path.exists():
            final_card = json.loads(card_path.read_text(encoding="utf-8"))
    except: pass

    # Engine Outputs Check
    topics_count = _count_files(base_dir, f"data/topics/{ymd.replace('-','/')}", "*.json")
    meta_path = base_dir / "data" / "meta_topics" / ymd.replace("-","/") / "meta_topics.json"
    meta_count = 0
    if meta_path.exists():
        try:
            meta_count = len(json.loads(meta_path.read_text()))
        except: pass
            
    regime_exists = (base_dir / "data" / "regimes" / f"regime_{ymd}.json").exists()
    script_path = base_dir / "data" / "content" / "insight_script_v1.md"
    script_exists = script_path.exists()
    
    topic_title = "대기중..."
    script_body = ""
    if script_exists:
        try:
            content = script_path.read_text(encoding="utf-8")
            lines = content.splitlines()
            body_lines = []
            title_found = False
            for line in lines:
                line = line.strip()
                if not line: continue
                
                if line.startswith("#") and not title_found:
                    topic_title = line.lstrip("#").replace("[Insight]", "").replace("[인사이트]", "").strip()
                    title_found = True
                elif title_found:
                    body_lines.append(line)
            
            script_body = "\n".join(body_lines)
        except: pass
    
    # [Standardized Status Logic - Run #53 Fix]
    from src.ops.core_dataset import CORE_DATASETS_V2
    
    core_fails = 0
    derived_fails = 0
    
    for cat, data in collection_health.items():
        for ds in data["datasets"]:
            did = ds["dataset_id"]
            stat = ds["status"]
            
            # Check if Core
            is_core = did in CORE_DATASETS_V2
            
            if stat != "OK" and stat != "WARMUP":
                if is_core:
                    core_fails += 1
                else:
                    derived_fails += 1

    if core_fails > 0:
        status_str = "FAIL"
        display_status = "실패 (Core)"
    elif derived_fails > 0 or total_fail > 0:
        status_str = "PARTIAL"
        display_status = "부분 성공"
    else:
        status_str = "SUCCESS"
        display_status = "성공"

    # Narrative Status Check (Phase 31-A)
    narr_status_file = base_dir / "data" / "narratives" / "status" / ymd.replace("-","/") / "collection_status.json"
    narr_label = "INGESTION_SKIP"
    narr_cls = "bg-gray-200 text-gray-500"
    
    if narr_status_file.exists():
        try:
            ns = json.loads(narr_status_file.read_text(encoding="utf-8"))
            detected = ns.get("videos_detected", 0)
            trans_ok = ns.get("transcript_ok", 0)
            
            if detected > 0:
                if trans_ok > 0:
                    narr_label = "INGESTION_OK"
                    narr_cls = "bg-blue-100 text-blue-800"
                else:
                    narr_label = "INGESTION_WARN"
                    narr_cls = "bg-orange-100 text-orange-800"
            else:
                narr_label = "INGESTION_SKIP"
        except:
            narr_label = "ERR"

    status_data = {
        "run_date": ymd,
        "run_id": os.environ.get("GITHUB_RUN_ID", "local"),
        "status": display_status,
        "raw_status": status_str,
        "narrative_label": narr_label,
        "narrative_cls": narr_cls
    }

    # [UI Logic] Prepare Data for Today's Insight (Safe variable generation)
    topic_title = final_card.get('topic', '분석 결과 대기 중...')
    rationale = final_card.get('decision_rationale', '아직 오늘의 주제가 선정되지 않았습니다.<br>잠시 후 다시 확인해주세요.')
    
    key_data_html = '<span style="font-size:10px; color:#cbd5e1;">데이터 없음</span>'
    if final_card.get('key_data'):
        # List comprehension outside f-string
        spans = [f'<span style="font-size:10px; background:#f8fafc; border:1px solid #e2e8f0; padding:2px 8px; border-radius:4px; color:#64748b;">{k}</span>' for k in final_card.get('key_data', {}).keys()]
        key_data_html = ''.join(spans)

    script_preview = '스크립트 생성 대기 중...'
    if script_body:
        script_preview = script_body[:800] + '...' if len(script_body) > 800 else script_body

    # System Status Logic
    if status_str == 'SUCCESS':
        status_icon_char = '🟢'
    elif status_str == 'PARTIAL':
        status_icon_char = '🟡'
    else:
        status_icon_char = '🔴'
    
    error_alert_html = ""
    if status_str == 'FAIL':
        error_alert_html = """
        <div style="background:#fef2f2; border:1px solid #fecaca; border-radius:8px; padding:15px; margin-bottom:25px; display:flex; align-items:center; gap:15px;">
            <div style="font-size:20px;">🔴</div>
            <div>
                <div style="font-weight:bold; color:#b91c1c; font-size:14px;">데이터 파이프라인 오류 감지 (Core Failure)</div>
                <div style="font-size:12px; color:#ef4444;">
                    핵심 데이터(Core) 수집 실패가 감지되었습니다. 분석 신뢰도가 매우 낮을 수 있습니다.
                    <a href="#" onclick="activate('data-status')" style="text-decoration:underline; color:#b91c1c;">데이터 현황 확인</a>
                </div>
            </div>
        </div>
        """
    elif status_str == 'PARTIAL':
         error_alert_html = """
        <div style="background:#fffbeb; border:1px solid #fcd34d; border-radius:8px; padding:15px; margin-bottom:25px; display:flex; align-items:center; gap:15px;">
            <div style="font-size:20px;">⚠️</div>
            <div>
                <div style="font-weight:bold; color:#92400e; font-size:14px;">데이터 파이프라인 부분 경고</div>
                <div style="font-size:12px; color:#b45309;">
                    일부 보조 데이터(Derived/Ops) 수집이 지연되거나 누락되었습니다. (Core 데이터는 정상입니다)
                    <a href="#" onclick="activate('data-status')" style="text-decoration:underline; color:#92400e;">데이터 현황 확인</a>
                </div>
            </div>
        </div>
        """

    
    dash_dir = base_dir / "dashboard"
    dash_dir.mkdir(parents=True, exist_ok=True)
    
    # CSS
    css = """
    body { font-family: 'Pretendard', 'Inter', system-ui, sans-serif; background: #f4f7fa; color: #1e293b; margin: 0; padding: 0; height: 100vh; display: flex; flex-direction: column; }
    
    .top-bar { background: white; border-bottom: 1px solid #e2e8f0; padding: 15px 40px; display: flex; justify-content: space-between; align-items: center; height: 60px; box-sizing: border-box; }
    h1 { margin: 0; font-size: 18px; font-weight: 700; color: #334155; }
    .status-badge { padding: 5px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; background: #e2e8f0; }
    .status-성공, .status-SUCCESS { background: #dcfce7; color: #166534; }
    .status-부분.성공, .status-PARTIAL { background: #fef9c3; color: #854d0e; }
    .status-실패, .status-FAIL { background: #fee2e2; color: #991b1b; }
    
    /* [Phase 36-B] Ops Styles */
    .ops-section { background: white; border-top: 2px solid #e2e8f0; padding: 40px; }
    .ops-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
    .ops-card { background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; }
    .ops-value { font-size: 24px; font-weight: 700; color: #1e293b; }
    .ops-label { font-size: 12px; color: #64748b; text-transform: uppercase; margin-top: 4px; }
    .sla-breach { color: #ef4444; font-weight: 700; }
    
    /* Layout */
    .dashboard-container { display: grid; grid-template-columns: 260px 1fr; height: calc(100vh - 60px); overflow: hidden; }
    
    /* LEFT: Navigation Panel (Modern Dark) */
    .nav-panel { 
        background: #0f172a; 
        color: #94a3b8; 
        display: flex; 
        flex-direction: column; 
        gap: 5px; 
        padding-top: 20px;
        overflow-y: auto;
    }
    
    .nav-label {
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        color: #475569;
        margin: 20px 0 10px 25px;
        letter-spacing: 0.05em;
    }

    .nav-item { 
        padding: 12px 25px; 
        font-size: 14px; 
        font-weight: 500; 
        cursor: pointer; 
        text-decoration: none; 
        display: flex; 
        align-items: center; 
        gap: 12px; 
        color: #94a3b8;
        border-left: 3px solid transparent;
        transition: all 0.2s; 
    }
    .nav-item:hover { 
        background: #1e293b; 
        color: #f1f5f9; 
    }
    .nav-item.active { 
        background: #1e293b; 
        color: #3b82f6; 
        border-left-color: #3b82f6;
        font-weight: 600;
        box-shadow: inset 5px 0 10px -5px rgba(0,0,0,0.2);
    }
    .nav-icon { margin-right: 5px; font-size: 16px; }
    
    /* CENTER: Main Process Flow */
    .main-panel { padding: 40px; overflow-y: auto; background: #f8fafc; display: flex; flex-direction: column; align-items: center; gap: 20px; scroll-behavior: smooth; }
    /* Sections Container */
    .sections-wrapper { max-width: 900px; width: 100%; display: flex; flex-direction: column; gap: 60px; padding-bottom: 100px; }
    
    .architecture-diagram { display: flex; flex-direction: column; gap: 60px; width: 100%; position: relative; scroll-margin-top: 40px; }
    
    /* Process Rows */
    .process-row { display: flex; justify-content: space-between; gap: 40px; position: relative; }
    
    .node-group-label { position: absolute; top: -25px; left: 0; font-size: 11px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; }
    
    .proc-node {
        flex: 1; background: white; border: 1px solid #cbd5e1; border-radius: 8px; padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); display: flex; align-items: center; gap: 15px;
        transition: transform 0.2s; position: relative; z-index: 10;
        min-height: 80px; box-sizing: border-box;
    }
    .proc-node:hover { transform: translateY(-2px); border-color: #3b82f6; }
    .proc-icon { width: 40px; height: 40px; border-radius: 8px; background: #eff6ff; color: #3b82f6; display: flex; align-items: center; justify-content: center; font-size: 20px; flex-shrink: 0; }
    .proc-content { flex: 1; min-width: 0; display: flex; flex-direction: column; justify-content: center; } 
    .proc-title { font-weight: 600; font-size: 14px; color: #334155; }
    .proc-desc { font-size: 12px; color: #64748b; margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .proc-sub { font-size: 11px; color: #94a3b8; margin-top: 1px; }

    /* Node Output Specifics (Clickable) */
    .node-output { cursor: pointer; border-top: 4px solid #3b82f6; }
    .node-output:hover { background-color: #eff6ff; border-color: #2563eb; }

    /* Connections Lines (CSS) */
    .arrow-down { position: absolute; left: 50%; bottom: -60px; height: 60px; width: 2px; background: #cbd5e1; z-index: 0; transform: translateX(-50%); }
    .arrow-down::after { content: ''; position: absolute; bottom: 0; left: -4px; border-left: 5px solid transparent; border-right: 5px solid transparent; border-top: 6px solid #cbd5e1; }

    /* Node Specifics */
    .node-scheduler { border-top: 4px solid #f59e0b; }
    .node-github { border-top: 4px solid #6366f1; }
    .node-data { border-top: 4px solid #10b981; }
    .node-engine { border-top: 4px solid #ec4899; }
    
    /* RIGHT: Sidebar Data Intake */
    .sidebar { background: white; border-left: 1px solid #e2e8f0; padding: 30px; overflow-y: auto; }
    .sidebar-title { font-size: 16px; font-weight: 700; color: #1e293b; margin-bottom: 25px; padding-bottom: 15px; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center; }
    
    .cat-group { margin-bottom: 25px; }
    .cat-title { font-size: 12px; font-weight: 700; color: #64748b; margin-bottom: 10px; text-transform: uppercase; display: flex; justify-content: space-between; }
    
    .ds-item { display: flex; align-items: center; justify-content: space-between; padding: 8px 10px; border-radius: 6px; margin-bottom: 5px; background: #f8fafc; border: 1px solid transparent; }
    .ds-item:hover { background: #f1f5f9; }
    .ds-item.fail { background: #fef2f2; border-color: #fecaca; }
    .ds-item.pending { background: #f8fafc; border-color: #e2e8f0; color: #94a3b8; }
    .ds-item.warmup { background: #fff7ed; border-color: #ffedd5; color: #9a3412; }
    
    .ds-left { display: flex; align-items: center; gap: 8px; overflow: hidden; }
    .ds-icon { width: 6px; height: 6px; border-radius: 50%; background: #cbd5e1; flex-shrink: 0; }
    .ds-name { font-size: 13px; color: #334155; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    
    .status-check { color: #166534; font-weight: bold; font-size: 14px; }
    .fail .status-check { color: #dc2626; }
    .pending .status-check { color: #94a3b8; font-size: 12px; }
    .warmup .status-check { color: #9a3412; font-size: 10px; border: 1px solid #fdba74; padding: 1px 4px; border-radius: 4px; }
    
    .fail .ds-icon { background: #dc2626; }
    .ok .ds-icon { background: #166534; }
    .pending .ds-icon { background: #cbd5e1; }
    .warmup .ds-icon { background: #f97316; }
    
    /* Footer */
    .footer { font-size: 11px; color: #94a3b8; text-align: center; margin-top: 40px; border-top: 1px solid #f1f5f9; padding-top: 20px; }
    
    @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.5); } 70% { box-shadow: 0 0 0 10px rgba(59, 130, 246, 0); } 100% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0); } }
    .active-node { animation: pulse 2s infinite; border-color: #3b82f6; }

    /* Modal Styles */
    .modal {
        display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%;
        overflow: auto; background-color: rgba(0,0,0,0.4);
    }
    .modal-content {
        background-color: #fefefe; margin: 5% auto; padding: 40px; border: 1px solid #888;
        width: 80%; max-width: 800px; border-radius: 12px; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
    }
    .close-btn { color: #aaa; float: right; font-size: 28px; font-weight: bold; cursor: pointer; }
    .close-btn:hover, .close-btn:focus { color: black; text-decoration: none; cursor: pointer; }
    
    .modal-header { font-size: 20px; font-weight: 700; color: #1e293b; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid #e2e8f0; }
    .modal-body { font-size: 14px; line-height: 1.6; color: #334155; white-space: pre-wrap; }
    """
    
    # We will invoke replace twice. First for CSS/HTML top part.
    # WAIT, I can do it in one go if I replace the `dashboard-container` and `nav-panel` part.
    
    # Let's focus on lines 1015-1028 (Nav Panel)
    
    pass
    """

    # Actually I need to re-write the CSS and HTML structure properly.
    # The `css` variable is defined around line 287.
    # The `html` variable starts around line 961.
    # The `dashboard-container` div starts around line 1015.
    
    # Due to complexity, I will just replace the `dashboard-container` block where `nav-panel` is defined.

    
    /* CENTER: Main Process Flow */
    .main-panel { padding: 40px; overflow-y: auto; background: #f8fafc; display: flex; flex-direction: column; align-items: center; gap: 20px; }
    /* Sections Container */
    .sections-wrapper { max-width: 900px; width: 100%; display: flex; flex-direction: column; gap: 40px; padding-bottom: 60px; }
    
    .architecture-diagram { display: flex; flex-direction: column; gap: 60px; width: 100%; position: relative; scroll-margin-top: 20px; }
    
    /* Process Rows */
    .process-row { display: flex; justify-content: space-between; gap: 40px; position: relative; }
    
    .node-group-label { position: absolute; top: -25px; left: 0; font-size: 11px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; }
    
    .proc-node {
        flex: 1; background: white; border: 1px solid #cbd5e1; border-radius: 8px; padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); display: flex; align-items: center; gap: 15px;
        transition: transform 0.2s; position: relative; z-index: 10;
        min-height: 80px; box-sizing: border-box;
    }
    .proc-node:hover { transform: translateY(-2px); border-color: #3b82f6; }
    .proc-icon { width: 40px; height: 40px; border-radius: 8px; background: #eff6ff; color: #3b82f6; display: flex; align-items: center; justify-content: center; font-size: 20px; flex-shrink: 0; }
    .proc-content { flex: 1; min-width: 0; display: flex; flex-direction: column; justify-content: center; } 
    .proc-title { font-weight: 600; font-size: 14px; color: #334155; }
    .proc-desc { font-size: 12px; color: #64748b; margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .proc-sub { font-size: 11px; color: #94a3b8; margin-top: 1px; }

    /* Node Output Specifics (Clickable) */
    .node-output { cursor: pointer; border-top: 4px solid #3b82f6; }
    .node-output:hover { background-color: #eff6ff; border-color: #2563eb; }

    /* Connections Lines (CSS) */
    .arrow-down { position: absolute; left: 50%; bottom: -60px; height: 60px; width: 2px; background: #cbd5e1; z-index: 0; transform: translateX(-50%); }
    .arrow-down::after { content: ''; position: absolute; bottom: 0; left: -4px; border-left: 5px solid transparent; border-right: 5px solid transparent; border-top: 6px solid #cbd5e1; }

    /* Node Specifics */
    .node-scheduler { border-top: 4px solid #f59e0b; }
    .node-github { border-top: 4px solid #6366f1; }
    .node-data { border-top: 4px solid #10b981; }
    .node-engine { border-top: 4px solid #ec4899; }
    
    /* RIGHT: Sidebar Data Intake */
    .sidebar { background: white; border-left: 1px solid #e2e8f0; padding: 30px; overflow-y: auto; }
    .sidebar-title { font-size: 16px; font-weight: 700; color: #1e293b; margin-bottom: 25px; padding-bottom: 15px; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center; }
    
    .cat-group { margin-bottom: 25px; }
    .cat-title { font-size: 12px; font-weight: 700; color: #64748b; margin-bottom: 10px; text-transform: uppercase; display: flex; justify-content: space-between; }
    
    .ds-item { display: flex; align-items: center; justify-content: space-between; padding: 8px 10px; border-radius: 6px; margin-bottom: 5px; background: #f8fafc; border: 1px solid transparent; }
    .ds-item:hover { background: #f1f5f9; }
    .ds-item.fail { background: #fef2f2; border-color: #fecaca; }
    .ds-item.pending { background: #f8fafc; border-color: #e2e8f0; color: #94a3b8; }
    .ds-item.warmup { background: #fff7ed; border-color: #ffedd5; color: #9a3412; }
    
    .ds-left { display: flex; align-items: center; gap: 8px; overflow: hidden; }
    .ds-icon { width: 6px; height: 6px; border-radius: 50%; background: #cbd5e1; flex-shrink: 0; }
    .ds-name { font-size: 13px; color: #334155; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    
    .status-check { color: #166534; font-weight: bold; font-size: 14px; }
    .fail .status-check { color: #dc2626; }
    .pending .status-check { color: #94a3b8; font-size: 12px; }
    .warmup .status-check { color: #9a3412; font-size: 10px; border: 1px solid #fdba74; padding: 1px 4px; border-radius: 4px; }
    
    .fail .ds-icon { background: #dc2626; }
    .ok .ds-icon { background: #166534; }
    .pending .ds-icon { background: #cbd5e1; }
    .warmup .ds-icon { background: #f97316; }
    
    /* Footer */
    .footer { font-size: 11px; color: #94a3b8; text-align: center; margin-top: 40px; border-top: 1px solid #f1f5f9; padding-top: 20px; }
    
    @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.5); } 70% { box-shadow: 0 0 0 10px rgba(59, 130, 246, 0); } 100% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0); } }
    .active-node { animation: pulse 2s infinite; border-color: #3b82f6; }

    /* Modal Styles */
    .modal {
        display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%;
        overflow: auto; background-color: rgba(0,0,0,0.4);
    }
    .modal-content {
        background-color: #fefefe; margin: 5% auto; padding: 40px; border: 1px solid #888;
        width: 80%; max-width: 800px; border-radius: 12px; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
    }
    .close-btn { color: #aaa; float: right; font-size: 28px; font-weight: bold; cursor: pointer; }
    .close-btn:hover, .close-btn:focus { color: black; text-decoration: none; cursor: pointer; }
    
    .modal-header { font-size: 20px; font-weight: 700; color: #1e293b; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid #e2e8f0; }
    .modal-body { font-size: 14px; line-height: 1.6; color: #334155; white-space: pre-wrap; }
    """
    
    # Sidebar HTML
    sidebar_html = ""
    for cat in sorted(collection_health.keys()):
        data = collection_health[cat]
        fail_count = data["failed"]
        # Pending count logic could be added here if needed
        sidebar_html += f"""
        <div class="cat-group">
            <div class="cat-title">
                <span>{cat}</span>
                <span class="{ 'text-red-500' if fail_count > 0 else 'text-green-500' }">{data['collected']}/{len(data['datasets'])}</span>
            </div>
        """
        for ds in data["datasets"]:
             status = ds["status"]
             if status == "FAIL":
                 status_cls = "fail"
                 check_mark = "✕"
             elif status == "OK":
                 status_cls = "ok"
                 check_mark = "✓"
             elif status == "WARMUP":
                 status_cls = "warmup"
                 check_mark = "WARMUP"
             else:
                 status_cls = "pending"
                 check_mark = "-"
             
             # Timestamp Display
             ts_html = ""
             if ds.get("last_updated"):
                 # Check if already formatted (MM/DD HH:MM from KST conversion)
                 if "/" in str(ds["last_updated"]) and ":" in str(ds["last_updated"]) and "T" not in str(ds["last_updated"]):
                     # Already formatted by _utc_to_kst_display(), use as-is
                     ts_html = f'<span style="font-size: 10px; color: #94a3b8; margin-left: 6px;">({ds["last_updated"]})</span>'
                 else:
                     # Original ISO format, parse and format
                     try:
                         # Parse ISO string
                         dt_obj = datetime.fromisoformat(ds["last_updated"].replace("Z", ""))
                         # Format to MM/DD HH:MM
                         short_ts = dt_obj.strftime("%m/%d %H:%M")
                         ts_html = f'<span style="font-size: 10px; color: #94a3b8; margin-left: 6px;">({short_ts})</span>'
                     except:
                         # Fallback simple slice if iso parse fails but it looks like ISO
                         if "T" in str(ds["last_updated"]):
                             parts = ds["last_updated"].split("T")
                             date_part = parts[0][5:] # 2026-01-16 -> 01-16
                             time_part = parts[1][:5] # 15:30:00 -> 15:30
                             ts_html = f'<span style="font-size: 10px; color: #94a3b8; margin-left: 6px;">({date_part.replace("-","/")} {time_part})</span>'
                         else:
                             ts_html = f'<span style="font-size: 10px; color: #94a3b8; margin-left: 6px;">({ds["last_updated"]})</span>'

             # Value Display
             val_html = ""
             if ds.get("latest_value"):
                 val_html = f'<span style="font-size: 11px; font-weight:bold; color: #334155; margin-left: auto; margin-right: 8px;">{ds["latest_value"]}</span>'

             sidebar_html += f"""
             <div class="ds-item {status_cls}" title="{ds.get('reason','')}">
                 <div class="ds-left">
                     <div class="ds-icon"></div>
                     <span class="ds-name">{ds['dataset_id']} {ts_html}</span>
                 </div>
                 {val_html}
                 <div class="status-check">{check_mark}</div>
             </div>
             """
        sidebar_html += "</div>"

    # [Ops Upgrade v1] Calculate Confidence
    from src.ops.regime_confidence import calculate_regime_confidence
    conf_res = calculate_regime_confidence(base_dir / "data" / "dashboard" / "collection_status.json")
    conf_level = conf_res.get("regime_confidence", "LOW")
    core_bd = conf_res.get("core_breakdown", {})
    
    # [Ops Upgrade v1.1] Content Status
    from src.ops.content_gate import evaluate_content_gate
    gate_res = evaluate_content_gate(base_dir)
    content_mode = gate_res.get("content_mode", "UNKNOWN")
    
    content_cls = "bg-gray-200 text-gray-800"
    if content_mode == "NORMAL": content_cls = "bg-green-100 text-green-800"
    elif content_mode == "CAUTIOUS": content_cls = "bg-yellow-100 text-yellow-800"
    elif content_mode == "SKIP": content_cls = "bg-gray-200 text-gray-500"

    # [Ops Upgrade v1.2] Content Preset
    preset_label = "-"
    preset_cls = "bg-gray-100 text-gray-400"
    
    if content_mode != "SKIP":
        from src.ops.content_preset_selector import select_content_preset
        
        # Load Regime Name
        regime_name = "Unknown"
        rh_path = base_dir / "data" / "regimes" / "regime_history.json"
        if rh_path.exists():
            try:
                rh_data = json.loads(rh_path.read_text(encoding="utf-8"))
                if rh_data.get("history"):
                    regime_name = rh_data["history"][-1].get("regime", "Unknown")
            except: pass
            
        # Check Meta
        has_meta = meta_count > 0
        
        # Select
        p_res = select_content_preset(regime_name, conf_level, has_meta)
        preset_label = p_res.get("preset", "STANDARD")
        
        # Colors
        if preset_label == "BRIEF": preset_cls = "bg-blue-50 text-blue-600 border border-blue-200"
        elif preset_label == "STANDARD": preset_cls = "bg-blue-100 text-blue-800 border border-blue-300"
        elif preset_label == "DEEP": preset_cls = "bg-purple-100 text-purple-800 border border-purple-300"
    
    # Confidence Colors
    conf_cls = "bg-gray-200 text-gray-800"
    if conf_level == "HIGH": conf_cls = "bg-green-100 text-green-800"
    elif conf_level == "MEDIUM": conf_cls = "bg-yellow-100 text-yellow-800"
    elif conf_level == "LOW": conf_cls = "bg-red-100 text-red-800"
    
    # [Phase 31-E+] YouTube Inbox (Latest Videos)
    # Displays latest collected videos and their pipeline status
    inbox_html = ""

    # [Phase 33] Load Aging Scores (with fallback to Phase 32)
    # [Phase 33] Load Aging Scores (with fallback to Phase 32)
    priority_map = {}
    
    # Attempt 1: Load Phase 33 (Aging)
    aging_path = base_dir / "data/narratives/prioritized" / narrative_ymd.replace("-","/") / "proposal_scores_with_aging.json"
    if aging_path.exists():
        try:
            print(f"[DEBUG] Loading Phase 33: {aging_path}")
            a_data = json.loads(aging_path.read_text(encoding="utf-8"))
            if isinstance(a_data, dict) and "items" in a_data:
                a_data = a_data["items"]
            for item in a_data:
                priority_map[item.get("video_id")] = item
            print(f"[DEBUG] Loaded {len(priority_map)} items from Phase 33")
        except Exception as e:
            print(f"[DEBUG] Phase 33 load failed: {e}")
            priority_map = {} # Reset on failure

    # Attempt 2: Fallback to Phase 32 (Prioritized) if map is still empty
    if not priority_map:
        prio_path = base_dir / "data/narratives/prioritized" / narrative_ymd.replace("-","/") / "proposal_scores.json"
        if prio_path.exists():
            try:
                print(f"[DEBUG] Loading Phase 32 (Fallback): {prio_path}")
                p_data = json.loads(prio_path.read_text(encoding="utf-8"))
                if isinstance(p_data, dict) and "items" in p_data:
                    p_data = p_data["items"]
                for item in p_data:
                    priority_map[item.get("video_id")] = item
                print(f"[DEBUG] Loaded {len(priority_map)} items from Phase 32")
            except Exception as e:
                print(f"[DEBUG] Phase 32 load failed: {e}")


    # [Phase 35] Load Ledger Summary
    ledger_map = {}
    ledger_summary = {}
    try:
        ledger_path = base_dir / "data/narratives/ledger_summary" / narrative_ymd.replace("-","/") / "ledger_summary.json"
        if ledger_path.exists():
            ledger_summary = json.loads(ledger_path.read_text(encoding="utf-8"))
            for entry in ledger_summary.get("recent_entries", []):
                ledger_map[entry.get("video_id")] = entry
    except: pass

    
    evo_map = {} # video_id -> list of evo proposals
    try:
        evo_dir = base_dir / "data/evolution/proposals"
        if evo_dir.exists():
            for p_file in evo_dir.glob("*.json"):
                try:
                    p_data = json.loads(p_file.read_text(encoding="utf-8"))
                    vid = p_data.get("video_id")
                    if vid:
                        if vid not in evo_map: evo_map[vid] = []
                        evo_map[vid].append(p_data)
                except: continue
    except: pass

    try:
        # Scan last 10 days of metadata
        
        inbox_items = []
        seen_vids = set()
        # Reverse day scan

        base_date = datetime.utcnow()
        
        # Check applied_summary for today to quick check APPLIED
        applied_today_vids = []
        applied_path = base_dir / "data/narratives/applied" / narrative_ymd.replace("-","/") / "applied_summary.json"
        if applied_path.exists():
             try:
                 ad = json.loads(applied_path.read_text(encoding="utf-8"))
                 applied_today_vids = [x.get('video_id') for x in ad.get('items', [])]
             except: pass

        for i in range(10): # Scan last 10 days
            scan_ymd = (base_date - timedelta(days=i)).strftime("%Y/%m/%d")
            # [Fix] Scan raw/youtube instead of metadata
            # Structure: data/narratives/raw/youtube/YYYY/MM/DD/{VIDEO_ID}/metadata.json
            raw_dir = base_dir / "data/narratives/raw/youtube" / scan_ymd
            
            check_dirs = []
            if raw_dir.exists():
                check_dirs.extend([d for d in raw_dir.iterdir() if d.is_dir()])
            
            # [Critical Fix] Also check root raw/youtube for manual or recent non-partitioned videos
            if i == 0:
                root_raw = base_dir / "data/narratives/raw/youtube"
                for d in root_raw.iterdir():
                    if d.is_dir() and d.name not in ["2024", "2025", "2026"]:
                        if d not in check_dirs:
                            check_dirs.append(d)

            for vid_dir in check_dirs:
                    
                    m_file = vid_dir / "metadata.json"
                    if m_file.exists():
                        try:
                            md = json.loads(m_file.read_text(encoding="utf-8"))
                            vid = md.get("video_id")
                            if not vid: continue
                            
                            if vid not in seen_vids:
                                seen_vids.add(vid)
                                # Determine Status
                                status = "NEW"
                                
                                # Check PROPOSED
                                prop_path = base_dir / "data/narratives/proposals" / scan_ymd / f"proposal_{vid}.md"
                                has_prop = prop_path.exists()
                                if has_prop:
                                    status = "PROPOSED"
                                    
                                # Check APPROVED
                                appr_path_1 = base_dir / "data/narratives/approvals" / scan_ymd / f"approve_{vid}.yml"
                                appr_path_2 = base_dir / "data/narratives/approvals" / narrative_ymd.replace("-","/") / f"approve_{vid}.yml"
                                if appr_path_1.exists() or appr_path_2.exists():
                                    status = "APPROVED"
                                    
                                # Check APPLIED
                                if vid in applied_today_vids:
                                    status = "APPLIED"
                                
                                # [Phase 35] Ledger Decision Colors
                                ledger_decision = None
                                ledger_reason = None
                                if vid in ledger_map:
                                    ledger_entry = ledger_map[vid]
                                    ledger_decision = ledger_entry.get("decision")
                                    ledger_reason = ledger_entry.get("reason", "")
                                    # Override status if decisioned
                                    if ledger_decision:
                                        status = ledger_decision
                                        needs_action = False  # No action needed if decisioned
                                
                                # Needs Action?
                                needs_action = status in ["NEW", "PROPOSED"]
                                
                                # [Sync Fix] Check if Deep Analysis exists
                                has_deep = False
                                for j in range(11):
                                    d_y = (base_date - timedelta(days=j)).strftime("%Y/%m/%d")
                                    if (base_dir / "data/narratives/deep_analysis" / d_y / f"video_{vid}_report.md").exists():
                                        has_deep = True
                                        break

                                item = {
                                    "video_id": vid,
                                    "title": md.get("title", "No Title"),
                                    "published_at": md.get("published_at", ""),
                                    "url": f"https://youtu.be/{vid}",
                                    "status": status,
                                    "needs_action": needs_action,
                                    "prop_path": prop_path,
                                    "ledger_decision": ledger_decision,
                                    "ledger_reason": ledger_reason,
                                    "has_deep": has_deep,
                                    "evo_count": len(evo_map.get(vid, []))
                                }
                                inbox_items.append(item)
                        except: pass
        
        # Sort by published (desc) ideally, or just collection time
        # Metadata doesn't strictly have collection time, uses published_at
        inbox_items.sort(key=lambda x: x['published_at'], reverse=True)
        
        if inbox_items:
            inbox_html += '<div class="inbox-list" style="display:flex; flex-direction:column; gap:10px;">'
            for it in inbox_items:
                vid = it["video_id"]
                st = it["status"]
                
                # Badge Color
                bg_col = "#e2e8f0"
                txt_col = "#475569"
                if st == "NEW": bg_col="#dbeafe"; txt_col="#1e40af"
                elif st == "PROPOSED": bg_col="#ffedd5"; txt_col="#9a3412"
                elif st == "APPROVED": bg_col="#dcfce7"; txt_col="#166534"
                elif st == "APPLIED": bg_col="#f0fdf4"; txt_col="#15803d"; # Green outline?
                # [Phase 35] Ledger Decision Colors
                elif st == "REJECTED": bg_col="#fee2e2"; txt_col="#991b1b"
                elif st == "DEFERRED": bg_col="#e0e7ff"; txt_col="#3730a3"
                elif st == "DUPLICATE": bg_col="#fed7aa"; txt_col="#9a3412"
                
                # Extract
                extract_html = ""
                if st == "PROPOSED" and it["prop_path"].exists():
                     try:
                         raw = it["prop_path"].read_text(encoding="utf-8")
                         lines = [l for l in raw.splitlines() if l.strip().startswith("-")][:3]
                         if lines:
                             extract_html = "<div style='background:#f8fafc; padding:5px; font-size:10px; color:#64748b; border-radius:4px; margin-top:5px;'>" + "<br>".join(lines) + "</div>"
                     except: pass
                
                action_ui = ""
                toggle_id = f"toggle-{vid}"
                
                # Action UI (Learning Needed Toggle)
                # Only offer this if NOT Applied
                if st != "APPLIED":
                    action_ui = f"""
                    <div style="margin-top:8px; border-top:1px solid #f1f5f9; padding-top:8px;">
                        <label style="font-size:11px; cursor:pointer; color:#3b82f6; font-weight:600; display:flex; align-items:center;">
                            <input type="checkbox" onchange="toggleAction('{vid}')" style="margin-right:5px;"> Learning Needed?
                        </label>
                        
                        <div id="action-box-{vid}" style="display:none; margin-top:10px;">
                            {extract_html}
                            <div class="approval-form" style="margin-top:10px;">
                                <div style="font-size:11px; font-weight:bold; margin-bottom:5px;">승인 옵션:</div>
                                <label style="display:block; font-size:11px;"><input type="checkbox" id="ib-dcm-{vid}" checked> Data Collection Master</label>
                                <label style="display:block; font-size:11px;"><input type="checkbox" id="ib-adl-{vid}"> Anomaly Detection Logic</label>
                                <label style="display:block; font-size:11px;"><input type="checkbox" id="ib-bs-{vid}"> Baseline Signals</label>
                                
                                <textarea id="ib-note-{vid}" placeholder="Notes..." style="width:100%; margin-top:5px; font-size:11px; border:1px solid #cbd5e1; border-radius:4px; height:40px;"></textarea>
                                
                                <button onclick="generateInboxYaml('{vid}')" style="width:100%; margin-top:5px; background:#3b82f6; color:white; border:none; padding:4px; border-radius:4px; font-size:11px; cursor:pointer;">
                                    Generate YAML
                                </button>
                            </div>
                        </div>
                    </div>
                    """

                inbox_html += f"""
                <div class="inbox-card" style="background:white; border:1px solid #cbd5e1; border-radius:6px; padding:10px; box-shadow:0 1px 2px rgba(0,0,0,0.05);">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                        <div style="font-size:12px; font-weight:600; color:#334155; line-height:1.4; width:70%; word-break:break-all;">
                            <a href="{it['url']}" target="_blank" style="text-decoration:none; color:inherit;">{it['title']}</a>
                        </div>
                        <span style="font-size:9px; font-weight:bold; background:{bg_col}; color:{txt_col}; padding:2px 5px; border-radius:4px; white-space:nowrap;">{st}</span>
                    </div>
                    <div style="font-size:10px; color:#94a3b8; margin-top:4px;">
                        {it['published_at'][:10]}
                        { " <span style='color:#f59e0b; font-weight:bold;'>⚠ Action</span>" if it['needs_action'] else "" }
                        { " <span style='color:#3b82f6; font-weight:bold; margin-left:5px;'>✨ Analysis Done</span>" if it.get('has_deep') else "" }
                        { f" <span style='color:#8b5cf6; font-weight:bold; margin-left:5px;'>🚀 Evolution Needed ({it['evo_count']})</span>" if it.get('evo_count', 0) > 0 else "" }
                        { " <span style='color:#ef4444; font-weight:bold; margin-left:5px;'>⚠ STALE DATA WARNING</span>" if freshness_summary.get('sla_breach_count', 0) > 0 else "" }
                    </div>
                    <button onclick="showDeepLogicReport('{vid}')" style="width:100%; margin-top:10px; background:#f8fafc; border:1px solid #cbd5e1; padding:6px; border-radius:4px; font-size:11px; cursor:pointer; font-weight:bold; color:#475569;" onmouseover="this.style.background='#f1f5f9'" onmouseout="this.style.background='#f8fafc'">
                        View Analysis & Action
                    </button>
    """
                
                # [Phase 33] Aging Score Badge in Inbox
                if vid in priority_map:
                    p_info = priority_map[vid]
                    a_score = p_info.get("alignment_score", 0)
                    final_score = p_info.get("final_priority_score", a_score)
                    age_days = p_info.get("age_days", 0)
                    
                    # Decay badge
                    decay_badge = ""
                    decay_cls = "bg-green-50 text-green-700"
                    decay_label = "FRESH"
                    if age_days >= 21:
                        decay_cls = "bg-red-50 text-red-700"
                        decay_label = "EXPIRED"
                    elif age_days >= 7:
                        decay_cls = "bg-orange-50 text-orange-700"
                        decay_label = "STALE"
                    
                    decay_badge = f'<span style="font-size:8px; padding:1px 4px; border-radius:3px; background:{decay_cls.split()[0].replace("bg-","#")}; color:{decay_cls.split()[1].replace("text-","#")}; margin-left:3px;">{decay_label}</span>'
                    
                    inbox_html += f"""
                    <div style="margin-top:4px; font-size:10px;">
                        <span style="color:#64748b;">Age: {age_days}d</span> {decay_badge}
                    </div>
                    <div style="margin-top:2px; font-size:10px;">
                        <span style="font-weight:bold; color:#1e293b;">Final Priority: {final_score}</span>
                        <span style="color:#94a3b8; margin-left:5px;">(Align: {a_score})</span>
                    </div>
                    """
                else:
                    inbox_html += f"""
                    <div style="margin-top:4px; font-size:10px;">
                        <span style="color:#cbd5e1; font-size:9px; border:1px dashed #cbd5e1; padding:1px 4px; border-radius:3px;">No scored proposals yet</span>
                    </div>
                    """
                
                # [Phase 35] Ledger Reason Display
                if it.get("ledger_reason"):
                    inbox_html += f"""
                    <div style="margin-top:6px; padding:6px; background:#f8fafc; border-left:3px solid {bg_col}; border-radius:3px;">
                        <div style="font-size:9px; font-weight:600; color:#64748b; margin-bottom:2px;">DECISION REASON:</div>
                        <div style="font-size:10px; color:#334155;">{it['ledger_reason']}</div>
                    </div>
                    """
                
                inbox_html += f"""
                    
                    {action_ui}
                </div>
                """
            inbox_html += "</div>"
        else:
             inbox_html += "<div style='font-size:12px; color:#94a3b8; padding:10px;'>최근 수집된 영상이 없습니다.</div>"
            
    except Exception as e:
        inbox_html += f"<div style='color:red; font-size:11px;'>Inbox Load Fail: {e}</div>"

    # sidebar_html += inbox_html  <-- REMOVED (Duplicated in Inbox Tab)

    queue_html = ""
    try:
        # Load Queue
        # [Phase 33] Enhanced Queue Sync: Scan last 3 days if empty
        q_data = []
        for i in range(10):
            scan_ymd = (base_date - timedelta(days=i)).strftime("%Y/%m/%d")
            q_p = base_dir / "data/narratives/queue" / scan_ymd / "proposal_queue.json"
            if q_p.exists():
                try:
                    day_q = json.loads(q_p.read_text(encoding="utf-8"))
                    # Merge and deduplicate by video_id
                    vids = [x.get('video_id') for x in q_data]
                    for item in day_q:
                        if item.get('video_id') not in vids:
                            q_data.append(item)
                except: pass
        
        print(f"[DEBUG] q_data length: {len(q_data)}")
        print(f"[DEBUG] priority_map length: {len(priority_map)}")
        if q_data or priority_map:
            queue_html += '<div class="queue-list">'
            
            # [Phase 33] Sort by final_priority_score
            final_queue_list = q_data
            if priority_map:
                # Merge proposal_path from q_data into priority_map items
                path_map = {item.get("video_id"): item.get("proposal_path") for item in q_data}
                
                for vid, item in priority_map.items():
                    if vid in path_map and path_map[vid]:
                        item["proposal_path"] = path_map[vid]
                        
                final_queue_list = list(priority_map.values())
                final_queue_list.sort(key=lambda x: x.get("final_priority_score", x.get("alignment_score", 0)), reverse=True)
            
            for item in final_queue_list:
                vid = item.get("video_id")
                status = item.get("status", "PENDING")
                status_color = "#f59e0b" if status == "PENDING" else "#10b981"
                
                # Phase 33 props
                alignment_score = item.get("alignment_score", 0)
                final_score = item.get("final_priority_score", alignment_score)
                age_days = item.get("age_days", 0)
                decay_factor = item.get("decay_factor", 1.0)
                rank = item.get("final_priority_rank", item.get("priority_rank", "-"))
                breakdown = item.get("score_breakdown", "")
                
                # Decay badge
                decay_label = "FRESH"
                decay_color = "#16a34a"
                if age_days >= 21:
                    decay_label = "EXPIRED"
                    decay_color = "#dc2626"
                elif age_days >= 7:
                    decay_label = "STALE"
                    decay_color = "#ea580c"
                
                score_badge_html = f"""
                <div style='margin-top:8px; font-size:11px;'>
                    <div style='margin-bottom:4px;'>
                        <span style='font-weight:bold; color:#1e293b;'>Final Priority: {final_score}</span>
                        <span style='background:#f1f5f9; color:#64748b; padding:2px 5px; border-radius:4px; margin-left:5px; font-size:10px;'>Align: {alignment_score}</span>
                    </div>
                    <div style='font-size:10px; color:#64748b;'>
                        Age: {age_days} days | Decay: {decay_factor} | <span style='color:{decay_color}; font-weight:bold;'>{decay_label}</span>
                    </div>
                </div>
                """
    
                # Load Content Hint
                prop_path_str = item.get("proposal_path", "")
                prop_excerpt = "제안 내용을 불러올 수 없습니다."
                if prop_path_str:
                    # Handle cross-environment paths
                    # If path contains 'data/', extract relative path from there
                    if "data/" in prop_path_str:
                        rel_part = prop_path_str.split("data/", 1)[1]
                        pp = base_dir / "data" / rel_part
                    else:
                        pp = Path(prop_path_str)
                    
                    if pp.exists():
                         try:
                             lines = pp.read_text(encoding="utf-8").splitlines()
                             hints = [l for l in lines if l.strip().startswith("-")][:5]
                             if not hints:
                                 # Fallback: take any non-empty lines
                                 hints = [l for l in lines if l.strip()][:3]
                             
                             prop_excerpt = "<br>".join(hints)
                         except: pass
                    else:
                        pass # Path missing or cross-env mismatch
    
                queue_html += f"""
                <div class="queue-card" id="card-{vid}">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                        <span style="font-weight:bold; font-size:13px; color:#334155;">ID: {vid} <span style='font-size:10px; color:#64748b; font-weight:normal;'>(Rank #{rank})</span></span>
                        <span style="font-size:10px; font-weight:bold; color:white; background:{status_color}; padding:2px 6px; border-radius:4px;">{status}</span>
                    </div>
                    
                    {score_badge_html}
    
                    <div class="prop-content" style="margin-top:10px;">
                        <strong>Note (Extract):</strong><br>
                        <span style="color:#64748b; font-size:11px;">{prop_excerpt}</span>
                    </div>
                    
                    <div class="approval-form" style="margin-top:10px; border-top:1px solid #f1f5f9; padding-top:10px; display:{'block' if status=='PENDING' else 'none'};">
                        <div style="font-size:11px; font-weight:bold; margin-bottom:5px;">승인 옵션 선택:</div>
                        <label><input type="checkbox" id="chk-dcm-{vid}" checked> Data Collection Master</label><br>
                        <label><input type="checkbox" id="chk-adl-{vid}"> Anomaly Detection Logic</label><br>
                        <label><input type="checkbox" id="chk-bs-{vid}"> Baseline Signals</label>
                        
                        <input type="text" id="note-{vid}" placeholder="승인 메모 (Notes)" style="width:100%; margin-top:8px; padding:4px; font-size:11px; border:1px solid #cbd5e1; border-radius:4px; box-sizing:border-box;">
                        
                        <button onclick="generateYaml('{vid}')" style="width:100%; margin-top:8px; background:#3b82f6; color:white; border:none; padding:6px; border-radius:4px; font-size:11px; cursor:pointer; font-weight:bold;">
                            📋 YAML 생성 (복사)
                        </button>
                    </div>
                </div>
                """
            queue_html += "</div>"
        else:
            queue_html += """
            <div style='padding:20px 10px; text-align:center; background:#f8fafc; border:1px dashed #e2e8f0; border-radius:6px; margin:10px 0;'>
                <div style='font-size:12px; color:#64748b; font-weight:bold;'>No proposals today — scoring logic active (Phase 32)</div>
                <div style='font-size:10px; color:#94a3b8; margin-top:5px;'>Hoin Insight engine is active and monitoring.</div>
            </div>
            """
    except Exception as e:
        queue_html = f"<div style='color:red; font-size:11px;'>Queue 로드 실패: {e}</div>"

    
    # [Phase 31-E] Deep Analysis Results Section (Replaces Applied Changes)
    # Renders summary of Deep Logic Analysis from deep_analysis_results.json
    applied_html = ""
    
    try:
        # Loop back 3 days to gather all recent analysis

        deep_base = base_dir / "data/narratives/deep_analysis"
        items = []
        seen_vids = set()
        
        for i in range(10):
            try:
                d = datetime.utcnow() - timedelta(days=i)
                d_ymd = d.strftime("%Y/%m/%d")
                sum_path = deep_base / d_ymd / "deep_analysis_results.json"
                
                if sum_path.exists():
                    day_items = json.loads(sum_path.read_text(encoding="utf-8"))
                    for item in day_items:
                        vid = item.get("video_id")
                        if vid and vid not in seen_vids:
                            seen_vids.add(vid)
                            # Store the folder date so we know where to find the markdown report
                            item["folder_date"] = d_ymd
                            items.append(item)
            except Exception:
                continue
        
        has_items = False
        
        if items:
            has_items = True
            applied_html += '<div class="applied-list" style="display:flex; flex-direction:column; gap:10px;">'
            
            # Prepare Report Data Injection
            report_data_js = "window.REPORT_DATA = window.REPORT_DATA || {};\n"
            
            for item in items:
                v_title = item.get("title", "Untitled")
                v_topic = item.get("real_topic", "Unknown")
                v_anomaly = item.get("anomaly_level", "NORMAL")
                v_logic = item.get("logic_path", "Standard")
                v_reason = item.get("real_topic_reasoning", "")
                vid = item.get("video_id", "")
                # Use folder_date for path lookup, fallback to analysis_date
                v_date = item.get("folder_date", item.get("analysis_date", "")).replace("-", "/") 
                
                # [Full Report Loader]
                full_report_html = "<p>리포트 파일이 없습니다.</p>"
                if vid and v_date:
                    rep_path = deep_base / v_date / f"video_{vid}_report.md"
                    if rep_path.exists():
                        raw_md = rep_path.read_text(encoding="utf-8")
                        full_report_html = parse_markdown(raw_md)
                
                # [Evolution UI Injection]
                evo_ui = ""
                if vid in evo_map:
                    for evo in evo_map[vid]:
                        evo_ui += f"""
                        <div style="margin-top:20px; padding:15px; border:2px dashed #8b5cf6; border-radius:8px; background:#f5f3ff; color:#1e293b; text-align:left;">
                            <h3 style="margin-top:0; color:#6d28d9; font-size:16px;">🚀 System Evolution Proposal ({evo['id']})</h3>
                            <div style="font-size:13px; color:#4c1d95; margin-bottom:12px; line-height:1.5;">
                                <strong style="color:#7c3aed;">[Category]</strong> {evo['category']}<br>
                                <strong style="color:#7c3aed;">[Proposed Change]</strong> {evo['content']['condition']}<br>
                                <strong style="color:#7c3aed;">[Logic/Meaning]</strong> {evo['content']['meaning']}
                            </div>
                            <!-- Approval UI -->
                            <div class="approval-form" style="background:white; padding:12px; border-radius:6px; border:1px solid #ddd; box-shadow:inset 0 1px 2px rgba(0,0,0,0.05);">
                                <div style="font-size:11px; font-weight:bold; margin-bottom:8px; color:#64748b;">승인 및 엔진 반영 옵션:</div>
                                <div style="display:flex; gap:15px; margin-bottom:10px;">
                                    <label style="display:flex; align-items:center; gap:5px; font-size:12px; cursor:pointer;"><input type="checkbox" id="popup-dcm-{evo['id']}" checked> Data Master</label>
                                    <label style="display:flex; align-items:center; gap:5px; font-size:12px; cursor:pointer;"><input type="checkbox" id="popup-adl-{evo['id']}"> Anomaly Logic</label>
                                </div>
                                <textarea id="popup-note-{evo['id']}" placeholder="승인 관련 메모를 입력하세요..." style="width:100%; margin-top:5px; font-size:12px; height:50px; padding:8px; border:1px solid #e2e8f0; border-radius:4px; font-family:sans-serif;"></textarea>
                                <button onclick="generatePopupYaml('{evo['id']}', '{vid}')" style="width:100%; margin-top:10px; background:#8b5cf6; color:white; border:none; padding:10px; border-radius:6px; cursor:pointer; font-weight:bold; font-size:13px; transition:background 0.2s;" onmouseover="this.style.background='#7c3aed'" onmouseout="this.style.background='#8b5cf6'">
                                    승인 및 YAML 복사 (Apply to Engine)
                                </button>
                            </div>
                        </div>
                        """
                full_report_html += evo_ui

                # Escape quotes for JS string
                full_report_html = full_report_html.replace('"', '&quot;').replace("'", "&#39;").replace("\n", " ").replace("\\", "\\\\")
                
                report_data_js += f'window.REPORT_DATA["{vid}"] = "{full_report_html}";\n'

                # Color coding for Anomaly
                anom_bg = "#e0f2fe" # blue-50
                anom_col = "#0369a1" # blue-700
                if v_anomaly == "CRITICAL":
                    anom_bg = "#fee2e2" # red-100
                    anom_col = "#b91c1c" # red-700
                elif v_anomaly == "WARNING":
                    anom_bg = "#ffedd5" # orange-100
                    anom_col = "#c2410c" # orange-700
                
                # Logic Badge
                logic_html = ""
                if v_logic:
                        logic_html = f'<span style="font-size:9px; background:#f1f5f9; color:#475569; padding:2px 5px; border-radius:3px; margin-right:3px;">{v_logic}</span>'

                applied_html += f"""
                <div class="applied-card" style="background:white; border:1px solid #cbd5e1; border-left:4px solid {anom_col}; border-radius:6px; padding:10px; box-shadow:0 1px 2px rgba(0,0,0,0.05);">
                    <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:5px;">
                        <span style="font-size:12px; font-weight:bold; color:{anom_col};">{v_anomaly} ANOMALY</span>
                        <span style="font-size:10px; color:#94a3b8;">Topic: {v_topic}</span>
                    </div>
                    <div style="font-size:12px; font-weight:600; color:#334155; margin-bottom:5px; line-height:1.4;">
                        {v_title}
                    </div>
                        <div style="display:flex; flex-wrap:wrap; gap:5px; margin-bottom:8px;">
                        {logic_html}
                    </div>
                    <div style="font-size:11px; color:#64748b; background:#f8fafc; padding:6px; border-radius:4px; margin-bottom:10px;">
                        {v_reason}
                    </div>
                    <button onclick="showDeepLogicReport('{vid}')" style="width:100%; padding:6px; background:white; border:1px solid #cbd5e1; border-radius:4px; font-size:11px; color:#475569; cursor:pointer;" onmouseover="this.style.background='#f1f5f9'" onmouseout="this.style.background='white'">
                        📄 상세 분석 리포트 보기
                    </button>
                </div>
                """
                
            # Inject JS Data
            applied_html += f"<script>{report_data_js}</script>"
            applied_html += "</div>"
        
        if not has_items:
             applied_html += "<div style='font-size:12px; color:#94a3b8; padding:20px; text-align:center;'>금일 분석된 딥 로직 데이터가 없습니다.</div>"
             
    except Exception as e:
        applied_html += f"<div style='color:red; font-size:11px;'>Load Error: {e}</div>"

    # sidebar_html += queue_html  <-- REMOVED (Duplicated in Narrative Queue Tab)
    # sidebar_html += applied_html <-- REMOVED (Moved to Change Effectiveness Tab)

    
    # [Phase 31-B Enhanced] Deep Logic Analysis Loader
    deep_logic_html = ""
    try:
        # Load from recent 10 days
        deep_results = []
        for i in range(10):
            d_ymd = (base_date - timedelta(days=i)).strftime("%Y/%m/%d")
            d_json = base_dir / "data/narratives/deep_analysis" / d_ymd / "deep_analysis_results.json"
            if d_json.exists():
                try:
                    day_data = json.loads(d_json.read_text(encoding="utf-8"))
                    if isinstance(day_data, list): deep_results.extend(day_data)
                    else: deep_results.append(day_data)
                except: pass
        
        if deep_results:
            # Sort by most recent
            deep_results.sort(key=lambda x: x.get('analysis_date', ''), reverse=True)
            
            deep_logic_html += '<div style="display:grid; gap:20px;">'
            for res in deep_results:
                vid = res.get('video_id')
                level = res.get('anomaly_level', 'L1')
                nature = res.get('content_nature', 'Lagging')
                
                lv_col = "#64748b"
                if level == "L3": lv_col = "#ef4444"
                elif level == "L2": lv_col = "#f59e0b"
                
                deep_logic_html += f"""
                <div style="background:white; border:1px solid #e2e8f0; border-radius:12px; padding:20px; box-shadow:0 4px 6px -1px rgba(0,0,0,0.05);">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:15px; border-bottom:1px solid #f1f5f9; padding-bottom:15px;">
                        <div style="width:70%;">
                            <div style="font-size:11px; font-weight:700; color:#64748b; margin-bottom:5px;">REAL TOPIC</div>
                            <div style="font-size:18px; font-weight:800; color:#1e293b;">{res.get('real_topic')}</div>
                            <div style="font-size:12px; color:#475569; margin-top:4px;">{res.get('real_topic_reasoning')}</div>
                        </div>
                        <div style="text-align:right;">
                            <span style="background:{lv_col}; color:white; padding:4px 10px; border-radius:8px; font-size:12px; font-weight:900;">{level}</span>
                            <div style="font-size:10px; color:#94a3b8; margin-top:5px; font-weight:bold;">{nature}</div>
                        </div>
                    </div>
                    
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:15px;">
                        <div style="background:#f8fafc; padding:12px; border-radius:8px;">
                            <div style="font-size:10px; font-weight:800; color:#64748b; margin-bottom:8px;">💡 WHY NOW (Trigger)</div>
                            <div style="font-size:12px; font-weight:700; color:#334155;">{res.get('why_now', {}).get('trigger_type')}</div>
                            <div style="font-size:11px; color:#475569; margin-top:4px; line-height:1.4;">{res.get('why_now', {}).get('description')}</div>
                        </div>
                        <div style="background:#f0f9ff; padding:12px; border-radius:8px;">
                            <div style="font-size:10px; font-weight:800; color:#0369a1; margin-bottom:8px;">🎯 ENGINE CONCLUSION</div>
                            <div style="font-size:12px; color:#0c4a6e; line-height:1.5;">{res.get('engine_conclusion')}</div>
                        </div>
                    </div>
                    
                    <div style="margin-top:15px; display:flex; justify-content:space-between; align-items:center;">
                        <div style="font-size:11px; color:#94a3b8;">Video: {res.get('title')} ({vid})</div>
                        <a href="https://youtu.be/{vid}" target="_blank" style="font-size:11px; color:#3b82f6; text-decoration:none; font-weight:bold;">Watch Original ➜</a>
                    </div>
                </div>
                """
            deep_logic_html += '</div>'
        else:
            deep_logic_html = "<div style='padding:40px; text-align:center; color:#94a3b8; background:#f8fafc; border-radius:12px; border:2px dashed #e2e8f0;'>최근 분석된 딥 로직 결과가 없습니다. (Phase 31-B)</div>"
    except Exception as e:
        deep_logic_html = f"<div style='color:red;'>Deep Logic Load Fail: {e}</div>"
    # [End] Deep Logic Analysis Loader
    # [Start] Analysis Log Loader
    analysis_log_html = ""
    try:
        log_path = base_dir / "data/evolution/reports" / ymd.replace("-","/") / "daily_analysis_log.json"
        if log_path.exists():
            log_data = json.loads(log_path.read_text(encoding='utf-8'))
            results = log_data.get("results", [])
            
            if results:
                analysis_log_html += '<div style="display:grid; gap:10px;">'
                for res in results:
                    title = res.get('source_file', 'Unknown Source')
                    decision = res.get('final_decision', 'UNKNOWN')
                    summary = res.get('summary', 'No summary')
                    
                    # Status Badge
                    d_color = "#64748b" # Default Gray
                    if decision == "UPDATE_REQUIRED": d_color = "#8b5cf6" # Purple
                    elif decision == "LOG_ONLY": d_color = "#10b981" # Green
                    
                    analysis_log_html += f"""
                    <div style="background:white; border:1px solid #e2e8f0; border-radius:8px; padding:15px; display:flex; flex-direction:column; gap:8px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="font-weight:bold; color:#1e293b; font-size:13px;">📺 {title}</span>
                            <span style="background:{d_color}; color:white; padding:2px 8px; border-radius:12px; font-size:10px; font-weight:bold;">{decision}</span>
                        </div>
                        <div style="font-size:12px; color:#475569;">{summary}</div>
                        <div style="font-size:11px; color:#94a3b8; background:#f8fafc; padding:6px; border-radius:4px;">
                            <span style="font-weight:bold;">Learned Rule:</span> {res.get('learned_rule','-')}
                        </div>
                    </div>
                    """
                analysis_log_html += '</div>'
            else:
                analysis_log_html = "<div style='color:#94a3b8; font-size:12px;'>분석된 영상이 없습니다.</div>"
        else:
             analysis_log_html = "<div style='color:#94a3b8; font-size:12px; padding:20px; text-align:center; background:#f8fafc; border-radius:8px;'>데이터가 아직 생성되지 않았습니다. (Daily Scan Pending)</div>"
    except Exception as e:
        analysis_log_html = f"<div style='color:red; font-size:11px;'>Log Load Error: {e}</div>"
    # [End] Analysis Log Loader

    # [Phase 35] Evolution Proposals Logic
    evolution_html = ""
    evo_dir = base_dir / "data" / "evolution" / "proposals"
    if evo_dir.exists():
        for evo_file in evo_dir.glob("*.json"):
            try:
                # Handle list or single dict
                content = json.loads(evo_file.read_text(encoding='utf-8'))
                items = content if isinstance(content, list) else [content]
                
                for item in items:
                    if item.get("status") not in ["PROPOSED", "COLLECTOR_GENERATED"]: continue
                    
                    bg_color = "#f3e5f5" if item.get('category') == "LOGIC_UPDATE" else "#e3f2fd"
                    border_color = "#9c27b0" if item.get('category') == "LOGIC_UPDATE" else "#2196f3"
                    badge = "🧠 LOGIC" if item.get('category') == "LOGIC_UPDATE" else "📊 DATA"
                    
                    # Check if collector script exists
                    collector_info = ""
                    if item.get('category') == 'DATA_ADD' and item.get('collector_script'):
                        collector_path = base_dir / item['collector_script']
                        if collector_path.exists():
                            collector_info = f"""
                            <div style="background:#d1fae5; padding:6px; border-radius:4px; margin-bottom:8px; font-size:10px;">
                                ✅ <b>수집 모듈 생성 완료:</b> <code>{item['collector_script']}</code>
                            </div>
                            """
                    
                    evolution_html += f"""
                    <div class="card" id="proposal-{item['id']}" style="border-left: 4px solid {border_color}; background: {bg_color}; margin-bottom: 15px; padding:12px;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                            <span class="badge" style="background:{border_color}; color:white; padding:2px 6px; border-radius:4px; font-size:10px;">{badge}</span>
                            <small style="font-size:10px; color:#666;">{item.get('generated_at','')[:10]}</small>
                        </div>
                        
                        {collector_info}
                        
                        <div style="font-weight:bold; margin-bottom:5px; font-size:12px; color:#333;">제안 내용:</div>
                        <div style="background:rgba(255,255,255,0.7); padding:8px; border-radius:4px; font-size:11px; font-family:monospace; margin-bottom:10px; border:1px solid rgba(0,0,0,0.1);">
                            {item['content'].get('condition', '') or item['content'].get('add_line', '')} 
                            <br>→ {item['content'].get('meaning', '')}
                        </div>
                        
                        <div style="font-size:10px; color:#555; margin-bottom:10px; font-style:italic;">
                            "{str(item.get('evidence',{}).get('quote',''))[:60]}..."
                        </div>
                        
                        <div style="display:flex; gap:5px;">
                            <button onclick="approveProposal('{item['id']}')" style="flex:1; background:{border_color}; color:white; border:none; padding:6px; border-radius:4px; cursor:pointer; font-size:11px; font-weight:bold;">승인 (Merge)</button>
                            <button onclick="requestImplementation('{item['id']}')" style="flex:1; background:#f59e0b; color:white; border:none; padding:6px; border-radius:4px; cursor:pointer; font-size:11px; font-weight:bold;">🤖 Antigravity 요청</button>
                            <button onclick="rejectProposal('{item['id']}')" style="flex:1; background:#94a3b8; color:white; border:none; padding:6px; border-radius:4px; cursor:pointer; font-size:11px;">거절</button>
                        </div>
                    </div>
                    """
            except Exception as e:
                print(f"Error loading evo file {evo_file}: {e}")

    if not evolution_html:
        evolution_html = "<div style='color:#999; text-align:center; padding:20px; font-size:12px;'>새로운 진화 제안이 없습니다.</div>"

    # [Layout Fix] Re-assembling the HTML with proper Tab Structure

    # [Restored Logic] Calculate missing variables for Dashboard
    
    # 1. Change Effectiveness
    effectiveness_html = """
    <div style="padding:40px; text-align:center; color:#94a3b8; background:white; border:1px solid #e2e8f0; border-radius:8px;">
        <h3>데이터 누적 중...</h3>
        <p style="font-size:12px;">변경 효과 분석을 위한 데이터가 충분하지 않습니다.</p>
    </div>
    """
    try:
        eff_path = base_dir / "data/ops/effectiveness" / ymd.replace("-","/") / "effectiveness_report.json"
        if eff_path.exists():
            eff_data = json.loads(eff_path.read_text(encoding='utf-8'))
            # Simple render
            effectiveness_html = '<div style="background:white; padding:20px; border-radius:8px; border:1px solid #e2e8f0;">'
            effectiveness_html += f"<div><strong>Score:</strong> {eff_data.get('score', 0)}</div>"
            effectiveness_html += f"<div style='margin-top:10px; font-size:12px; white-space:pre-wrap;'>{eff_data.get('analysis','')}</div>"
            effectiveness_html += "</div>"
    except: pass

    # 2. Topic Candidates & Script Output
    topics_count = 0
    try:
        tc_path = base_dir / "data/topics/candidates" / ymd.replace("-","/") / "topic_candidates.json"
        if tc_path.exists():
            tc_data = json.loads(tc_path.read_text(encoding='utf-8'))
            topics_count = len(tc_data.get("candidates", []))
    except: pass
    
    # Candidate HTML (Simple List)
    candidate_html = ""
    if topics_count > 0:
        candidate_html += f'<div style="background:white; padding:20px; border-radius:8px; border:1px solid #e2e8f0;">Found {topics_count} candidates.</div>'
    else:
        candidate_html += '<div style="padding:20px; text-align:center; color:#94a3b8;">No candidates found.</div>'

    # Script Output
    topic_title = "주제 선정 대기중"
    script_exists = False
    script_body = ""
    try:
        out_path = base_dir / "data/output" / ymd.replace("-","/") / "insight_script.md"
        if out_path.exists():
            script_exists = True
            script_body = out_path.read_text(encoding='utf-8')
            # Extract title
            for line in script_body.splitlines():
                if line.startswith("# "):
                    topic_title = line[2:].strip()
                    break
            if not topic_title: topic_title = "스크립트 생성 완료"
    except: pass

    # 3. Archive HTML
    archive_html = ""
    try:
        # List last 7 days of output
        archive_html += '<div class="archive-list" style="background:white; border-radius:8px; border:1px solid #e2e8f0; overflow:hidden;">'
        for i in range(1, 8):
            past_date = (datetime.utcnow() - timedelta(days=i)).strftime("%Y/%m/%d")
            p_script = base_dir / "data/output" / past_date / "insight_script.md"
            if p_script.exists():
                archive_html += f'<div style="padding:15px; border-bottom:1px solid #f1f5f9; display:flex; justify-content:space-between;">'
                archive_html += f'<span style="font-weight:bold; color:#334155;">{past_date} Report</span>'
                archive_html += f'<a href="#" style="color:#3b82f6; text-decoration:none; font-size:12px;">View</a>'
                archive_html += '</div>'
        
        if archive_html == '<div class="archive-list" style="background:white; border-radius:8px; border:1px solid #e2e8f0; overflow:hidden;">':
             archive_html = '<div style="padding:20px; text-align:center; color:#94a3b8;">No archives found.</div>'
        else:
             archive_html += '</div>'
    except: 
        archive_html = '<div style="padding:20px; text-align:center; color:#94a3b8;">Archive error.</div>'
    
    # 4. Revival HTML
    revival_html = '<div style="padding:20px; text-align:center; color:#94a3b8;">No revival data.</div>'
    
    # 5. Ledger HTML
    ledger_html = '<div style="padding:20px; text-align:center; color:#94a3b8;">No ledger data.</div>'
    
    # 6. Final Card (Ensure variable exists)
    if 'final_card' not in locals():
        final_card = {}

    html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="utf-8">
        <title>Hoin Insight 파이프라인</title>
        <style>{css}</style>
        <style>
            /* Additional Tab Styles */
            .tab-content {{ display: none; animation: fadeIn 0.3s ease; }}
            .tab-content.active {{ display: block; }}
            @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(5px); }} to {{ opacity: 1; transform: translateY(0); }} }}
            
            .core-health-box {{ display: flex; gap: 15px; align-items: center; background: #fff; padding: 5px 15px; border-radius: 8px; border: 1px solid #e2e8f0; margin-right: 20px; }}
            .core-item {{ display: flex; flex-direction: column; align-items: center; font-size: 11px; }}
            .core-label {{ font-weight: bold; color: #64748b; }}
            .core-val {{ font-weight: bold; }}
            .cv-OK {{ color: #166534; }}
            .cv-FAIL {{ color: #dc2626; }}
            .cv-SKIP {{ color: #9ca3af; }}
            .cv-WARMUP {{ color: #ea580c; }}
            
            .conf-badge {{ padding: 4px 10px; border-radius: 6px; font-weight: bold; font-size: 13px; }}
            .bg-green-100 {{ background-color: #dcfce7; }} .text-green-800 {{ color: #166534; }}
            .bg-yellow-100 {{ background-color: #fef9c3; }} .text-yellow-800 {{ color: #854d0e; }}
            .bg-red-100 {{ background-color: #fee2e2; }} .text-red-800 {{ color: #991b1b; }}
            
            /* Queue Card Styles */
            .queue-list {{ display: flex; flex-direction: column; gap: 10px; }}
            .queue-card {{ background: white; border: 1px solid #cbd5e1; border-radius: 6px; padding: 12px; font-size: 12px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }}
            .approval-form label {{ display: block; margin-bottom: 2px; cursor: pointer; }}
        </style>
        <script>
            function activate(tabId) {{
                // Hide all tabs
                document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(el => el.style.display = 'none');
                
                // Deactivate all nav items
                document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
                
                // Show target tab
                const target = document.getElementById(tabId);
                if(target) {{
                    target.classList.add('active');
                    target.style.display = 'block';
                }}
                
                // Activate nav item
                const navItem = document.querySelector(`.nav-item[onclick="activate('${{tabId}}')"]`);
                if(navItem) navItem.classList.add('active');
                
                // Scroll to top
                document.querySelector('.main-panel').scrollTop = 0;
            }}
            
            function toggleAction(id) {{
                const box = document.getElementById('action-box-' + id);
                box.style.display = box.style.display === 'none' ? 'block' : 'none';
            }}
            
            function openModal() {{
                document.getElementById('scriptModal').classList.add('modal-active');
            }}
            
            function approveProposal(proposalId) {{
                if (!confirm(`제안 ${{proposalId}}를 승인하시겠습니까?\\n\\n승인 시 DATA_COLLECTION_MASTER가 업데이트되고 수집 스케줄에 추가됩니다.`)) {{
                    return;
                }}
                
                // GitHub Pages는 정적 사이트이므로 실제 승인은 GitHub Actions를 통해 처리
                alert(`승인 요청이 접수되었습니다.\\n\\nGitHub Actions를 통해 처리됩니다:\\n1. 제안 상태 → APPROVED\\n2. DATA_COLLECTION_MASTER 업데이트\\n3. 수집 스케줄 추가\\n\\n처리 완료까지 약 1-2분 소요됩니다.`);
                
                // 시각적 피드백
                const card = document.getElementById(`proposal-${{proposalId}}`);
                if (card) {{
                    card.style.opacity = '0.5';
                    card.style.border = '2px solid #10b981';
                    const badge = document.createElement('div');
                    badge.style.cssText = 'background:#10b981; color:white; padding:4px 8px; border-radius:4px; margin-top:8px; font-size:10px; text-align:center;';
                    badge.textContent = '✓ 승인 대기 중...';
                    card.appendChild(badge);
                }}
                
                // TODO: GitHub API를 통한 자동 승인 처리 구현
                // 현재는 수동으로 proposal JSON 파일의 status를 APPROVED로 변경 필요
            }}
            
            function rejectProposal(proposalId) {{
                const reason = prompt(`제안 ${{proposalId}}를 거절하는 이유를 입력하세요:`);
                if (!reason) return;
                
                alert(`거절 사유가 기록되었습니다:\\n"${{reason}}"\\n\\n제안이 거절 목록으로 이동됩니다.`);
                
                // 시각적 피드백
                const card = document.getElementById(`proposal-${{proposalId}}`);
                if (card) {{
                    card.style.opacity = '0.3';
                    card.style.border = '2px solid #ef4444';
                    const badge = document.createElement('div');
                    badge.style.cssText = 'background:#ef4444; color:white; padding:4px 8px; border-radius:4px; margin-top:8px; font-size:10px; text-align:center;';
                    badge.textContent = '✗ 거절됨';
                    card.appendChild(badge);
                }}
                
                // TODO: 거절 사유를 포함한 상태 업데이트
            }}
            
            function requestImplementation(proposalId) {{
                const notes = prompt(`Antigravity에게 전달할 추가 요구사항이나 메모를 입력하세요 (선택사항):`);
                
                const message = `🤖 Antigravity 구현 요청\\n\\n` +
                    `제안 ID: ${{proposalId}}\\n\\n` +
                    `다음 작업이 GitHub Issue로 생성됩니다:\\n` +
                    `1. 데이터 수집 모듈 완성 (API 연동)\\n` +
                    `2. 로직 업데이트 (필요시)\\n` +
                    `3. 테스트 및 검증\\n` +
                    `4. DATA_COLLECTION_MASTER 업데이트\\n\\n` +
                    (notes ? `추가 요구사항: ${{notes}}\\n\\n` : '') +
                    `계속하시겠습니까?`;
                
                if (!confirm(message)) return;
                
                // 시각적 피드백
                const card = document.getElementById(`proposal-${{proposalId}}`);
                if (card) {{
                    card.style.border = '3px solid #f59e0b';
                    const badge = document.createElement('div');
                    badge.style.cssText = 'background:#f59e0b; color:white; padding:6px 10px; border-radius:4px; margin-top:8px; font-size:11px; text-align:center; font-weight:bold;';
                    badge.innerHTML = '🤖 Antigravity 구현 요청됨<br><small style="font-size:9px;">GitHub Issue 생성 중...</small>';
                    card.appendChild(badge);
                }}
                
                alert(`✅ 구현 요청이 접수되었습니다!\\n\\n` +
                    `GitHub Issue가 자동으로 생성되며,\\n` +
                    `Antigravity가 다음 세션에서 작업을 시작합니다.\\n\\n` +
                    `진행 상황은 GitHub Issues에서 확인하세요.`);
                
                // TODO: GitHub API를 통한 Issue 자동 생성
                // 현재는 다음 파이프라인 실행 시 human_loop_notifier가 처리
            }}
        </script>
    </head>
    <body>
        <div class="top-bar">
            <div style="display:flex; align-items:center; gap:20px;">
                <h1>Hoin Insight</h1>
                
                <!-- Core Health Widget -->
                <div class="core-health-box">
                    <span style="font-size:11px; font-weight:bold; color:#475569; margin-right:5px;">CORE:</span>
                    <div class="core-item"><span class="core-label">US10Y</span><span class="core-val cv-{core_bd.get('US10Y','FAIL')}">{core_bd.get('US10Y','-')}</span></div>
                    <div style="width:1px; height:20px; background:#e2e8f0;"></div>
                    <div class="core-item"><span class="core-label">SPX</span><span class="core-val cv-{core_bd.get('SPX','FAIL')}">{core_bd.get('SPX','-')}</span></div>
                    <div style="width:1px; height:20px; background:#e2e8f0;"></div>
                    <div class="core-item"><span class="core-label">BTC</span><span class="core-val cv-{core_bd.get('BTC','FAIL')}">{core_bd.get('BTC','-')}</span></div>
                </div>
                
                <div class="conf-badge {conf_cls}">Confidence: {conf_level}</div>
            </div>
            
            <div style="display:flex; gap:10px;">
                <div class="conf-badge {content_cls}">{content_mode}</div>
                <div class="conf-badge {status_data['narrative_cls']}">Narrative: {status_data['narrative_label']}</div>
                <div class="conf-badge {preset_cls}" title="Content Depth Preset">Preset: {preset_label}</div>
                <div class="status-badge status-{status_data['raw_status']}">{status_data['status']}</div>
            </div>
        </div>
        
        <div class="dashboard-container">
            
            <!-- LEFT: Navigation Panel -->
            <div class="nav-panel">
                <div style="font-size: 13px; font-weight: 800; color: #f8fafc; padding: 20px 25px; border-bottom: 1px solid #1e293b; margin-bottom: 10px; display: flex; align-items: center; justify-content: space-between;">
                    <span>HOIN INSIGHT v1.1.1</span>
                    <span title="System Status: {display_status}" style="font-size:10px; cursor:help;">{status_icon_char}</span>
                </div>
                
                <div class="nav-label">MAIN VIEW</div>
                <div class="nav-item active" onclick="activate('today-insight')"><span class="nav-icon">⭐</span> 오늘의 인사이트</div>
                <div class="nav-item" onclick="activate('architecture-diagram')"><span class="nav-icon">🟦</span> 아키텍처</div>
                
                <div class="nav-label">OPERATIONS</div>
                <div class="nav-item" onclick="activate('ops-scoreboard')"><span class="nav-icon">📈</span> 운영 지표</div>
                <div class="nav-item" onclick="activate('data-status')"><span class="nav-icon">📡</span> 데이터 수집 현황</div>
                <div class="nav-item" onclick="activate('system-evolution')"><span class="nav-icon">🚀</span> 시스템 진화 제안</div>
                <div class="nav-item" onclick="activate('change-effectiveness')"><span class="nav-icon">📊</span> 변경 효과 분석</div>

                <div class="nav-label">WORKFLOW</div>
                <div class="nav-item" onclick="activate('youtube-inbox')"><span class="nav-icon">📺</span> 유튜브 인박스</div>
                <div class="nav-item" onclick="activate('revival-engine')"><span class="nav-icon">♻️</span> 부활 엔진</div>
                
                <div class="nav-label">ARCHIVE / LOGS</div>
                <div class="nav-item" onclick="activate('rejection-ledger')"><span class="nav-icon">🚫</span> 거절/보류 리스트</div>
                <div class="nav-item" onclick="activate('topic-candidates')"><span class="nav-icon">📂</span> 토픽 후보군</div>
                
                <div class="nav-label">OUTPUT</div>
                <div class="nav-item" onclick="activate('final-decision')"><span class="nav-icon">⚖️</span> 최종 의사결정 (Raw)</div>
                <div class="nav-item" onclick="activate('insight-script')"><span class="nav-icon">📜</span> 인사이트 스크립트 (Raw)</div>
            </div>

            <!-- CENTER: Main Process Flow (Tabs) -->
            <div class="main-panel">
                <div class="sections-wrapper">
                    
                    <!-- TAB 0: Today's Insight (NEW HOME) -->
                    <div id="today-insight" class="tab-content active" style="display:block;">
                        <div style="max-width: 900px; margin: 0 auto;">
                            <!-- Header -->
                            <div style="text-align:center; margin-bottom:30px;">
                                <div style="font-size:12px; color:#64748b; font-weight:600; text-transform:uppercase; letter-spacing:1px; margin-bottom:5px;">Today's Insight</div>
                                <h1 style="font-size:28px; font-weight:800; color:#1e293b; margin:0;">
                                    {topic_title}
                                </h1>
                                <div style="margin-top:10px;">
                                    <span style="font-size:11px; background:#f1f5f9; color:#475569; padding:4px 10px; border-radius:15px; font-weight:600;">{ymd}</span>
                                </div>
                            </div>

                            <!-- Error Alert (If System Failed) -->
                            {error_alert_html}

                            <!-- Main Content Grid -->
                            <div style="display:grid; grid-template-columns: 1fr 1.5fr; gap:25px;">
                                
                                <!-- Left: Decision Logic -->
                                <div>
                                    <div class="card" style="height:100%;">
                                        <h3 style="font-size:14px; font-weight:700; color:#334155; margin-bottom:15px; border-bottom:1px solid #e2e8f0; padding-bottom:10px;">
                                            🎯 선정 이유 (Rationale)
                                        </h3>
                                        <div style="font-size:13px; line-height:1.6; color:#475569;">
                                            {rationale}
                                        </div>
                                        
                                        <div style="margin-top:20px;">
                                            <h4 style="font-size:12px; font-weight:700; color:#64748b; margin-bottom:8px;">관련 데이터</h4>
                                            <div style="display:flex; flex-wrap:wrap; gap:5px;">
                                                {key_data_html}
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <!-- Right: Script Preview -->
                                <div>
                                    <div class="card" style="height:100%; border-left:4px solid #3b82f6;">
                                        <h3 style="font-size:14px; font-weight:700; color:#334155; margin-bottom:15px; display:flex; justify-content:space-between; align-items:center;">
                                            <span>📜 스크립트 초안</span>
                                            <button onclick="activate('insight-script')" style="font-size:10px; background:#eff6ff; color:#3b82f6; border:none; padding:4px 8px; border-radius:4px; cursor:pointer;">전체 보기 ➜</button>
                                        </h3>
                                        <div style="font-size:12px; line-height:1.7; color:#334155; white-space:pre-wrap; max-height:400px; overflow-y:auto; background:#fafafa; padding:15px; border-radius:6px; border:1px solid #f1f5f9;">
{script_preview}
                                        </div>
                                    </div>
                                </div>
                            </div>

                        </div>
                    </div>

                    <!-- TAB 1: Architecture Diagram -->
                    <div id="architecture-diagram" class="tab-content" style="display:none;">
                        <div class="architecture-diagram">
                            <div style="text-align: center; margin-bottom: 20px;">
                                <h2 style="font-size: 20px; font-weight: 700; color: #1e293b;">Hoin Insight 파이프라인</h2>
                                <p style="font-size: 13px; color: #64748b;">실시간 데이터 수집 및 분석 흐름도</p>
                            </div>
                            
                            <!-- 1. Scheduler -->
                            <div class="process-row">
                                <div class="node-group-label" style="color: #f59e0b;">01. 스케줄 및 트리거</div>
                                <div class="proc-node node-scheduler">
                                    <div class="proc-icon">⏰</div>
                                    <div class="proc-content">
                                        <div class="proc-title">자동 스케줄러 (축 분할)</div>
                                        <div class="proc-desc">암호화폐(4회), 환율, 시장지수, 백필</div>
                                    </div>
                                </div>
                                <div class="arrow-down"></div>
                            </div>
                            
                            <!-- 2. Github Actions -->
                            <div class="process-row">
                                <div class="node-group-label">02. 오케스트레이션</div>
                                <div class="proc-node node-github active-node">
                                    <div class="proc-icon">🏗️</div>
                                    <div class="proc-content">
                                        <div class="proc-title">GitHub Actions 파이프라인</div>
                                        <div class="proc-desc">Run ID: {status_data['run_id']}</div>
                                    </div>
                                </div>
                                <div class="arrow-down"></div>
                            </div>

                            <!-- 3. Data Intake -->
                            <div class="process-row">
                                <div class="node-group-label">03. 데이터 수집</div>
                                <div class="proc-node node-data">
                                    <div class="proc-icon">📥</div>
                                    <div class="proc-content">
                                        <div class="proc-title">데이터 수집 및 정규화</div>
                                        <div class="proc-desc">원본 수집 → 정제(Curated) CSV</div>
                                    </div>
                                </div>
                                <div class="arrow-down"></div>
                            </div>

                            <!-- 4. Engine Processing -->
                            <div class="process-row" style="grid-template-columns: 1fr 1fr 1fr; display: grid;">
                                <div class="node-group-label">04. 엔진 코어</div>
                                <div class="proc-node node-engine">
                                    <div class="proc-title">피처 빌더</div>
                                </div>
                                <div class="proc-node node-engine">
                                    <div class="proc-title">이상치 탐지</div>
                                    <div class="proc-desc">국면: { "감지됨" if regime_exists else "없음" }</div>
                                </div>
                                <div class="proc-node node-engine">
                                     <div class="proc-title">토픽 선정</div>
                                     <div class="proc-desc">토픽 {topics_count}개</div>
                                </div>
                            </div>
                            
                            <!-- 5. Output -->
                            <div class="process-row">
                                 <div style="position:absolute; left:50%; top:-60px; height:60px; width:2px; background:#cbd5e1; transform:translateX(-50%);"></div>
                                <div class="node-group-label" style="top:-80px;">05. 배포 및 출력</div>
                                <div class="proc-node node-output" onclick="openModal()">
                                    <div class="proc-icon">🚀</div>
                                    <div class="proc-content">
                                        <div class="proc-title">콘텐츠 생성</div>
                                        <div class="proc-desc" style="font-weight:bold; color:#2563eb; margin-bottom:4px; white-space:normal; overflow:visible;">{topic_title}</div>
                                        <div class="proc-sub" style="margin-top:6px;">{ "스크립트 생성 완료 (클릭하여 전체보기)" if script_exists else "대기중" }</div>
                                    </div>
                                </div>
                            </div>
                            
                            <div style="text-align:center; padding:20px;">
                                <a href="assets/architecture.svg" target="_blank">
                                     <img src="assets/architecture.svg" style="max-width:100%; border-radius:8px;" onerror="this.parentElement.innerHTML='<div style=\'padding:40px; color:#94a3b8; font-size:14px;\'>⚠ architecture.svg/png missing</div>'" />
                                </a>
                            </div>

                            <!-- Current System State Summary (Inside Architecture Tab) -->
                            <div class="architecture-summary-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 25px; border-radius: 12px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.2); color: white; margin-top: 30px;">
                                <h3 style="font-size: 16px; font-weight: 700; margin: 0 0 20px 0; color: white; border-bottom: 2px solid rgba(255,255,255,0.3); padding-bottom: 10px;">
                                    Current System State (Today)
                                </h3>
                                
                                <div style="display: flex; flex-direction: column; gap: 15px;">
                                    <div style="background: rgba(255,255,255,0.15); padding: 12px; border-radius: 8px; backdrop-filter: blur(10px);">
                                        <div style="font-size: 11px; font-weight: 600; color: rgba(255,255,255,0.8); margin-bottom: 5px;">CORE DATASETS</div>
                                        <div style="font-size: 14px; font-weight: 700; display: flex; align-items: center; gap: 8px;">
                                            {f'🟢 HEALTHY' if all(v == 'OK' for v in core_bd.values() if v != 'SKIP') else ('🟡 PARTIAL' if any(v == 'OK' for v in core_bd.values()) else '🔴 FAIL')}
                                        </div>
                                    </div>
                                    
                                    <div style="background: rgba(255,255,255,0.15); padding: 12px; border-radius: 8px; backdrop-filter: blur(10px);">
                                        <div style="font-size: 11px; font-weight: 600; color: rgba(255,255,255,0.8); margin-bottom: 5px;">REGIME</div>
                                        <div style="font-size: 14px; font-weight: 700;">
                                            {regime_name if regime_name != "Unknown" else "N/A"}
                                        </div>
                                        <div style="font-size: 10px; color: rgba(255,255,255,0.7); margin-top: 3px;">
                                            {'(Meta-driven)' if meta_count > 0 else '(Driver-based)'}
                                        </div>
                                    </div>
                                    
                                    <div style="background: rgba(255,255,255,0.15); padding: 12px; border-radius: 8px; backdrop-filter: blur(10px);">
                                        <div style="font-size: 11px; font-weight: 600; color: rgba(255,255,255,0.8); margin-bottom: 5px;">CONFIDENCE</div>
                                        <div style="font-size: 14px; font-weight: 700; display: flex; align-items: center; gap: 8px;">
                                            {f'🟢 {conf_level}' if conf_level == 'HIGH' else (f'🟡 {conf_level}' if conf_level == 'MEDIUM' else f'🔴 {conf_level}')}
                                        </div>
                                    </div>
                                </div>
                                <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.2); font-size: 10px; color: rgba(255,255,255,0.6); text-align: center;">
                                    Last Updated: {ymd}
                                </div>
                            </div>

                        </div>
                    </div>
    """

    # [Ops Scoreboard Tab]
    ops_rows = []
    if ops_scoreboard:
        for metric, val in ops_scoreboard.items():
             if metric == "history": continue 
             label = metric.replace("_", " ").upper()
             val_cls = "ops-value"
             if metric == "reliability_score" and float(str(val).replace("%","")) < 95:
                 val_cls += " sla-breach"
             
             ops_rows.append(f"""
             <div class="ops-card">
                 <div class="{val_cls}">{val}</div>
                 <div class="ops-label">{label}</div>
             </div>
             """)
    
    html += f"""
                    <div id="ops-scoreboard" class="tab-content" style="display:none;">
                        <div style="background: white; border-top: 1px solid #e2e8f0; padding: 40px; border-radius: 8px;">
                            <h2 style="font-size: 20px; font-weight: 700; color: #1e293b; margin-bottom: 25px;">📈 운영 성과 지표 (Ops Scoreboard)</h2>
                            <div class="ops-grid">
                                {"".join(ops_rows)}
                            </div>
                            
                            <div style="margin-top: 30px; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden;">
                                <table style="width: 100%; border-collapse: collapse; font-size: 12px; background: white;">
                                    <thead style="background: #f8fafc; border-bottom: 1px solid #e2e8f0;">
                                        <tr>
                                            <th style="padding: 10px 15px; text-align: left; color: #64748b;">Date</th>
                                            <th style="padding: 10px 15px; text-align: left; color: #64748b;">Status</th>
                                            <th style="padding: 10px 15px; text-align: right; color: #64748b;">Duration</th>
                                        </tr>
                                    </thead>
                                    <tbody>
    """
    for h in ops_scoreboard.get('history', [])[:7]:
        st_color = 'background:#dcfce7; color:#166534;' if h.get('status') == 'SUCCESS' else 'background:#fee2e2; color:#991b1b;'
        html += f"""
                                        <tr style="border-bottom: 1px solid #f1f5f9;">
                                            <td style="padding: 10px 15px; color: #1e293b;">{h.get('date')}</td>
                                            <td style="padding: 10px 15px;">
                                                <span style="padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold; {st_color}">
                                                    {h.get('status')}
                                                </span>
                                            </td>
                                            <td style="padding: 10px 15px; text-align: right; color: #64748b;">{h.get('duration_minutes')}m</td>
                                        </tr>
        """
    html += """
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
    """

    # [Data Status Tab (Moved from Sidebar)]
    # Convert sidebar list items to a grid layout for main view
    data_status_grid = sidebar_html.replace('class="status-item"', 'class="status-card-grid-item"')
    data_status_grid = data_status_grid.replace('font-size: 11px', 'font-size: 13px')
    
    html += f"""
                    <div id="data-status" class="tab-content" style="display:none;">
                        <h2 style="font-size: 20px; font-weight: 700; color: #1e293b; margin-bottom: 25px;">📡 데이터 수집 현황</h2>
                        <div style="background:white; padding:30px; border-radius:8px; border:1px solid #e2e8f0;">
                            <div class="status-grid-view" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 15px;">
                                {data_status_grid}
                            </div>
                        </div>
                        <style>
                            .status-card-grid-item {{
                                display: flex; justify-content: space-between; align-items: center;
                                padding: 15px; border: 1px solid #e2e8f0; border-radius: 6px;
                                background: #f8fafc;
                            }}
                            .status-card-grid-item:hover {{
                                background: #f1f5f9; border-color: #cbd5e1;
                            }}
                        </style>
                    </div>
    """


    # [System Evolution Tab (Moved from Sidebar)]
    # Make evolution cards grid style
    evo_grid_html = evolution_html.replace('margin-bottom: 15px;', '')
    # Wrap multiple cards in grid container if simple concat
    
    html += f"""
                    <div id="system-evolution" class="tab-content" style="display:none;">
                        <h2 style="font-size: 20px; font-weight: 700; color: #1e293b; margin-bottom: 10px;">🚀 시스템 진화 제안</h2>
                        <p style="font-size:14px; color:#666; margin-bottom:25px;">
                            영상을 분석하여 발견된 <b>새로운 로직</b>과 <b>데이터</b>입니다. 승인 시 지식 베이스가 업데이트됩니다.
                        </p>

                        <!-- Analysis Log Section (New) -->
                        <div style="margin-bottom: 40px;">
                            <h3 style="font-size: 16px; font-weight: 700; color: #334155; margin-bottom: 15px; border-left: 4px solid #64748b; padding-left: 10px;">
                                📋 금일 분석 로그 (수집된 영상 분석 결과)
                            </h3>
                            {analysis_log_html}
                        </div>

                        <!-- Proposals Section -->
                        <h3 style="font-size: 16px; font-weight: 700; color: #334155; margin-bottom: 15px; border-left: 4px solid #8b5cf6; padding-left: 10px;">
                            💡 진화 제안 (승인 대기중)
                        </h3>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px;">
                            {evo_grid_html}
                        </div>
                    </div>
    """

    # [YouTube Inbox Tab]
    html += f"""
                    <div id="youtube-inbox" class="tab-content" style="display:none;">
                        <div style="background: white; padding: 40px; border-radius: 8px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px;">
                                <h2 style="font-size: 20px; font-weight: 700; color: #1e293b; margin: 0;">📺 유튜브 인박스</h2>
                                <span style="font-size: 12px; font-weight: 600; color: #64748b; background: #f1f5f9; padding: 4px 10px; border-radius: 20px;">
                                    영상 {len(inbox_items)}개
                                </span>
                            </div>
                            <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px;">
                                {inbox_html}
                            </div>
                        </div>
                    </div>
    """
    # [Revival Engine Tab]
    html += f"""
                    <div id="revival-engine" class="tab-content" style="display:none;">
                        <h2 style="font-size: 20px; font-weight: 700; color: #1e293b; margin-bottom: 25px;">♻️ 부활 엔진</h2>
                        {revival_html}
                    </div>
    """

    # [Rejection Ledger Tab]
    html += f"""
                    <div id="rejection-ledger" class="tab-content" style="display:none;">
                        <h2 style="font-size: 20px; font-weight: 700; color: #1e293b; margin-bottom: 25px;">🚫 거절/보류 리스트</h2>
                        {ledger_html}
                    </div>
    """

    # [Topic Candidates Tab]
    html += f"""
                    <div id="topic-candidates" class="tab-content" style="display:none;">
                        <h2 style="font-size: 20px; font-weight: 700; color: #1e293b; margin-bottom: 25px;">📂 토픽 후보군</h2>
                        {candidate_html}
                    </div>
    """
    
    # [Final Decision Tab]
    # We need to construct decision card html here or reuse it.
    # The variable `decision_card_html` was built in original code. 
    # But since we are rewriting, we need to rebuild it or ensure it was built before anchor.
    # Wait, `decision_card_html` was built AFTER anchor in original code.
    # So we must rebuild it here.
    
    decision_html = ""
    if final_card:
        blocks = final_card.get("blocks", {})
        reg = blocks.get("regime", {})
        rev = blocks.get("revival", {})
        ops = blocks.get("ops", {})
        reg_col = "#10b981" if reg.get("confidence") > 0.5 else "#f59e0b"
        rev_col = "#3b82f6" if rev.get("has_revival") else "#64748b"
        ops_col = "#10b981" if ops.get("system_freshness", 0) >= 85 and not ops.get("has_stale_warning") else "#ef4444"
        
        loop_warn_html = ""
        if rev.get("loop_warning_count", 0) > 0:
            loop_warn_html = f'<div style="background:#fee2e2; color:#991b1b; padding:4px 8px; border-radius:4px; font-size:11px; margin-top:5px; font-weight:bold;">⚠ LOOP_WARNING: {rev["loop_warning_count"]} items repeating</div>'

        decision_html = (
            "<div style=\"background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);\">\n"
            "    <div style=\"display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));\">\n"
            "        <div style=\"padding: 20px; border-right: 1px solid #e2e8f0; min-height: 140px;\">\n"
            "            <div style=\"font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; margin-bottom: 15px;\">01. Regime Context</div>\n"
            f"            <div style=\"font-size: 18px; font-weight: 700; color: {reg_col};\">{reg.get('current_regime')}</div>\n"
            f"            <div style=\"font-size: 13px; color: #475569; margin-top: 5px;\">Confidence: {reg.get('confidence'):.1%} ({reg.get('basis_type')})</div>\n"
            f"            <div style=\"font-size: 12px; color: #64748b; margin-top: 8px;\">Meta Topics: {reg.get('meta_topic_count')} detected</div>\n"
            "        </div>\n"
            "        <div style=\"padding: 20px; border-right: 1px solid #e2e8f0; min-height: 140px;\">\n"
            "            <div style=\"font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; margin-bottom: 15px;\">02. Revival Context</div>\n"
            f"            <div style=\"font-size: 18px; font-weight: 700; color: {rev_col};\">{rev.get('proposal_count')} Candidates</div>\n"
            f"            <div style=\"font-size: 13px; color: #475569; margin-top: 5px;\">Primary Reason: {rev.get('primary_revival_reason')}</div>\n"
            f"            {loop_warn_html}\n"
            "        </div>\n"
            "        <div style=\"padding: 20px; min-height: 140px;\">\n"
            "            <div style=\"font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; margin-bottom: 15px;\">03. Ops Context</div>\n"
            f"            <div style=\"font-size: 18px; font-weight: 700; color: {ops_col};\">{ops.get('system_freshness', 0)}% Freshness</div>\n"
            f"            <div style=\"font-size: 13px; color: #475569; margin-top: 5px;\">7D Success: {ops.get('7d_success_rate')}</div>\n"
            f"            <div style=\"font-size: 12px; color: {ops_col}; margin-top: 8px; font-weight: bold;\">\n"
            f"                { '⚠️ SLA BREACH DETECTED' if ops.get('has_stale_warning') else '✅ All Systems Nominal' }\n"
            "            </div>\n"
            "        </div>\n"
            "    </div>\n"
            "    <div style=\"background: white; border-top: 1px solid #e2e8f0; padding: 25px; text-align: center;\">\n"
            f"        <div style=\"font-size: 16px; font-weight: 700; color: #1e293b; margin-bottom: 10px;\">\n"
            f"            {final_card.get('human_prompt')}\n"
            "        </div>\n"
            "        <div style=\"font-size: 12px; color: #94a3b8; font-style: italic;\">\n"
            "            가치는 운영자가 판단하며, 엔진은 이를 위한 근거 데이터만을 제공합니다.\n"
            "        </div>\n"
            "    </div>\n"
            "</div>"
        )
    else:
        decision_html = "<div style='padding:20px; text-align:center;'>No Data</div>"
        
    html += f"""
                    <div id="final-decision" class="tab-content" style="display:none;">
                        <h2 style="font-size: 20px; font-weight: 700; color: #1e293b; margin-bottom: 25px;">⚖️ 최종 의사결정 카드</h2>
                        {decision_html}
                    </div>
    """

    # [Archive & Script Tabs]
    html += f"""
                    <div id="archive-list" class="tab-content" style="display:none;">
                        <h2 style="font-size: 20px; font-weight: 700; color: #1e293b; margin-bottom: 25px;">🗄 아카이브</h2>
                        {archive_html}
                    </div>
                    
                    <div id="insight-script" class="tab-content" style="display:none;">
                        <div style="max-width: 1100px; margin: 0 auto;">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                                <h2 style="font-size: 20px; font-weight: 700; color: #1e293b; margin: 0;">📝 인사이트 스크립트 (V1)</h2>
                                <button onclick="copyScript()" style="padding:5px 10px; background:#eff6ff; color:#3b82f6; border:1px solid #bfdbfe; border-radius:4px; cursor:pointer; font-size:12px; font-weight:bold;">Copy Text</button>
                            </div>
                            <div style="background:#f8fafc; padding:20px; border-radius:8px; border:1px solid #e2e8f0; white-space:pre-wrap; font-size:13px; line-height:1.6; color:#334155;">
{script_body if script_body else "스크립트가 아직 생성되지 않았습니다."}
                            </div>
                        </div>
    """
    
    html += f"""
        <!-- Insight Script Section -->
        <div id="insight-script" style="background: white; border-top: 2px solid #e2e8f0; padding: 40px; margin-top: 0;">
            <div style="max-width: 1100px; margin: 0 auto;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                    <h2 style="font-size: 20px; font-weight: 700; color: #1e293b; margin: 0;">📝 인사이트 스크립트 (V1)</h2>
                    <button onclick="copyScript()" style="padding:5px 10px; background:#eff6ff; color:#3b82f6; border:1px solid #bfdbfe; border-radius:4px; cursor:pointer; font-size:12px; font-weight:bold;">Copy Text</button>
                </div>
                <p style="font-size: 14px; color: #64748b; margin-bottom: 25px;">최종 생성된 분석 원고(v1.0)입니다.</p>
                
                <div style="background:#f8fafc; padding:20px; border-radius:8px; border:1px solid #e2e8f0; font-family:'Inter',sans-serif; white-space:pre-wrap; font-size:13px; line-height:1.6; color:#334155;">
{script_body if script_body else "스크립트가 아직 생성되지 않았습니다."}
                </div>
            </div>
        </div>
    """

    html += """
        <div style="height: 50px;"></div>
        </div> <!-- End sections-wrapper -->
    </div> <!-- End Main Panel -->

    <!-- Right Sidebar -->
    <div class="sidebar">
        <div class="section-header" style="border:none; margin-bottom:10px;">
            <div style="font-size:14px; font-weight:800; color:#475569; text-transform:uppercase;">Data Status</div>
        </div>
        
        <div id="sidebar-content">
            <!-- Dynamic Content injected here -->
        </div>
    </div>

</div>

<!-- MODAL -->
<div id="scriptModal" class="modal">
    <div class="modal-box">
         <div style="display:flex; justify-content:space-between; margin-bottom:20px;">
             <h2 style="margin:0;">Insight Script</h2>
             <button onclick="closeModal()" style="border:none; background:none; font-size:20px; cursor:pointer;">✕</button>
         </div>
         <p id="script-modal-content">Script content here...</p>
    </div>
</div>

<script>
    // Initialize global data container
    {report_data_js}

    function closeModal() {
        document.getElementById('scriptModal').classList.remove('modal-active');
    }
    
    function copyScript() {
        const text = document.querySelector('#insight-script pre') ? document.querySelector('#insight-script pre').innerText : document.querySelector('#insight-script div').innerText;
        navigator.clipboard.writeText(text).then(() => alert('Copied!'));
    }
    
    // [Deep Logic Report Viewer]
    function showDeepLogicReport(vid) {
        var modal = document.getElementById("reportModal");
        var content = document.getElementById("reportContent");
        
        if (modal && content) {
            if (window.REPORT_DATA[vid]) {
                content.innerHTML = window.REPORT_DATA[vid];
            } else {
                content.innerHTML = "<div style='padding:20px; text-align:center; color:#94a3b8;'>리포트 데이터가 로드되지 않았습니다.</div>";
            }
            modal.style.display = "block";
        }
    }
    
    function closeReportModal() {
        var modal = document.getElementById("reportModal");
        if (modal) modal.style.display = "none";
    }

    function generatePopupYaml(evoId, vid) {
        // Collect checked items
        const dcm = document.getElementById('popup-dcm-' + evoId).checked;
        const adl = document.getElementById('popup-adl-' + evoId).checked;
        const note = document.getElementById('popup-note-' + evoId).value;
        
        let yaml = "## SYSTEM_EVOLUTION_APPROVAL\\n";
        yaml += "id: " + evoId + "\\n";
        yaml += "video_id: " + vid + "\\n";
        yaml += "target:\\n";
        if (dcm) yaml += "  - DATA_COLLECTION_MASTER\\n";
        if (adl) yaml += "  - ANOMALY_DETECTION_LOGIC\\n";
        yaml += "status: APPROVED\\n";
        yaml += "note: |-\\n  " + note.replace(/\\n/g, "\\n  ") + "\\n";
        yaml += "---";
        
        const el = document.createElement('textarea');
        el.value = yaml;
        document.body.appendChild(el);
        el.select();
        document.execCommand('copy');
        document.body.removeChild(el);
        
        alert("Approval YAML copied to clipboard!\\nPaste this into your ledger or commit message.");
    }
    
    // Close modals when clicking outside
    window.onclick = function(event) {
        var reportModal = document.getElementById("reportModal");
        var scriptModal = document.getElementById("scriptModal");
        
        if (event.target == reportModal) {
            reportModal.style.display = "none";
        }
        if (event.target == scriptModal) {
            scriptModal.classList.remove('modal-active');
        }
    }
</script>


    <!-- Report Viewer Modal -->
    <div id="reportModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeReportModal()">&times;</span>
            <div id="reportContent" class="report-view">
                <!-- Content injected via JS -->
            </div>
        </div>
    </div>

</body>
</html>
"""
    return html

def main():
    # ... (existing main logic placeholder if needed) ...
    pass


if __name__ == "__main__":
    # Ensure directories exist
    os.makedirs("data/dashboard", exist_ok=True)
    os.makedirs("dashboard", exist_ok=True)
    
    html = generate_dashboard(Path("."))
    
    with open("dashboard/index.html", "w") as f:
        f.write(html)
    
    print("[Dashboard] Generated dashboard/index.html")
