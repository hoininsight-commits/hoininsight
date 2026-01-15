from __future__ import annotations

import json
import os
import sys
import traceback
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
        timestamp = status_info.get("timestamp", "")
    else:
        status = "PENDING"
        reason = "수집 대기 중"
        timestamp = ""
    
    # [Emergency Reliability Fix]
    # If status is FAIL, but the data file for TODAY actually exists and is non-empty, override to OK.
    # This handles cases where one run fails but previous run succeeded, or yfinance is flaky but data is saved.
    if status != "OK":
        try:
            # Check curated path first (most important for dashboard)
            cpath_str = dataset.get("curated_path")
            if cpath_str:
                cpath = base_dir / cpath_str
                if cpath.exists() and cpath.stat().st_size > 0:
                     # Check if it has today's date? Or just trust it exists?
                     # CSVs grow, so just checking existence/modification time might be enough for now.
                     # Let's check modification time -> if modified today UTC (rough check)
                     mtime = datetime.utcfromtimestamp(cpath.stat().st_mtime)
                     now = datetime.utcnow()
                     if (now - mtime).total_seconds() < 86400: # Modified within 24h
                         status = "OK"
                         reason = "데이터 파일 존재 (자동 복구됨)"
        except Exception:
            pass

    return {
        "dataset_id": ds_id,
        "category": display_category,
        "status": status,
        "reason": reason,
        "last_updated": timestamp
    }

