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
    
    # Status Translation
    status_str = "SUCCESS" if total_fail == 0 else "PARTIAL" if total_ok > 0 else "FAIL"
    status_map = {"SUCCESS": "성공", "PARTIAL": "부분 성공", "FAIL": "실패"}
    display_status = status_map.get(status_str, status_str)

    status_data = {
        "run_date": ymd,
        "run_id": os.environ.get("GITHUB_RUN_ID", "local"),
        "status": display_status,
        "raw_status": status_str
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
                 <div class="conf-badge {content_cls}">Content: {content_mode}</div>
                 <div class="conf-badge {preset_cls}" title="Content Depth Preset">Preset: {preset_label}</div>
                 <div class="status-badge status-{status_data['status']}">{status_data['status']}</div>
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
    
    (dash_dir / "index.html").write_text(html, encoding="utf-8")
    print(f"파이프라인 아키텍처 대시보드 생성 완료: {dash_dir}/index.html")

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