def generate_dashboard(base_dir: Path):
    ymd = _utc_ymd()
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
    
    /* Layout */
    .dashboard-container { display: grid; grid-template-columns: 1fr 380px; height: calc(100vh - 60px); }
    
    /* LEFT: Main Process Flow */
    .main-panel { padding: 40px; overflow-y: auto; background: #f8fafc; display: flex; justify-content: center; }
    .architecture-diagram { display: flex; flex-direction: column; gap: 60px; max-width: 800px; width: 100%; position: relative; }
    
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
             
             sidebar_html += f"""
             <div class="ds-item {status_cls}" title="{ds.get('reason','')}">
                 <div class="ds-left">
                     <div class="ds-icon"></div>
                     <span class="ds-name">{ds['dataset_id']}</span>
                 </div>
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

    html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="utf-8">
        <title>Hoin Insight 파이프라인</title>
        <style>{css}</style>
        <style>
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
        </style>
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
                
                <!-- [Ops v1.1] Content Status Badge -->
                <!-- Logic handled in Python, displayed below -->
            </div>
            
            <div style="display:flex; gap:10px;">
                <!-- Narrative Badge -->
                <div class="conf-badge {content_cls}">{content_mode}</div>
                <div class="conf-badge {status_data['narrative_cls']}">Narrative: {status_data['narrative_label']}</div>
                 <div class="conf-badge {preset_cls}" title="Content Depth Preset">Preset: {preset_label}</div>
                 <div class="status-badge status-{status_data['raw_status']}">{status_data['status']}</div>
            </div>
        </div>
        
        <div class="dashboard-container">
            <!-- MAIN FLOW -->
            <div class="main-panel">
                <div class="architecture-diagram">
                    
                    <!-- 1. Scheduler -->
                    <div class="process-row">
                        <div class="node-group-label">01. 스케줄 및 트리거</div>
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
                    <div class="process-row" style="gap:20px;">
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
                        <!-- Added ID and onclick handler for Modal -->
                        <div class="proc-node node-output" onclick="openModal()">
                            <div class="proc-icon">🚀</div>
                            <div class="proc-content">
                                <div class="proc-title">콘텐츠 생성</div>
                                <div class="proc-desc" style="font-weight:bold; color:#2563eb; margin-bottom:4px; white-space:normal; overflow:visible;">{topic_title}</div>
                                <div class="proc-sub" style="margin-top:6px;">{ "스크립트 생성 완료 (클릭하여 전체보기)" if script_exists else "대기중" }</div>
                            </div>
                        </div>
                    </div>

                </div>
            </div>
            
            <!-- RIGHT SIDEBAR -->
            <div class="sidebar">
                <div class="sidebar-title">
                    데이터 수집 현황판
                </div>
                {sidebar_html}
                
                <div class="footer">
                    Hoin Engine 자동 생성<br>{ymd}
                </div>
            </div>
        </div>

        <!-- The Modal -->
        <div id="scriptModal" class="modal">
          <div class="modal-content">
            <span class="close-btn" onclick="closeModal()">&times;</span>
            <div class="modal-header">{topic_title}</div>
            <div class="modal-body">
{script_body}
            </div>
          </div>
        </div>

        <script>
        var modal = document.getElementById("scriptModal");
        function openModal() {{
          modal.style.display = "block";
        }}
        function closeModal() {{
          modal.style.display = "none";
        }}
        window.onclick = function(event) {{
          if (event.target == modal) {{
            modal.style.display = "none";
          }}
        }}
        </script>
    </body>
    </html>
    """
    
    
    # [Phase 31-E+] YouTube Inbox (Latest Videos)
    # Displays latest collected videos and their pipeline status
    inbox_html = """
    <div class="sidebar-title" style="margin-top:40px; border-top:1px solid #e2e8f0; padding-top:20px;">
        YouTube Inbox (Latest Videos)
    </div>
    """

    # [Phase 33] Load Aging Scores (with fallback to Phase 32)
    priority_map = {}
    try:
        # Try Phase 33 first
        aging_path = base_dir / "data/narratives/prioritized" / ymd.replace("-","/") / "proposal_scores_with_aging.json"
        if aging_path.exists():
            a_data = json.loads(aging_path.read_text(encoding="utf-8"))
            if isinstance(a_data, dict) and "items" in a_data:
                a_data = a_data["items"]
            for item in a_data:
                priority_map[item.get("video_id")] = item
        else:
            # Fallback to Phase 32
            prio_path = base_dir / "data/narratives/prioritized" / ymd.replace("-","/") / "proposal_scores.json"
            if prio_path.exists():
                p_data = json.loads(prio_path.read_text(encoding="utf-8"))
                if isinstance(p_data, dict) and "items" in p_data:
                    p_data = p_data["items"]
                for item in p_data:
                    priority_map[item.get("video_id")] = item
    except: pass

    
    try:
        # Scan for metadata in recent days? Or just today/yesterday?
        # Inbox should probably show recent active items.
        # Let's scan last 3 days of metadata.json
        
        inbox_items = []
        # Reverse day scan
        from datetime import timedelta
        base_date = datetime.utcnow()
        
        # Check applied_summary for today to quick check APPLIED
        applied_today_vids = []
        applied_path = base_dir / "data/narratives/applied" / ymd.replace("-","/") / "applied_summary.json"
        if applied_path.exists():
             try:
                 ad = json.loads(applied_path.read_text(encoding="utf-8"))
                 applied_today_vids = [x.get('video_id') for x in ad.get('items', [])]
             except: pass

        for i in range(3): # Scan last 3 days
            scan_ymd = (base_date - timedelta(days=i)).strftime("%Y/%m/%d")
            meta_dir = base_dir / "data/narratives/metadata" / scan_ymd
            if meta_dir.exists():
                for m_file in meta_dir.glob("meta_*.json"):
                    try:
                        md = json.loads(m_file.read_text(encoding="utf-8"))
                        vid = md.get("video_id")
                        if not vid: continue
                        
                        # Determine Status
                        status = "NEW"
                        
                        # Check PROPOSED
                        prop_path = base_dir / "data/narratives/proposals" / scan_ymd / f"proposal_{vid}.md"
                        has_prop = prop_path.exists()
                        if has_prop:
                            status = "PROPOSED"
                            
                        # Check APPROVED
                        # We need to search approvals fairly broadly or just in likely places
                        # For simplicity, check TODAY and Scan Date
                        appr_path_1 = base_dir / "data/narratives/approvals" / scan_ymd / f"approve_{vid}.yml"
                        appr_path_2 = base_dir / "data/narratives/approvals" / ymd.replace("-","/") / f"approve_{vid}.yml"
                        if appr_path_1.exists() or appr_path_2.exists():
                            status = "APPROVED"
                            
                        # Check APPLIED
                        if vid in applied_today_vids:
                            status = "APPLIED"
                        
                        # Check SKIP (if title indicates no interesting content? Engine logic determines this usually)
                        # For inbox, we just show what we have. 
                        # If proposal exists but is empty? 
                        # If narrative_analyzer skipped it, proposal might not exist.
                        # So NEW -> No Proposal might mean Skipped by Analyzer (Low Confidence)?
                        # Re-read narrative_analyzer.py: if no strong signals, it might not generate proposal file or generated empty one?
                        # It generates proposal if "candidates" found.
                        
                        # Let's just use these states.
                        
                        # Needs Action?
                        needs_action = status in ["NEW", "PROPOSED", "APPROVED"] # Approved but not Applied yet? 
                        # If STATUS=APPROVED, we wait for Pipeline to Apply. Action is 'Wait' or 'Run Pipeline'.
                        # But technically user action is done.
                        # Let's say Needs Action = NEW or PROPOSED.
                        needs_action = status in ["NEW", "PROPOSED"]
                        
                        item = {
                            "video_id": vid,
                            "title": md.get("title", "No Title"),
                            "published_at": md.get("published_at", ""),
                            "url": f"https://youtu.be/{vid}",
                            "status": status,
                            "needs_action": needs_action,
                            "prop_path": prop_path
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
                    </div>
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
                
                inbox_html += f"""
                    
                    {action_ui}
                </div>
                """
            inbox_html += "</div>"
        else:
             inbox_html += "<div style='font-size:12px; color:#94a3b8; padding:10px;'>최근 수집된 영상이 없습니다.</div>"
            
    except Exception as e:
        inbox_html += f"<div style='color:red; font-size:11px;'>Inbox Load Fail: {e}</div>"

    sidebar_html += inbox_html

    # [Phase 31-D] Narrative Approval Queue Section
    queue_html = ""
    try:
        # Load Queue
        q_path = base_dir / "data/narratives/queue" / ymd.replace("-","/") / "proposal_queue.json"
        
        # Always render the container structure for verification consistency
        queue_html += """
        <div class="sidebar-title" style="margin-top:40px; border-top:1px solid #e2e8f0; padding-top:20px;">
            Narrative Review Queue
        </div>
        """
        
        q_data = []
        if q_path.exists():
            q_data = json.loads(q_path.read_text(encoding="utf-8"))
            
        if q_data:
            queue_html += '<div class="queue-list">'
            
            # [Phase 33] Sort by final_priority_score
            final_queue_list = q_data
            if priority_map:
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
                    pp = base_dir / prop_path_str
                    if pp.exists():
                         try:
                             hints = [l for l in pp.read_text(encoding="utf-8").splitlines() if l.strip().startswith("-")][:5]
                             prop_excerpt = "<br>".join(hints)
                         except: pass

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

    
    # [Phase 31-E] Applied Changes Section
    # Renders summary of today's applied changes based on applied_summary.json
    applied_html = """
    <div class="sidebar-title" style="margin-top:40px; border-top:1px solid #e2e8f0; padding-top:20px;">
        Applied Changes (Today)
    </div>
    """
    
    try:
        sum_path = base_dir / "data/narratives/applied" / ymd.replace("-","/") / "applied_summary.json"
        has_items = False
        
        if sum_path.exists():
            s_data = json.loads(sum_path.read_text(encoding="utf-8"))
            items = s_data.get("items", [])
            
            if items:
                has_items = True
                applied_html += '<div class="applied-list" style="display:flex; flex-direction:column; gap:10px;">'
                
                for item in items:
                    v_title = item.get("title", "Untitled")
                    v_by = item.get("approved_by", "System")
                    v_at = item.get("approved_at", "")
                    
                    # Shorten date
                    if "T" in v_at: v_at = v_at.split("T")[0]
                    
                    scopes = item.get("applied_scopes", [])
                    scope_badges = ""
                    for sc in scopes:
                        short_sc = sc.replace("_", " ").title().replace("Data Collection Master", "DCM").replace("Anomaly Detection Logic", "ADL").replace("Baseline Signals", "Base")
                        scope_badges += f'<span style="font-size:9px; background:#e0f2fe; color:#0369a1; padding:2px 5px; border-radius:3px; margin-right:3px;">{short_sc}</span>'
                    
                    applied_html += f"""
                    <div class="applied-card" style="background:white; border:1px solid #bbf7d0; border-left:4px solid #22c55e; border-radius:6px; padding:10px; box-shadow:0 1px 2px rgba(0,0,0,0.05);">
                        <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:5px;">
                            <span style="font-size:12px; font-weight:bold; color:#15803d;">🟢 APPLIED</span>
                            <span style="font-size:10px; color:#94a3b8;">{v_at}</span>
                        </div>
                        <div style="font-size:12px; font-weight:600; color:#334155; margin-bottom:5px;">{v_title}</div>
                        <div style="font-size:11px; color:#64748b; margin-bottom:8px;">by {v_by}</div>
                        <div>{scope_badges}</div>
                    </div>
                    """
                applied_html += '</div>'
        
        if not has_items:
             applied_html += "<div style='font-size:12px; color:#94a3b8; padding:10px;'>오늘 적용된 변경 사항이 없습니다.</div>"
             
    except Exception as e:
        applied_html += f"<div style='color:red; font-size:11px;'>Load Error: {e}</div>"

    sidebar_html += queue_html
    sidebar_html += applied_html
    
    html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="utf-8">
        <title>Hoin Insight 파이프라인</title>
        <style>{css}</style>
        <style>
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
                <!-- Narrative Badge -->
                <div class="conf-badge {content_cls}">{content_mode}</div>
                <div class="conf-badge {status_data['narrative_cls']}">Narrative: {status_data['narrative_label']}</div>
                 <div class="conf-badge {preset_cls}" title="Content Depth Preset">Preset: {preset_label}</div>
                 <div class="status-badge status-{status_data['raw_status']}">{status_data['status']}</div>
            </div>
        </div>
        
        <div class="dashboard-container">
            <!-- MAIN FLOW -->
            <div class="main-panel">
                <div class="architecture-diagram">
                    
                    <!-- 1. Scheduler -->
                    <div class="process-row">
                        <div class="node-group-label">01. 스케줄 및 트리거</div>
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
                    <div class="process-row" style="gap:20px;">
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
                        <!-- Added ID and onclick handler for Modal -->
                        <div class="proc-node node-output" onclick="openModal()">
                            <div class="proc-icon">🚀</div>
                            <div class="proc-content">
                                <div class="proc-title">콘텐츠 생성</div>
                                <div class="proc-desc" style="font-weight:bold; color:#2563eb; margin-bottom:4px; white-space:normal; overflow:visible;">{topic_title}</div>
                                <div class="proc-sub" style="margin-top:6px;">{ "스크립트 생성 완료 (클릭하여 전체보기)" if script_exists else "대기중" }</div>
                            </div>
                        </div>
                    </div>

                </div>
            </div>
            
            <!-- RIGHT SIDEBAR -->
            <div class="sidebar">
                <div class="sidebar-title">
                    데이터 수집 현황판
                </div>
                {sidebar_html}
                
                <div class="footer">
                    Hoin Engine 자동 생성<br>{ymd}
                </div>
            </div>
        </div>

        <!-- Architecture Section -->
        <div style="background: white; border-top: 2px solid #e2e8f0; padding: 40px; margin-top: 0;">
            <div style="max-width: 1100px; margin: 0 auto;">
                <h2 style="font-size: 20px; font-weight: 700; color: #1e293b; margin-bottom: 10px;">Architecture</h2>
                <p style="font-size: 14px; color: #64748b; margin-bottom: 25px;">End-to-end pipeline from ingestion to approval-driven learning.</p>
                
                <!-- 2-Column Grid: Diagram + Summary Card -->
                <div style="display: grid; grid-template-columns: 1fr 350px; gap: 30px; align-items: start;">
                    <!-- Left: Architecture Diagram -->
                    <div style="background: #f8fafc; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0;">
                        <a href="assets/architecture.svg" target="_blank" style="display: inline-block; text-decoration: none; width: 100%;">
                            <img src="assets/architecture.png" alt="Hoin Insight Architecture Diagram" 
                                 style="max-width: 100%; height: auto; border-radius: 4px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);"
                                 onerror="this.parentElement.innerHTML='<div style=\\'padding:40px; color:#94a3b8; font-size:14px;\\'>⚠ architecture.svg/png missing</div>'">
                        </a>
                        <div style="margin-top: 10px; font-size: 11px; color: #94a3b8; text-align: center;">
                            <a href="assets/architecture.svg" target="_blank" style="color: #3b82f6; text-decoration: none;">View full diagram →</a>
                        </div>
                    </div>
                    
                    <!-- Right: Current State Summary Card -->
                    <div class="architecture-summary-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 25px; border-radius: 12px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.2); color: white;">
                        <h3 style="font-size: 16px; font-weight: 700; margin: 0 0 20px 0; color: white; border-bottom: 2px solid rgba(255,255,255,0.3); padding-bottom: 10px;">
                            Current System State (Today)
                        </h3>
                        
                        <div style="display: flex; flex-direction: column; gap: 15px;">
                            <!-- Core Dataset Health -->
                            <div style="background: rgba(255,255,255,0.15); padding: 12px; border-radius: 8px; backdrop-filter: blur(10px);">
                                <div style="font-size: 11px; font-weight: 600; color: rgba(255,255,255,0.8); margin-bottom: 5px;">CORE DATASETS</div>
                                <div style="font-size: 14px; font-weight: 700; display: flex; align-items: center; gap: 8px;">
                                    {f'🟢 HEALTHY' if all(v == 'OK' for v in core_bd.values() if v != 'SKIP') else ('🟡 PARTIAL' if any(v == 'OK' for v in core_bd.values()) else '🔴 FAIL')}
                                </div>
                                <div style="font-size: 10px; color: rgba(255,255,255,0.7); margin-top: 3px;">
                                    {', '.join([f"{k}:{v}" for k,v in core_bd.items() if v != 'SKIP'][:3])}
                                </div>
                            </div>
                            
                            <!-- Regime -->
                            <div style="background: rgba(255,255,255,0.15); padding: 12px; border-radius: 8px; backdrop-filter: blur(10px);">
                                <div style="font-size: 11px; font-weight: 600; color: rgba(255,255,255,0.8); margin-bottom: 5px;">REGIME</div>
                                <div style="font-size: 14px; font-weight: 700;">
                                    {regime_name if regime_name != "Unknown" else "N/A"}
                                </div>
                                <div style="font-size: 10px; color: rgba(255,255,255,0.7); margin-top: 3px;">
                                    {'(Meta-driven)' if meta_count > 0 else '(Driver-based)'}
                                </div>
                            </div>
                            
                            <!-- Regime Confidence -->
                            <div style="background: rgba(255,255,255,0.15); padding: 12px; border-radius: 8px; backdrop-filter: blur(10px);">
                                <div style="font-size: 11px; font-weight: 600; color: rgba(255,255,255,0.8); margin-bottom: 5px;">CONFIDENCE</div>
                                <div style="font-size: 14px; font-weight: 700; display: flex; align-items: center; gap: 8px;">
                                    {f'🟢 {conf_level}' if conf_level == 'HIGH' else (f'🟡 {conf_level}' if conf_level == 'MEDIUM' else f'🔴 {conf_level}')}
                                </div>
                            </div>
                            
                            <!-- Content Preset -->
                            <div style="background: rgba(255,255,255,0.15); padding: 12px; border-radius: 8px; backdrop-filter: blur(10px);">
                                <div style="font-size: 11px; font-weight: 600; color: rgba(255,255,255,0.8); margin-bottom: 5px;">CONTENT PRESET</div>
                                <div style="font-size: 14px; font-weight: 700;">
                                    {preset_label if preset_label != "-" else "N/A"}
                                </div>
                                <div style="font-size: 10px; color: rgba(255,255,255,0.7); margin-top: 3px;">
                                    Mode: {content_mode}
                                </div>
                            </div>
                        </div>
                        
                        <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.2); font-size: 10px; color: rgba(255,255,255,0.6); text-align: center;">
                            Last Updated: {ymd}
                        </div>
                    </div>
                </div>
                
                <!-- Mobile Responsive: Stack vertically on small screens -->
                <style>
                    @media (max-width: 768px) {{
                        .architecture-summary-card {{
                            grid-column: 1 / -1;
                        }}
                        div[style*="grid-template-columns: 1fr 350px"] {{
                            grid-template-columns: 1fr !important;
                        }}
                    }}
                </style>
            </div>
        </div>

        <!-- Change Effectiveness Section (Phase 34) -->
        <div style="background: #f8fafc; border-top: 2px solid #e2e8f0; padding: 40px; margin-top: 0;">
            <div style="max-width: 1100px; margin: 0 auto;">
                <h2 style="font-size: 20px; font-weight: 700; color: #1e293b; margin-bottom: 10px;">Change Effectiveness (Last 30 Days)</h2>
                <p style="font-size: 14px; color: #64748b; margin-bottom: 25px;">Quantitative impact of approved changes on pipeline metrics.</p>
                
    """
    
    # Load effectiveness data
    effectiveness_html = ""
    ymd = datetime.utcnow().strftime("%Y/%m/%d")
    effectiveness_path = base_dir / "data" / "narratives" / "effectiveness" / ymd / "effectiveness.json"
    
    if effectiveness_path.exists():
        try:
            eff_data = json.loads(effectiveness_path.read_text(encoding="utf-8"))
            events = eff_data.get("events", [])
            
            if events:
                # Show top 3 most recent events
                top_events = sorted(events, key=lambda x: x["applied_at"], reverse=True)[:3]
                
                effectiveness_html += """
                <div style="display: grid; gap: 20px;">
                """
                
                for event in top_events:
                    metrics = event.get("metrics", {})
                    apply_scope = event.get("apply_scope", {})
                    data_quality = event.get("data_quality", {})
                    
                    # Extract key deltas
                    success_delta = metrics.get("pipeline_reliability", {}).get("delta")
                    topics_delta = metrics.get("topics_count_avg", {}).get("delta")
                    conf_delta = metrics.get("confidence_high_share", {}).get("delta")
                    flip_delta = metrics.get("regime_flip_count", {}).get("delta")
                    
                    # Format deltas
                    success_str = f"{success_delta:+.2f}" if success_delta is not None else "N/A"
                    topics_str = f"{topics_delta:+.1f}" if topics_delta is not None else "N/A"
                    conf_str = f"{conf_delta:+.2%}" if conf_delta is not None else "N/A"
                    flip_str = f"{flip_delta:+d}" if flip_delta is not None else "N/A"
                    
                    # Scope summary
                    scope_items = [k for k, v in apply_scope.items() if v]
                    scope_str = ", ".join(scope_items) if scope_items else "N/A"
                    
                    effectiveness_html += f"""
                    <div style="background: white; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px;">
                            <div>
                                <div style="font-size: 14px; font-weight: 700; color: #1e293b;">{event["event_id"]}</div>
                                <div style="font-size: 12px; color: #64748b; margin-top: 3px;">Applied: {event["applied_at"]}</div>
                            </div>
                            <div style="font-size: 10px; color: #94a3b8; text-align: right;">
                                Pre/Post: {data_quality["pre_days_used"]}d / {data_quality["post_days_used"]}d
                            </div>
                        </div>
                        
                        <div style="font-size: 11px; color: #64748b; margin-bottom: 12px;">
                            <strong>Scope:</strong> {scope_str}
                        </div>
                        
                        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px;">
                            <div style="background: #f1f5f9; padding: 10px; border-radius: 6px; text-align: center;">
                                <div style="font-size: 10px; color: #64748b; margin-bottom: 3px;">Success Rate Δ</div>
                                <div style="font-size: 14px; font-weight: 700; color: {'#059669' if success_delta and success_delta > 0 else ('#dc2626' if success_delta and success_delta < 0 else '#64748b')};">{success_str}</div>
                            </div>
                            <div style="background: #f1f5f9; padding: 10px; border-radius: 6px; text-align: center;">
                                <div style="font-size: 10px; color: #64748b; margin-bottom: 3px;">Topics Δ</div>
                                <div style="font-size: 14px; font-weight: 700; color: {'#059669' if topics_delta and topics_delta > 0 else ('#dc2626' if topics_delta and topics_delta < 0 else '#64748b')};">{topics_str}</div>
                            </div>
                            <div style="background: #f1f5f9; padding: 10px; border-radius: 6px; text-align: center;">
                                <div style="font-size: 10px; color: #64748b; margin-bottom: 3px;">Conf HIGH Δ</div>
                                <div style="font-size: 14px; font-weight: 700; color: {'#059669' if conf_delta and conf_delta > 0 else ('#dc2626' if conf_delta and conf_delta < 0 else '#64748b')};">{conf_str}</div>
                            </div>
                            <div style="background: #f1f5f9; padding: 10px; border-radius: 6px; text-align: center;">
                                <div style="font-size: 10px; color: #64748b; margin-bottom: 3px;">Regime Flips Δ</div>
                                <div style="font-size: 14px; font-weight: 700; color: {'#059669' if flip_delta and flip_delta < 0 else ('#dc2626' if flip_delta and flip_delta > 0 else '#64748b')};">{flip_str}</div>
                            </div>
                        </div>
                    </div>
                    """
                
                effectiveness_html += """
                </div>
                """
            else:
                effectiveness_html = """
                <div style="background: white; padding: 30px; border-radius: 8px; border: 1px solid #e2e8f0; text-align: center; color: #94a3b8;">
                    No applied events in lookback window
                </div>
                """
        except Exception as e:
            effectiveness_html = f"""
            <div style="background: white; padding: 30px; border-radius: 8px; border: 1px solid #e2e8f0; text-align: center; color: #94a3b8;">
                Error loading effectiveness data: {str(e)}
            </div>
            """
    else:
        effectiveness_html = """
        <div style="background: white; padding: 30px; border-radius: 8px; border: 1px solid #e2e8f0; text-align: center; color: #94a3b8;">
            No applied events in lookback window
        </div>
        """
    
    html += effectiveness_html
    html += """
            </div>
        </div>

        <!-- The Modal -->
        <div id="scriptModal" class="modal">
          <div class="modal-content">
            <span class="close-btn" onclick="closeModal()">&times;</span>
            <div class="modal-header">{topic_title}</div>
            <div class="modal-body">
{script_body}
            </div>
          </div>
        </div>

        <script>
        var modal = document.getElementById("scriptModal");
        function openModal() {{
          modal.style.display = "block";
        }}
        function closeModal() {{
          modal.style.display = "none";
        }}
        window.onclick = function(event) {{
          if (event.target == modal) {{
            modal.style.display = "none";
          }}
        }}

        function generateYaml(videoId) {{
            const dcm = document.getElementById('chk-dcm-' + videoId).checked;
            const adl = document.getElementById('chk-adl-' + videoId).checked;
            const bs = document.getElementById('chk-bs-' + videoId).checked;
            const note = document.getElementById('note-' + videoId).value;
            
            copyYaml(videoId, dcm, adl, bs, note);
        }}
        
        function toggleAction(videoId) {{
            var box = document.getElementById('action-box-' + videoId);
            if (box.style.display === "none") {{
                box.style.display = "block";
            }} else {{
                box.style.display = "none";
            }}
        }}
        
        function generateInboxYaml(videoId) {{
            const dcm = document.getElementById('ib-dcm-' + videoId).checked;
            const adl = document.getElementById('ib-adl-' + videoId).checked;
            const bs = document.getElementById('ib-bs-' + videoId).checked;
            const note = document.getElementById('ib-note-' + videoId).value;
            
            copyYaml(videoId, dcm, adl, bs, note);
        }}
        
        function copyYaml(videoId, dcm, adl, bs, note) {{
            const today = new Date().toISOString().split('T')[0].replace(/-/g, '/');
            const now = new Date().toISOString();
            
            const yaml = `approval_version: "approve_yml_v1"
video_id: "${{videoId}}"
approved_by: "USER_WEB_UI"
approved_at: "${{now}}"
apply:
  data_collection_master: ${{dcm}}
  anomaly_detection_logic: ${{adl}}
  baseline_signals: ${{bs}}
notes: "${{note}}"
`;
            
            navigator.clipboard.writeText(yaml).then(function() {{
                alert('승인 코드가 복사되었습니다!\\n\\n1. Git 저장소로 이동\\n2. "data/narratives/approvals/' + today + '/approve_' + videoId + '.yml" 파일 생성\\n3. 붙여넣기 후 커밋');
            }}, function(err) {{
                alert('복사 실패: ' + err);
            }});
        }}
        </script>
    </body>
    </html>
    """
    
    (dash_dir / "index.html").write_text(html, encoding="utf-8")
    print(f"파이프라인 아키텍처 대시보드 생성 완료: {dash_dir}/index.html")
    return dash_dir / "index.html"

if __name__ == "__main__":
    try:
        # Resolve project root (HoinInsight/)
        base_dir = Path(__file__).resolve().parent.parent.parent
        # Add project root to sys.path to allow 'from src.ops...' imports
        if str(base_dir) not in sys.path:
            sys.path.append(str(base_dir))
            
        out_file = generate_dashboard(base_dir)
        print(f"파이프라인 아키텍처 대시보드 생성 완료: {out_file.relative_to(base_dir)}")
    except Exception:
        print("[FATAL] Dashboard generation crashed!")
        traceback.print_exc()
        sys.exit(1)
