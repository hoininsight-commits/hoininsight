from __future__ import annotations

import json
import os
import logging
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List
from src.utils.markdown_parser import parse_markdown
from src.utils.i18n_ko import I18N_KO

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


def _load_historical_cards(base_dir: Path) -> List[Dict]:
    """Load all historical final_decision_card.json files"""
    cards = []
    decision_dir = base_dir / "data" / "decision"
    if not decision_dir.exists():
        return []
    
    # Recursive search
    for card_file in decision_dir.glob("**/*/final_decision_card.json"):
        try:
            data = json.loads(card_file.read_text(encoding="utf-8"))
            # Extract date from path or card content
            # Path format: data/decision/YYYY/MM/DD/final_decision_card.json
            parts = card_file.parts
            if len(parts) >= 5:
                # Approximate date extraction from path
                ymd = f"{parts[-4]}-{parts[-3]}-{parts[-2]}"
                data['_date'] = ymd
            cards.append(data)
        except: pass
    
    # Sort by date desc
    cards.sort(key=lambda x: x.get('_date', ''), reverse=True)
    return cards

def _generate_archive_view(cards: List[Dict]) -> str:
    """Generate HTML Table for Topic Archive with Top 5 Detail Support"""
    if not cards:
        return '<div style="padding:40px; text-align:center; color:#94a3b8;">저장된 과거 데이터가 없습니다.</div>'

    # Prepare Data for JS Modal
    topic_details_map = {}
    
    table_rows = ""
    
    for card_idx, c in enumerate(cards):
        date = c.get('_date', 'Unknown')
        
        # Determine Topic List (Top 5 or Single Fallback)
        top_topics = c.get("top_topics", [])
        if not top_topics:
            # Fallback to single topic structure
            single_topic = c.get('topic')
            if not single_topic:
                 # Check narrative fallback
                 n_topics = c.get('narrative_topics', [])
                 if n_topics:
                     # Create a pseudo-topic dict from narrative
                     top_topics = [{
                         "title": n_topics[0].get('topic_anchor'),
                         "level": "Narrative",
                         "rationale": n_topics[0].get('core_narrative'),
                         "evidence": {"details": {"value": "N/A", "reasoning": "Narrative Engine Output"}}
                     }]
            else:
                # Create a pseudo-topic from the flat card
                top_topics = [{
                    "title": single_topic,
                    "level": c.get('level', 'L2'),
                    "rationale": c.get('decision_rationale', ''),
                    "leader_stocks": c.get('leader_stocks', []),
                    "evidence": c.get('raw_data', {}).get('evidence', {})
                }]

        # Generate Rows for this Date
        for t_idx, topic in enumerate(top_topics):
            # Unique ID for Modal
            topic_uid = f"t_{card_idx}_{t_idx}"
            
            title = topic.get("title", "Untitled Topic")
            level = topic.get("level", "L2")
            rationale = topic.get("rationale", "No rationale provided.")
            
            # Formatting Evidence
            evidence = topic.get("evidence", {})
            evidence_html = ""
            if isinstance(evidence, dict):
                details = evidence.get("details", {})
                if details:
                    evidence_html += "<div style='background:#f8fafc; padding:10px; border-radius:6px; margin-top:10px; font-size:12px; border:1px solid #e2e8f0;'>"
                    evidence_html += f"<strong>📊 {I18N_KO['DATA_EVIDENCE']}</strong><br>"
                    evidence_html += f"{I18N_KO['VALUE']}: {details.get('value', 'N/A')}<br>"
                    evidence_html += f"Z-Score: {details.get('z_score', 'N/A')}<br>"
                    evidence_html += f"Analyst Note: {details.get('reasoning', '')}"
                    evidence_html += "</div>"
            
            # Formatting Leader Stocks
            stocks = topic.get("leader_stocks", [])
            stocks_html = ""
            if stocks:
                s_tags = "".join([f"<span style='background:#f0fdf4; color:#166534; padding:2px 6px; border-radius:4px; margin-right:4px; font-size:11px; font-weight:bold;'>{s}</span>" for s in stocks])
                stocks_html = f"<div style='margin-top:10px;'><strong>🚀 {I18N_KO['LEADER_STOCKS']}:</strong><br><div style='margin-top:4px;'>{s_tags}</div></div>"

            # Construct Modal Content
            modal_content = f"""
                <div style="border-bottom:1px solid #e2e8f0; padding-bottom:15px; margin-bottom:15px;">
                    <div style="font-size:12px; color:#64748b; margin-bottom:4px;">{date} / Rank #{t_idx+1}</div>
                    <h3 style="margin:0; font-size:18px; color:#1e293b;">{title}</h3>
                </div>
                <div style="font-size:14px; color:#334155; line-height:1.6;">
                    <strong style="color:#0f172a;">💡 {I18N_KO['RATIONALE']}</strong>
                    <p style="margin-top:4px; background:#fffbeb; padding:10px; border-radius:6px; border:1px solid #fcd34d;">{rationale}</p>
                    {evidence_html}
                    {stocks_html}
                </div>
            """
            topic_details_map[topic_uid] = modal_content
            
            # Badge Style
            type_badge = '<span style="background:#dbeafe; color:#1e40af; padding:2px 6px; border-radius:4px; font-size:11px;">구조적</span>'
            if str(level).lower() == "narrative":
                 type_badge = '<span style="background:#f3e8ff; color:#6b21a8; padding:2px 6px; border-radius:4px; font-size:11px;">내러티브</span>'
            
            # Row HTML
            # Only show date on the first item of the day (rowspan logic is hard in flat loop, so just show empty or repeat)
            # We'll just repeat date for clarity or make it lighter
            date_display = f"<strong>{date}</strong>" if t_idx == 0 else f"<span style='color:#cbd5e1; font-size:11px;'>{date}</span>"
            
            table_rows += f"""
            <tr style="border-bottom:1px solid #f1f5f9; cursor:pointer;" onmouseover="this.style.background='#f8fafc'" onmouseout="this.style.background='white'" onclick="showArchiveDetail('{topic_uid}')">
                <td style="padding:12px; color:#334155;">{date_display}</td>
                <td style="padding:12px;">
                    <div style="font-weight:600; color:#1e293b; font-size:13px;">{title}</div>
                    <div style="font-size:11px; color:#64748b; margin-top:2px;">Rank #{t_idx+1}</div>
                </td>
                <td style="padding:12px;">{type_badge}</td>
                <td style="padding:12px; text-align:right;">
                    <button style="border:1px solid #cbd5e1; background:white; color:#64748b; padding:4px 8px; border-radius:4px; font-size:11px; cursor:pointer;">{I18N_KO['VIEW']}</button>
                </td>
            </tr>
            """

    html = f"""
    <div id="topic-archive" class="tab-content" style="display:none; width:100%;">
        <h2 style="font-size:18px; font-weight:700; color:#334155; margin-bottom:20px;">📅 일별 아카이브 (Daily Topic History)</h2>
        <div style="background:white; border-radius:8px; border:1px solid #e2e8f0; overflow:hidden;">
            <table style="width:100%; border-collapse:collapse; font-size:13px;">
                <thead style="background:#f8fafc; border-bottom:1px solid #e2e8f0;">
                    <tr>
                        <th style="padding:12px; text-align:left; color:#64748b; font-weight:600; width:90px;">{I18N_KO['DATE']}</th>
                        <th style="padding:12px; text-align:left; color:#64748b; font-weight:600;">선정 토픽 (Top 5)</th>
                        <th style="padding:12px; text-align:left; color:#64748b; font-weight:600; width:70px;">{I18N_KO['TYPE']}</th>
                        <th style="padding:12px; text-align:right; color:#64748b; font-weight:600; width:60px;">{I18N_KO['DETAIL']}</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>
    </div>
    
    <!-- Topic Detail Modal & Scripts -->
    <div id="topicDetailModal" class="modal">
        <div class="modal-content" style="max-width:600px;">
            <span class="close-btn" onclick="closeTopicModal()">&times;</span>
            <div id="topic-detail-content"></div>
        </div>
    </div>

    <script>
        window.TOPIC_DETAILS = {json.dumps(topic_details_map)};
        
        function showArchiveDetail(uid) {{
            var content = window.TOPIC_DETAILS[uid];
            if(content) {{
                document.getElementById('topic-detail-content').innerHTML = content;
                document.getElementById('topicDetailModal').style.display = 'block';
            }}
        }}
        
        function closeTopicModal() {{
            document.getElementById('topicDetailModal').style.display = 'none';
        }}
        
        // Close on outside click
        window.addEventListener('click', function(e) {{
            var accModal = document.getElementById('topicDetailModal');
            if (e.target == accModal) {{
                accModal.style.display = 'none';
            }}
        }});
    </script>
    """
    return html

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
        card_base = base_dir / "data" / "decision" / ymd.replace("-","/")
        card_path = card_base / "final_decision_card.json"
        if card_path.exists():
            final_card = json.loads(card_path.read_text(encoding="utf-8"))
    except: pass

    # [Phase 40] Load Topic Gate Output
    gate_data = {}
    try:
        gate_base = base_dir / "data" / "topics" / "gate" / ymd.replace("-", "/")
        gate_path = gate_base / "topic_gate_output.json"
        if gate_path.exists():
            gate_data = json.loads(gate_path.read_text(encoding="utf-8"))
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
    
    # [Phase 42] Load Synthesized Topic (Content Topic)
    synth_topic = {}
    try:
        synth_path = base_dir / "data" / "topics" / "synthesized" / ymd.replace("-","/") / "synth_topic_v1.json"
        if synth_path.exists():
            synth_topic = json.loads(synth_path.read_text(encoding="utf-8"))
    except: pass
    
    # [Fix] Point to the correct date-based insight script for the Main View
    # Standard reports directory for daily brief/scripts
    script_path = base_dir / "data" / "reports" / ymd.replace("-","/") / "daily_brief.md"
    script_exists = script_path.exists()
    
    # Fallback to older path if needed
    if not script_exists:
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
    topic_title = final_card.get('topic')
    
    # Check for Narrative Topics if Structural is missing
    narrative_topics = final_card.get('narrative_topics', [])
    
    if not topic_title:
        if narrative_topics:
            topic_title = f"Narrative Candidates Found ({len(narrative_topics)})"
            # Use the first narrative topic as the rationale preview
            top_nt = narrative_topics[0]
            rationale = f"<b>[Narrative] {top_nt.get('topic_anchor')}</b><br>{top_nt.get('core_narrative')}<br><br>(Structural Topic은 감지되지 않았습니다)"
        else:
            topic_title = '분석 결과 대기 중...'
            rationale = final_card.get('decision_rationale', '아직 오늘의 주제가 선정되지 않았습니다.<br>잠시 후 다시 확인해주세요.')
    else:
        rationale = final_card.get('decision_rationale', 'Rationale loading...')

    key_data_html = '<span style="font-size:10px; color:#cbd5e1;">데이터 없음</span>'
    if final_card.get('key_data'):
        # List comprehension outside f-string
        spans = [f'<span style="font-size:10px; background:#f8fafc; border:1px solid #e2e8f0; padding:2px 8px; border-radius:4px; color:#64748b;">{k}</span>' for k in final_card.get('key_data', {}).keys()]
        key_data_html = ''.join(spans)

    script_preview = '스크립트 생성 대기 중...'
    if script_body:
        script_preview = script_body[:800] + '...' if len(script_body) > 800 else script_body

    leader_stocks_html = ""
    # Main topic is top_topics[0] if it exists in final_card
    the_top_topics = final_card.get("top_topics", [])
    if the_top_topics:
        main_topic_meta = the_top_topics[0]
        stocks = main_topic_meta.get("leader_stocks", [])
        if stocks:
            stock_spans = [f'<span style="font-size:11px; background:#f0fdf4; border:1px solid #bbf7d0; padding:4px 12px; border-radius:20px; color:#166534; font-weight:700;">{s}</span>' for s in stocks]
            leader_stocks_html = '<div style="margin-top:20px;"><h4 style="font-size:12px; font-weight:700; color:#166534; margin-bottom:10px;">🚀 관련 테마 대장주</h4><div style="display:flex; flex-wrap:wrap; gap:8px;">' + ''.join(stock_spans) + '</div></div>'

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
    
    .stat-counter { background: white; border: 1px solid #e2e8f0; padding: 4px 12px; border-radius: 6px; font-size: 12px; font-weight: 600; color: #475569; display: flex; align-items: center; gap: 6px; }
    
    .advanced-toggle { margin-top: auto; padding: 15px 25px; cursor: pointer; display: flex; align-items: center; justify-content: space-between; color: #475569; font-size: 12px; font-weight: 700; border-top: 1px solid #1e293b; background: #0f172a; }
    .advanced-toggle:hover { color: #f1f5f9; background: #1e293b; }
    .advanced-content { display: none; background: #0b1120; }
    .advanced-content.open { display: block; }
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
                                        needs_action = False  # I18N_KO["NO_ACTION_NEEDED_IF_DECISIONED"]
                                
                                # Needs Action?
                                needs_action = status in [I18N_KO["NEW"], I18N_KO["PROPOSED"]]
                                
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
                            <input type="checkbox" onchange="toggleAction('{vid}')" style="margin-right:5px;"> {I18N_KO['LEARNING_NEEDED']}?
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
                        { f" <span style='color:#3b82f6; font-weight:bold; margin-left:5px;'>✨ {I18N_KO['ANALYSIS_DONE']}</span>" if it.get('has_deep') else "" }
                        { f" <span style='color:#8b5cf6; font-weight:bold; margin-left:5px;'>🚀 {I18N_KO['EVOLUTION_NEEDED']} ({it['evo_count']})</span>" if it.get('evo_count', 0) > 0 else "" }
                        { f" <span style='color:#ef4444; font-weight:bold; margin-left:5px;'>⚠ {I18N_KO['STALE_DATA_WARNING']}</span>" if freshness_summary.get('sla_breach_count', 0) > 0 else "" }
                    </div>
                    <button onclick="showDeepLogicReport('{vid}')" style="width:100%; margin-top:10px; background:#f8fafc; border:1px solid #cbd5e1; padding:6px; border-radius:4px; font-size:11px; cursor:pointer; font-weight:bold; color:#475569;" onmouseover="this.style.background='#f1f5f9'" onmouseout="this.style.background='#f8fafc'">
                        {I18N_KO['VIEW_ANALYSIS_ACTION']}
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

    # [Narrative Layer] Load Narrative Topics
    narrative_cards_html = ""
    narrative_data_js = "window.NARRATIVE_DATA = {};"
    
    narr_topics_path = base_dir / "data" / "reports" / ymd.replace("-","/") / "narrative_topics.json"
    if narr_topics_path.exists():
        try:
            nt_data = json.loads(narr_topics_path.read_text(encoding='utf-8'))
            topics = nt_data.get("topics", [])
            
            if topics:
                for t in topics:
                    tid = t['topic_id']
                    # Escape for JS
                    t_json = json.dumps(t, ensure_ascii=False)
                    narrative_data_js += f"window.NARRATIVE_DATA['{tid}'] = {t_json};\n"
                    
                    script_prev = t.get('script_kr', '').replace('\n', ' ')[:100] + "..."
                    
                    narrative_cards_html += f"""
                    <div style="background:white; border:1px solid #e2e8f0; border-radius:12px; overflow:hidden; box-shadow:0 4px 6px -1px rgba(0,0,0,0.05); transition:transform 0.2s; cursor:pointer;" 
                         onmouseover="this.style.transform='translateY(-2px)'" 
                         onmouseout="this.style.transform='translateY(0)'"
                         onclick="openNarrativeModal('{tid}')">
                         
                         <div style="background:#5b21b6; padding:15px; color:white;">
                        <div style="font-size:10px; font-weight:bold; opacity:0.8; margin-bottom:5px;">OPEN CANDIDATE</div>
                        <h3 style="margin:0; font-size:16px; line-height:1.4;">{t['topic_anchor']}</h3>
                     </div>
                         <div style="padding:20px;">
                            <div style="margin-bottom:10px;">
                                <div style="font-size:11px; font-weight:bold; color:#64748b;">DRIVER</div>
                                <div style="font-size:13px; color:#1e293b; font-weight:600;">{t['narrative_driver']}</div>
                            </div>
                            <div style="font-size:11px; color:#64748b; background:#f8fafc; padding:8px; border-radius:4px; margin-top:10px; border:1px solid #e2e8f0;">
                                "{script_prev}"
                            </div>
                            <div style="margin-top:15px; text-align:right;">
                                <span style="font-size:11px; color:#7c3aed; font-weight:bold;">Tap to View Details ➜</span>
                            </div>
                         </div>
                    </div>
                    """
            else:
                 narrative_cards_html = "<div style='grid-column:1/-1; text-align:center; padding:40px; color:#94a3b8;'>생성된 내러티브 토픽이 없습니다.</div>"
        except Exception as e:
            narrative_cards_html = f"<div style='color:red;'>Narrative Load Error: {e}</div>"
    else:
        narrative_cards_html = "<div style='grid-column:1/-1; text-align:center; padding:40px; color:#94a3b8; background:#f9fafb; border-radius:8px;'>아직 Narrative Engine이 실행되지 않았습니다.</div>"

    # Inject JS Data into head or body


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

    # Script Output (Already loaded in step 1, just reusing variables)
    # Ensure topic_title is synced if script loaded update
    if script_body and topic_title == "주제 선정 대기중":
         for line in script_body.splitlines():
            if line.startswith("# "):
                topic_title = line[2:].strip()
                break
    if script_body and not topic_title: topic_title = "스크립트 생성 완료"

    # 3. Archive HTML
    archive_html = ""
    try:
        # List last 7 days of output
        archive_html += '<div class="archive-list" style="background:white; border-radius:8px; border:1px solid #e2e8f0; overflow:hidden;">'
        for i in range(1, 8):
            past_date = (datetime.utcnow() - timedelta(days=i)).strftime("%Y/%m/%d")
            p_script = base_dir / "data" / "reports" / past_date / "daily_brief.md"
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
    
    # [NEW] Topic Archive HTML
    try:
        historical_cards = _load_historical_cards(base_dir)
        topic_archive_view_html = _generate_archive_view(historical_cards)
    except Exception as e:
        topic_archive_view_html = f"<div style='padding:20px; color:red;'>Archive Load Error: {e}</div>"

    
    # [NEW] Topic Gate Explanation Card v1.0
    topic_gate_html = ""
    try:
        tg_base = base_dir / "data" / "topics" / "gate" / ymd.replace("-", "/")
        tg_path = tg_base / "topic_gate_output.json"
        
        # [Step 10-2] Trust Score Resolution Logic
        event_trust_map = {}
        try:
            ev_path = base_dir / "data" / "events" / ymd.replace("-", "/") / "events.json"
            if ev_path.exists():
                ev_data = json.loads(ev_path.read_text(encoding="utf-8"))
                for ev in ev_data.get("events", []):
                    event_trust_map[ev["event_id"]] = ev.get("trust_score", 0.5)
        except: pass

        cand_event_map = {}
        try:
            tc_path = tg_base / "topic_gate_candidates.json"
            if tc_path.exists():
                tc_data = json.loads(tc_path.read_text(encoding="utf-8"))
                for cand in tc_data.get("candidates", []):
                    # Extract event_id from ref like 'events:policy:ev_abc123'
                    ev_ids = []
                    for ref in cand.get("evidence_refs", []):
                        parts = ref.split(":")
                        if len(parts) == 3: ev_ids.append(parts[2])
                    cand_event_map[cand["candidate_id"]] = ev_ids
        except: pass

        if tg_path.exists():
            tg_data = json.loads(tg_path.read_text(encoding="utf-8"))
            title = tg_data.get("title", "No Title")
            question = tg_data.get("question", "")
            raw_conf = tg_data.get("confidence", "N/A")
            handoff = tg_data.get("handoff_to_structural", False)
            
            # [Step 10-2] Reframe Policy
            max_trust = 0.0
            for c_id in tg_data.get("source_candidates", []):
                for e_id in cand_event_map.get(c_id, []):
                    max_trust = max(max_trust, event_trust_map.get(e_id, 0.0))
            
            is_watchlist = False
            conf = raw_conf
            if raw_conf == "LOW" and len(tg_data.get("numbers", [])) >= 1 and max_trust >= 0.7:
                conf = "WATCHLIST_CANDIDATE"
                is_watchlist = True

            # Logic for 5 Mandatory Blocks
            # 1) Market Expectation
            expectation = tg_data.get("why_people_confused", "INSUFFICIENT DATA")
            
            # 2) Actual Market Move (Min 2 items) - Placeholder as per spec
            market_move_html = """
            <div style="display:flex; gap:10px; margin-top:8px;">
                <span style="background:#fef2f2; color:#b91c1c; padding:4px 8px; border-radius:4px; font-size:12px; font-weight:bold;">INSUFFICIENT DATA</span>
                <span style="background:#fef2f2; color:#b91c1c; padding:4px 8px; border-radius:4px; font-size:12px; font-weight:bold;">INSUFFICIENT DATA</span>
            </div>
            """
            
            # 3) Divergence / Why mismatch
            reasons_tags = "".join([f"<span style='background:#fef3c7; color:#92400e; padding:2px 8px; border-radius:12px; font-size:11px; font-weight:600;'>#{r[:15]}...</span>" for r in tg_data.get("key_reasons", [])])
            
            watchlist_supplement_html = ""
            if is_watchlist:
                watchlist_supplement_html = f"""
                <div style="margin-top:15px; background:#eef2ff; border:1px solid #c7d2fe; border-radius:8px; padding:12px;">
                    <div style="font-size:11px; font-weight:800; color:#4338ca; text-transform:uppercase; margin-bottom:6px;">⭐ Watchlist Supplement</div>
                    <div style="font-size:12px; color:#3730a3; margin-bottom:4px;"><strong>Missing for ELIGIBLE:</strong> Multi-source structural correlation (Current Trust: {max_trust:.1f})</div>
                    <div style="font-size:12px; color:#3730a3;"><strong>Next Action:</strong> {tg_data.get("risk_one", "Next major data check")}</div>
                </div>
                """

            divergence_html = f"""
            <div style="margin-top:10px;">
                <div style="font-size:14px; color:#1e293b; font-weight:600; line-height:1.4;">{tg_data.get("why_people_confused", "INSUFFICIENT DATA")}</div>
                <div style="display:flex; flex-wrap:wrap; gap:6px; margin-top:8px;">{reasons_tags}</div>
                {watchlist_supplement_html}
            </div>
            """

            # 4) Evidence Comparison (Expected vs Actual)
            evidence_rows = ""
            for n in tg_data.get("numbers", []):
                evidence_rows += f"""
                <tr style="border-bottom:1px solid #f1f5f9;">
                    <td style="padding:8px 0; color:#64748b;">{n.get('label')}</td>
                    <td style="padding:8px 0; text-align:center; color:#94a3b8;">N/A</td>
                    <td style="padding:8px 0; text-align:right; color:#1e3a8a; font-weight:700;">{n.get('value')} {n.get('unit')}</td>
                </tr>
                """
            if not evidence_rows:
                evidence_rows = '<tr><td colspan="3" style="padding:10px; text-align:center; color:#94a3b8;">INSUFFICIENT DATA</td></tr>'

            # 5) Forward Watchlist
            watchlist_items = [tg_data.get("risk_one", "INSUFFICIENT DATA"), "Next Major Data Release Check", "Liquidity Shift Confirmation"]
            watchlist_html = "".join([f"<div style='display:flex; align-items:start; gap:8px; margin-bottom:6px;'><span style='color:#3b82f6;'>•</span><span style='font-size:12px; color:#475569;'>{w}</span></div>" for w in watchlist_items])

            # Final Card Assembly
            conf_color = "#4f46e5" if is_watchlist else ("#10b981" if conf == "HIGH" else "#f59e0b" if conf == "MEDIUM" else "#ef4444")
            handoff_badge = '<span style="background:#dcfce7; color:#166534; padding:2px 6px; border-radius:4px; font-size:11px; font-weight:bold;">Handoff OK</span>' if handoff else '<span style="background:#f1f5f9; color:#64748b; padding:2px 6px; border-radius:4px; font-size:11px; font-weight:bold;">Gate Only</span>'

            topic_gate_html = f"""
            <div style="background:white; border:1px solid #e2e8f0; border-radius:16px; overflow:hidden; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);">
                <!-- Header -->
                <div style="background:#f8fafc; padding:20px 25px; border-bottom:1px solid #e2e8f0; display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <div style="font-size:11px; font-weight:800; color:#6366f1; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px;">EVENT-TRIGGERED ANALYSIS</div>
                        <h3 style="margin:0; font-size:22px; color:#1e293b; font-weight:800; letter-spacing:-0.02em;">{title}</h3>
                    </div>
                    <div style="display:flex; flex-direction:column; align-items:end; gap:6px;">
                        <span style="background:{conf_color}; color:white; padding:3px 8px; border-radius:4px; font-size:10px; font-weight:800;">{conf.replace("_", " ")}</span>
                        {handoff_badge}
                    </div>
                </div>

                <div style="padding:25px; display:grid; grid-template-columns: 1fr 1fr; gap:30px;">
                    <!-- Left Column: Narrative -->
                    <div style="display:flex; flex-direction:column; gap:25px;">
                        <section>
                            <h4 style="margin:0; font-size:12px; color:#64748b; text-transform:uppercase; font-weight:700; display:flex; align-items:center; gap:6px;">
                                💭 1. Market Expectation
                            </h4>
                            <div style="margin-top:8px; font-size:14px; color:#475569; line-height:1.6; border-left:3px solid #e2e8f0; padding-left:12px;">{expectation}</div>
                        </section>

                        <section>
                            <h4 style="margin:0; font-size:12px; color:#64748b; text-transform:uppercase; font-weight:700;">
                                📉 2. Actual Market Move
                            </h4>
                            {market_move_html}
                        </section>

                        <section>
                            <h4 style="margin:0; font-size:12px; color:#64748b; text-transform:uppercase; font-weight:700;">
                                ⚡ 3. Divergence / Why Mismatch
                            </h4>
                            {divergence_html}
                        </section>
                    </div>

                    <!-- Right Column: Data & Watchlist -->
                    <div style="background:#f8fafc; border-radius:12px; padding:20px; border:1px solid #f1f5f9; display:flex; flex-direction:column; gap:25px;">
                        <section>
                            <h4 style="margin:0; font-size:12px; color:#64748b; text-transform:uppercase; font-weight:700; margin-bottom:12px;">
                                📊 4. Evidence Comparison
                            </h4>
                            <table style="width:100%; font-size:13px; border-collapse:collapse;">
                                <thead style="color:#94a3b8; font-size:11px;">
                                    <tr>
                                        <th style="padding:4px 0; text-align:left;">Metric</th>
                                        <th style="padding:4px 0; text-align:center;">Expected</th>
                                        <th style="padding:4px 0; text-align:right;">Actual</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {evidence_rows}
                                </tbody>
                            </table>
                        </section>

                        <section>
                            <h4 style="margin:0; font-size:12px; color:#64748b; text-transform:uppercase; font-weight:700; margin-bottom:12px;">
                                🔭 5. Forward Watchlist
                            </h4>
                            <div style="background:white; border:1px solid #e2e8f0; border-radius:8px; padding:12px;">
                                {watchlist_html}
                            </div>
                        </section>
                    </div>
                </div>
            </div>
            """
        else:
            topic_gate_html = '<div style="padding:60px; text-align:center; color:#94a3b8; background:white; border-radius:16px; border:1px dashed #cbd5e1;">오늘의 이벤트 기반 토픽이 아직 생성되지 않았습니다.</div>'
    except Exception as e:
        topic_gate_html = f'<div style="padding:20px; color:red; background:#fee2f2; border-radius:8px;">Topic Gate UI Error: {e}</div>'

    # 5. Ledger HTML
    ledger_html = '<div style="padding:20px; text-align:center; color:#94a3b8;">No ledger data.</div>'
    
    # 6. Final Card (Ensure variable exists)
    if 'final_card' not in locals():
        final_card = {}

    # 7. Topic List Tab Logic
    topic_list_html = ""
    top_topics = final_card.get("top_topics", [])
    topic_details = {} # Global map for modals
    
    consumed_ids = set()
    synth_id = f"synth_{ymd}"

    # [Phase 42] Render Synthesized Topic Section (Top Priority)
    synth_html = ""
    ct = synth_topic.get("content_topic", {})
    if ct:
        s_title = ct.get("title", "Unknown")
        s_status = ct.get("status", "WATCH")
        s_why = ct.get("why_now", "")
        s_comps = ct.get("components", {})
        
        # Populate Consumed IDs
        structs = s_comps.get("structural", [])
        for s in structs:
             if s.get("dataset_id"):
                 consumed_ids.add(s.get("dataset_id"))
        
        s_ev_count = len(structs)
        
        # Register Synth Details for Modals
        # Construct Script (7-step outline)
        s_outline = [
            f"# [합성] {s_title}",
            "## 1. Hook (Why Now)",
            f"{s_why}",
            "## 2. Event Context",
            f"Question: {s_comps.get('event',{}).get('question','N/A')}",
            "## 3. Structural Evidence",
            f"Mapped Signals: {s_ev_count}",
            "\n".join([f"- {s.get('title','')} ({s.get('score',0)})" for s in structs])
        ]
        topic_details[synth_id] = {
            "script_text": "\n\n".join(s_outline),
            "evidence_trace": {
                "summary": f"Synthesized from {s_ev_count} structural signals + Event Gate",
                "components": s_comps
            },
            "anchors": [],
            "metadata": {"type": "synthesized"}
        }

        # [Logic Change] Check if Synth Topic is Primary Speakable
        # Criteria: READY status + Struct Count >= 3 (User Rule)
        is_synth_primary = (s_status == "READY" and s_ev_count >= 3)
        
        status_color = "#10b981" if is_synth_primary else "#f59e0b"
        card_bg = "linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%)" if is_synth_primary else "linear-gradient(135deg, #ffffff 0%, #fffbeb 100%)"
        border_col = "#bfdbfe" if is_synth_primary else "#fcd34d"
        
        header_text = "🗣️ 오늘의 핵심 발화 (Synthesized Speakable)" if is_synth_primary else "🔬 오늘의 합성 관찰 (Synthesized Watch)"
        type_badge = '<span style="background:#4f46e5; color:white; padding:2px 8px; border-radius:4px; font-size:10px; margin-left:8px;">STATE_TRANSITION</span>' if is_synth_primary else ""

        synth_html = f"""
        <!-- Synthesized Topic Card -->
        <div style="background: {card_bg}; border: 1px solid {border_col}; border-radius: 12px; padding: 25px; margin-bottom: 40px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
            <div style="font-size: 12px; font-weight: 800; color: #64748b; text-transform: uppercase; margin-bottom: 10px; display:flex; align-items:center;">
                <span>{header_text}</span>
                {type_badge}
            </div>
            
            <h2 style="font-size: 24px; font-weight: 800; color: #1e293b; margin: 0 0 15px 0;">{s_title}</h2>
            
            <div style="background: rgba(255,255,255,0.8); padding: 15px; border-radius: 8px; font-size: 14px; color: #334155; line-height: 1.6; border: 1px solid #e2e8f0;">
                <strong>Why Now:</strong> {s_why}
            </div>
            
            <div style="margin-top: 15px; display: flex; justify-content:space-between; align-items:center;">
                <div style="font-size: 13px; color: #64748b; display: flex; gap: 20px;">
                    <span>✅ Structural Evidence: <strong>{s_ev_count} signals</strong> mapped</span>
                    <span>🔥 Event Relevance: <strong>{'YES' if s_comps.get('event', {}).get('eligible') else 'NO'}</strong></span>
                </div>
                <div style="display:flex; gap:10px;">
                     <button onclick="showTopicScript('{synth_id}')" style="background:#3b82f6; color:white; border:none; padding:6px 12px; border-radius:6px; cursor:pointer; font-weight:bold; font-size:12px;">📄 스크립트 보기</button>
                     <button onclick="showDeepLogicReport('{synth_id}')" style="background:white; color:#3b82f6; border:1px solid #3b82f6; padding:6px 12px; border-radius:6px; cursor:pointer; font-weight:bold; font-size:12px;">📊 근거 보기</button>
                </div>
            </div>
        </div>
        """

    # [Narrative Layer Integration] Load Narrative Topics
    narrative_data = {}
    try:
        narrative_path = base_dir / "data" / "reports" / ymd.replace("-","/") / "narrative_topics.json"
        print(f"[DEBUG] Checking narrative path: {narrative_path}")
        if narrative_path.exists():
            print(f"[DEBUG] Narrative file found!")
            narrative_data = json.loads(narrative_path.read_text(encoding="utf-8"))
        else:
            print(f"[DEBUG] Narrative file NOT found at {narrative_path}")
    except Exception as e: 
        print(f"[DEBUG] Error loading narrative topics: {e}")
    
    narrative_topics_list = narrative_data.get("topics", [])
    print(f"[DEBUG] Found {len(narrative_topics_list)} narrative topics.")
    
    # Merge or separate? For MVP, let's append them but mark them.
    # We want to keep structural topics first if any.
    
    # Prepare scripts map
    all_scripts_map = {}
    
    # 1. Load Structural Scripts
    for i in range(len(top_topics)):
        s_body = ""
        try:
            if i == 0:
                s_path = base_dir / "data" / "reports" / ymd.replace("-","/") / "daily_brief.md"
                if not s_path.exists(): s_path = base_dir / "data" / "content" / "insight_script_v1.md"
            else:
                s_path = base_dir / "data" / "reports" / ymd.replace("-","/") / f"insight_script_{i+1}.md"
            
            if s_path.exists():
                s_body = s_path.read_text(encoding='utf-8')
        except: pass
        all_scripts_map[f"structural_{i}"] = s_body or "스크립트 생성 대기 중..."

    # 2. Add Narrative Topics to the display list
    for idx, nt in enumerate(narrative_topics_list):
        # Map narrative topic to the structure expected by the UI
        mapped_t = {
            "title": nt.get("topic_anchor"),
            "rationale": nt.get("core_narrative"),
            "level": "Narrative",
            "confidence": 70 if nt.get("confidence_level") == "MEDIUM" else (90 if nt.get("confidence_level") == "HIGH" else 50),
            "is_narrative": True,
            "topic_id": nt.get("topic_id"),
            "observed_metrics": nt.get("observed_metrics", []),
            "leader_stocks": nt.get("leader_stocks", []),
            "trigger_event": nt.get("trigger_event", "")
        }
        top_topics.append(mapped_t)
        all_scripts_map[f"narrative_{idx}"] = nt.get("script_kr", "스크립트가 없습니다.")

    # [Phase 18] Prepare Refactored Data (SPEAK, WATCH, EVIDENCE)
    speak_topics = []
    watch_topics = []
    consolidated_anchors = []

    def _get_or_gen_script(t, idx, is_structural=True):
        """Load specific script or generate minimal 7-step outline."""
        script_text = ""
        # 1. Try Loading File
        try:
            if is_structural:
                if idx == 0:
                    s_path = base_dir / "data" / "reports" / ymd.replace("-","/") / "daily_brief.md"
                    if not s_path.exists(): s_path = base_dir / "data" / "content" / "insight_script_v1.md"
                else:
                    s_path = base_dir / "data" / "reports" / ymd.replace("-","/") / f"insight_script_{idx+1}.md"
            else:
                s_path = base_dir / "data" / "reports" / ymd.replace("-","/") / f"narrative_script_{idx}.md"
            
            if s_path.exists():
                script_text = s_path.read_text(encoding='utf-8')
        except: pass

        if script_text: return script_text

        # 2. Fallback Generation
        title = t.get('title', 'Unknown')
        rationale = t.get('rationale', t.get('core_narrative', 'No rationale'))
        
        # Simple 7-step pattern
        outline = [
            f"# {title}",
            "## 1. Hook (Current Status)",
            f"시장 데이터에서 {title}와 관련하여 평소와 다른 유의미한 움직임이 감지되었습니다.",
            "## 2. Market Expectation",
            f"기존 시장의 기대치와 달리 {rationale.split('.')[0]} 수준의 변화가 확인됩니다.",
            "## 3. Actual Market Move",
            f"지표는 {t.get('level', 'L2')} 수준의 경고 영역에 진입했습니다.",
            "## 4. Why Mismatch (Divergence)",
            "공급망 및 자금 흐름 데이터상에서 실질적인 괴리가 발생하고 있습니다.",
            "## 5. Evidence (Quant & Trace)",
            f"정량 데이터: {t.get('observed_metrics', ['N/A'])} / Trace 코드: {t.get('topic_id', 'Unknown')}",
            "## 6. What to Watch Next",
            f"관련 대장주({', '.join(t.get('leader_stocks', ['N/A']))[:50]})의 변동성과 추가 지표 확인이 필수적입니다.",
            "## 7. Risk Note",
            "단기적인 변동성에 유의하며, 지표의 확산 여부를 지속적으로 관찰해야 합니다."
        ]
        return "\n\n".join(outline)
    
    # 1. Structural Topics from Final Card
    all_struct = final_card.get("top_topics", [])
    for idx, t in enumerate(all_struct):
        # [Deduplication] Hide if consumed by Synthesis
        if t.get("dataset_id") in consumed_ids:
            # [Fix] Even if hidden from Speak/Watch, its evidence must be in Evidence Tab
            # Manually add to consolidated_anchors
            c_anchor = {
                "sensor_id": t.get("dataset_id"), 
                "title": t.get("title"), 
                "_topic_title": t.get("title"),
                "_type": "structural",
                "rationale": f"Level: <b>{t.get('level', 'N/A')}</b> | Z-score: <b>{t.get('raw_data', {}).get('evidence', {}).get('details', {}).get('z_score', 'N/A')}</b>"
            }
            consolidated_anchors.append(c_anchor)
            continue
            
        # Ensure ID
        tid = t.get("topic_id") or f"struct_{idx}_{ymd}"
        t["topic_id"] = tid
        
        # Map into the internal speaker-friendly format
        t_mapped = dict(t)
        t_mapped["speak_eligibility_trace"] = {
            "triggers": [t.get("rationale", "Structural deviation detected")],
            "summary": "VALIDATED BY ANCHOR ENGINE"
        }
        # Anchors for evidence
        t_mapped["anchors"] = {"structural": [{"sensor_id": t.get("dataset_id"), "title": t.get("title")}]}
        
        # Populate Details
        topic_details[tid] = {
            "script_text": _get_or_gen_script(t, idx, True),
            "evidence_trace": t_mapped["speak_eligibility_trace"],
            "anchors": t_mapped["anchors"].get("structural", []),
            "metadata": {"dataset": t.get("dataset_id"), "level": t.get("level")}
        }

        if t.get("proof_status") == "VALIDATED" and t.get("confidence", 0) >= 80:
            speak_topics.append(t_mapped)
        else:
            watch_topics.append(t_mapped)

    # 2. Event-Triggered Topics (Topic Gate)
    if gate_data:
        # Ensure ID
        tid = gate_data.get("topic_id") or f"gate_{ymd}"
        gate_data["topic_id"] = tid
        
        gate_eligibility = gate_data.get("speak_eligibility", {})
        gate_topic = {
            "title": gate_data.get("title"),
            "topic_id": tid,
            "dataset_id": "topic_gate",
            "rationale": gate_data.get("why_people_confused"),
            "speak_eligibility_trace": gate_eligibility,
            "anchors": {"event": [{"sensor_id": "topic_gate", "title": gate_data.get("title")}]}
        }
        
        # Populate Details
        topic_details[tid] = {
            "script_text": _get_or_gen_script(gate_topic, 0, False), # idx 0 for simplicity if only one gate
            "evidence_trace": gate_eligibility,
            "anchors": gate_topic["anchors"].get("event", []),
            "metadata": {"type": "event-gate"}
        }

        if gate_eligibility.get("eligible"):
            speak_topics.append(gate_topic)
        else:
            # If not eligible but has shift, put in watch
            if gate_eligibility.get("summary") or gate_eligibility.get("trace", {}).get("NARRATIVE_SHIFT", {}).get("triggered"):
                 watch_topics.append(gate_topic)

    # 3. Evidence Collection
    for t in speak_topics + watch_topics:
        # [Deduplication] Skip if Title matches Synth Topic exactly
        if s_title and t.get("title") == s_title:
             # Ensure its evidence is captured though!
             ans = t.get("anchors", {})
             for atype, alist in ans.items():
                for a in alist:
                    a_with_topic = dict(a)
                    a_with_topic["_topic_title"] = t.get("title")
                    a_with_topic["_type"] = atype
                    # [Requirement] Data Only (No narrative)
                    _lvl = t.get('level', 'N/A')
                    _z = t.get('raw_data', {}).get('evidence', {}).get('details', {}).get('z_score', 'N/A')
                    a_with_topic["rationale"] = f"Level: <b>{_lvl}</b> | Z-score: <b>{_z}</b>"
                    consolidated_anchors.append(a_with_topic)
             continue

        ans = t.get("anchors", {})
        for atype, alist in ans.items():
            for a in alist:
                # Add topic reference to anchor
                a_with_topic = dict(a)
                a_with_topic["_topic_title"] = t.get("title")
                a_with_topic["_type"] = atype
                # [Requirement] Data Only
                _lvl = t.get('level', 'N/A')
                _z = t.get('raw_data', {}).get('evidence', {}).get('details', {}).get('z_score', 'N/A')
                a_with_topic["rationale"] = f"Level: <b>{_lvl}</b> | Z-score: <b>{_z}</b>"
                consolidated_anchors.append(a_with_topic)

    # [Deduplication] Remove Synth-matching topics from speak/watch lists
    if s_title:
        speak_topics = [t for t in speak_topics if t.get("title") != s_title]
        watch_topics = [t for t in watch_topics if t.get("title") != s_title]
    
    # [Phase 18] Generate HTML for Refactored Panels
    
    # [Grouping] Post-process Watch Topics (Deduplicate by Theme)
    grouped_watch = {}
    for t in watch_topics:
        title = t.get("title", "")
        # Extract [Theme]
        theme_match = re.search(r"^\[(.*?)\]", title)
        group_key = theme_match.group(1) if theme_match else title
        
        if group_key not in grouped_watch:
            grouped_watch[group_key] = []
        grouped_watch[group_key].append(t)
    
    final_watch_topics = []
    for key, items in grouped_watch.items():
        # Sort by score desc
        items.sort(key=lambda x: x.get("score", 0), reverse=True)
        representative = items[0]
        count = len(items)
        
        if count > 1:
            # Mark as group leader
            representative["is_group_leader"] = True
            representative["group_count"] = count
            representative["group_key"] = key
        
        final_watch_topics.append(representative)
        
    watch_topics = final_watch_topics
    
    def _render_cards(topics: List[Dict], card_type: str) -> str:
        if not topics:
            if card_type == "speak":
                return '<div style="padding:60px; text-align:center; color:#94a3b8; background:white; border-radius:12px; border:1px dashed #cbd5e1;">오늘 발화 가능한 대상이 없습니다. (No speakable topics today)</div>'
            elif card_type == "watch":
                return '<div style="padding:60px; text-align:center; color:#94a3b8; background:white; border-radius:12px; border:1px dashed #cbd5e1;">오늘 관찰 중인 대상이 없습니다.</div>'
        
        cards_html = ""
        for idx, t in enumerate(topics):
            trace = t.get("speak_eligibility_trace", {})
            reasons = trace.get("triggers", []) if card_type == "speak" else trace.get("shift_metadata", {}).get("reasons", ["Observation ongoing"])
            anchors_sum = t.get("anchors", {})
            dataset_id = t.get('dataset_id', '')
            border_color = "#3b82f6" if card_type == "speak" else "#f59e0b"

            # Formatting anchors
            ans_html = ""
            for atype, alist in anchors_sum.items():
                tags = "".join([f"<span style='background:#f1f5f9; color:#475569; padding:2px 8px; border-radius:4px; font-size:10px; margin-right:4px;'>{a['sensor_id']}</span>" for a in alist])
                ans_html += f"<div style='margin-top:5px;'><span style='font-size:11px; font-weight:bold; color:#64748b;'>{atype.upper()}:</span> {tags}</div>"

            # [Grouping] Badge
            group_badge = ""
            if t.get("is_group_leader"):
                count = t.get("group_count", 1)
                group_badge = f'<span style="background:#e0e7ff; color:#4338ca; padding:2px 8px; border-radius:12px; font-size:11px; font-weight:bold; margin-left:8px;">+{count-1} More (Collapsed)</span>'

            cards_html += f"""
            <div class="card" style="margin-bottom:20px; border-left:4px solid {border_color};">
                <div style="font-size:11px; color:#94a3b8; margin-bottom:4px; font-family:monospace;">
                    TOPIC #{idx+1} | {dataset_id} {group_badge}
                </div>
                <h3 style="margin:0 0 10px 0; font-size:18px; color:#1e293b; line-height:1.4;">
                    {t.get('title')}
                </h3>
                
                <div style="background:#f0f9ff; padding:12px; border-radius:6px; font-size:13px; margin-bottom:15px;">
                    <strong>🎯 Triggered Conditions:</strong>
                    <ul style="margin:5px 0 0 20px; padding:0;">
                        {"".join([f"<li>{r}</li>" for r in reasons])}
                    </ul>
                </div>
                
                {ans_html}
                
                <div style="display:flex; gap:10px; margin-top:20px;">
                    <button onclick="showTopicScript('{t.get('topic_id')}')" style="background:#3b82f6; color:white; border:none; padding:8px 15px; border-radius:6px; font-weight:bold; cursor:pointer; font-size:12px;">📜 스크립트 보기</button>
                    <button onclick="showDeepLogicReport('{t.get('topic_id')}')" style="background:#eff6ff; color:#3b82f6; border:1px solid #bfdbfe; padding:8px 15px; border-radius:6px; font-weight:bold; cursor:pointer; font-size:12px;">📊 근거 보기</button>
                    <button onclick="activate('rejection-ledger')" style="background:white; color:#64748b; border:1px solid #e2e8f0; padding:8px 15px; border-radius:6px; font-weight:bold; cursor:pointer; font-size:12px;">🚫 보류/거절 보기</button>
                </div>
            </div>
            """
        return cards_html

    speak_topics_html = _render_cards(speak_topics, "speak")
    watch_topics_html = _render_cards(watch_topics, "watch")




    # 3. EVIDENCE TODAY
    evidence_today_html = ""
    
    # [Requirement] Evidence screen structure: 1. STRUCTURAL, 2. EVENT
    if consolidated_anchors:
        # Group by type
        grouped = {}
        for a in consolidated_anchors:
            atype = a.get("_type", "other")
            if atype not in grouped: grouped[atype] = []
            grouped[atype].append(a)
            
        # Explicit Order Logic
        ordered_keys = []
        if "structural" in grouped: ordered_keys.append("structural")
        if "event" in grouped: ordered_keys.append("event")
        
        # Add remaining keys
        for k in sorted(grouped.keys()):
            if k not in ordered_keys:
                ordered_keys.append(k)
            
        for atype in ordered_keys:
            items = grouped[atype]
            rows = ""
            for it in items:
                rows += f"""
                <tr style="border-bottom:1px solid #f1f5f9;">
                    <td style="padding:10px; font-weight:600; color:#1e293b; width:25%; font-family:monospace;">{it.get('sensor_id')}</td>
                    <td style="padding:10px; font-size:12px; color:#64748b; width:45%;">{it.get('_topic_title')}</td>
                    <td style="padding:10px; font-size:12px; color:#3b82f6; width:30%; font-family:monospace;">{it.get('rationale','-')}</td>
                </tr>
                """
            
            evidence_today_html += f"""
            <div class="card" style="margin-bottom:25px; padding:0; overflow:hidden;">
                <div style="background:#f8fafc; padding:12px 20px; border-bottom:1px solid #e2e8f0; font-weight:800; font-size:12px; color:#475569; text-transform:uppercase;">
                    {atype.replace("_"," ")}
                </div>
                <table style="width:100%; border-collapse:collapse; font-size:13px;">
                    {rows}
                </table>
            </div>
            """
    else:
         evidence_today_html += '<div style="padding:60px; text-align:center; color:#94a3b8; background:white; border-radius:12px; border:1px dashed #cbd5e1;">수집된 근거(Anchors) 데이터가 없습니다.</div>'
    
    # 7. Topic List Tab Logic
    if top_topics:
        list_items = ""
        for idx, t in enumerate(top_topics):
            is_main = (idx == 0)
            is_narrative = t.get("is_narrative", False)
            bg = "#f0f9ff" if is_main and not is_narrative else ("#f5f3ff" if is_narrative else "white")
            border = "2px solid #3b82f6" if is_main and not is_narrative else ("1px solid #7c3aed" if is_narrative else "1px solid #e2e8f0")
            
            badge = ""
            if is_main and not is_narrative:
                badge = '<span style="background:#3b82f6; color:white; font-size:10px; padding:2px 6px; border-radius:4px; margin-left:5px;">MAIN</span>'
            if is_narrative:
                badge = '<span style="background:#7c3aed; color:white; font-size:10px; padding:2px 6px; border-radius:4px; margin-left:5px;">NARRATIVE</span>'
            
            level_display = t.get('level', 'L?')
            level_color = "#ef4444" if not is_narrative else "#7c3aed"

            script_btn = ""
            if (is_main or is_narrative) and (script_exists or is_narrative):
                btn_bg = "#eff6ff" if not is_narrative else "#f5f3ff"
                btn_color = "#3b82f6" if not is_narrative else "#7c3aed"
                btn_border = "#bfdbfe" if not is_narrative else "#ddd6fe"
                script_btn = f'<button onclick="showTopicDetail({idx})" style="width:100%; margin-top:10px; background:{btn_bg}; color:{btn_color}; border:1px solid {btn_border}; padding:6px; border-radius:4px; cursor:pointer; font-size:11px; font-weight:bold;">스크립트 & 상세 보기 ➜</button>'
            else:
                 script_btn = f'<button onclick="showTopicDetail({idx})" style="width:100%; margin-top:10px; background:white; color:#64748b; border:1px solid #e2e8f0; padding:6px; border-radius:4px; cursor:pointer; font-size:11px;">상세 보기 ➜</button>'

            list_items += f"""
            <div class="topic-card" style="background:{bg}; border:{border}; padding:15px; border-radius:8px; margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                    <span style="font-weight:bold; font-size:11px; color:#64748b;">#{idx+1} {t.get('dataset_id','')}</span>
                    <span style="font-weight:bold; font-size:11px; color:{level_color};">{level_display}</span>
                </div>
                <div style="font-size:14px; font-weight:bold; color:#1e293b; margin-bottom:5px;">{t.get('title')} {badge}</div>
                <div style="font-size:12px; color:#475569; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden;">{t.get('rationale')}</div>
                {script_btn}
            </div>
            """
            
        if list_items:
             # Wrap the items generated above in the Container
            items_html = list_items # renamed for clarity
            
            # Load scripts in order of top_topics
            scripts_content = []
            structural_count = 0
            narrative_count = 0
            for t in top_topics:
                # Refined scripts_content generation
                if t.get("is_narrative"):
                    scripts_content.append(all_scripts_map.get(f"narrative_{narrative_count}", ""))
                    narrative_count += 1
                else:
                    scripts_content.append(all_scripts_map.get(f"structural_{structural_count}", ""))
                    structural_count += 1

            topic_list_html = f"""
            <div style="display:grid; grid-template-columns: 1fr 1.5fr; gap:20px; height:600px;">
                <div style="overflow-y:auto; padding-right:10px;">
                    {items_html}
                </div>
                <div id="topic-detail-view" style="background:white; border:1px solid #e2e8f0; border-radius:8px; padding:25px; overflow-y:auto;">
                    <div style="color:#94a3b8; text-align:center; margin-top:50px;">
                        좌측 리스트에서 토픽을 선택하세요.
                    </div>
                </div>
            </div>
            """
            topic_list_html += f"""
        <script>
            const TOPIC_DATA = {json.dumps(top_topics)};
            const ALL_SCRIPTS = {json.dumps(scripts_content)};
            
            function showTopicDetail(idx) {{
                const t = TOPIC_DATA[idx];
                const view = document.getElementById('topic-detail-view');
                const scriptContent = ALL_SCRIPTS[idx];
                
                // [Feature] Extract Evidence Data
                let evidenceHtml = '';
                if (t.raw_data && t.raw_data.evidence && t.raw_data.evidence.details) {{
                    const d = t.raw_data.evidence.details;
                    const val = d.value !== undefined ? d.value : '-';
                    const z = d.z_score !== undefined ? d.z_score : '-';
                    const pct = d.percentile !== undefined ? d.percentile + '%' : '-';
                    const mean = d.rolling_mean_20d !== undefined ? parseFloat(d.rolling_mean_20d).toFixed(2) : '-';
                    
                    evidenceHtml = `
                    <h3 style="font-size:14px; color:#334155; margin-bottom:10px;">📊 {I18N_KO['DATA_EVIDENCE']}</h3>
                    <div style="background:#f0f9ff; padding:15px; border-radius:6px; border:1px solid #bae6fd; margin-bottom:20px;">
                        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; font-size:12px;">
                            <div><span style="color:#64748b;">현재값 ({I18N_KO['VALUE']}):</span> <span style="font-weight:bold; color:#0f172a;">${{val}}</span></div>
                            <div><span style="color:#64748b;">Z-Score:</span> <span style="font-weight:bold; color:#0369a1;">${{z}}</span></div>
                            <div><span style="color:#64748b;">평균 (20d Mean):</span> <span style="font-weight:bold; color:#334155;">${{mean}}</span></div>
                            <div><span style="color:#64748b;">Percentile:</span> <span style="font-weight:bold; color:#334155;">${{pct}}</span></div>
                        </div>
                        <div style="margin-top:10px; padding-top:10px; border-top:1px solid #e0f2fe; font-size:11px; color:#0c4a6e;">
                            <b>{I18N_KO['SIGNAL_LOGIC']}:</b> ${{d.reasoning || 'N/A'}}
                        </div>
                    </div>
                    `;
                }} else if (t.is_narrative && t.observed_metrics) {{
                    evidenceHtml = `
                    <h3 style="font-size:14px; color:#334155; margin-bottom:10px;">📊 {I18N_KO['DATA_EVIDENCE']}</h3>
                    <div style="background:#f5f3ff; padding:15px; border-radius:6px; border:1px solid #ddd6fe; margin-bottom:20px;">
                        <div style="font-size:12px; color:#334155;">
                            ${{t.observed_metrics.map(m => `• <span style="font-weight:bold;">${{m}}</span>`).join('<br>')}}
                        </div>
                        <div style="margin-top:10px; padding-top:10px; border-top:1px solid #ede9fe; font-size:11px; color:#6b21a8;">
                            <b>{I18N_KO['TRIGGER_EVENT']}:</b> ${{t.trigger_event || 'N/A'}}
                        </div>
                    </div>
                    `;
                }}

                const levelColor = t.is_narrative ? "#7c3aed" : "#ef4444";
                const levelLabel = t.is_narrative ? "Narrative Insight" : (t.level || 'L?') + " Anomaly";

                let html = `
                    <div style="border-bottom:1px solid #e2e8f0; padding-bottom:15px; margin-bottom:15px;">
                        <div style="font-size:12px; font-weight:bold; color:#64748b;">TOPIC #${{idx+1}}</div>
                        <h2 style="margin:5px 0; font-size:22px; color:#1e293b;">${{t.title}}</h2>
                        <div style="display:flex; gap:10px; align-items:center;">
                            <div style="font-size:11px; color:#fff; background:${{levelColor}}; display:inline-block; padding:2px 8px; border-radius:10px; font-weight:bold;">${{levelLabel}}</div>
                            <div style="font-size:11px; color:#64748b; font-weight:bold;">{I18N_KO['CONFIDENCE']}: <span style="color:#10b981;">${{t.confidence || 0}}%</span></div>
                        </div>
                    </div>
                    
                    <h3 style="font-size:14px; color:#334155; margin-bottom:10px;">🎯 {I18N_KO['RATIONALE']}</h3>
                    <div style="background:#f8fafc; padding:15px; border-radius:6px; font-size:13px; line-height:1.6; color:#334155; margin-bottom:20px;">
                        ${{t.rationale}}
                    </div>

                    ${{evidenceHtml}}

                    ${{t.leader_stocks && t.leader_stocks.length > 0 ? `
                    <h3 style="font-size:14px; color:#166534; margin-bottom:10px;">🚀 {I18N_KO['LEADER_STOCKS']}</h3>
                    <div style="display:flex; flex-wrap:wrap; gap:8px; margin-bottom:20px;">
                        ${{t.leader_stocks.map(s => `<span style="font-size:11px; background:#f0fdf4; border:1px solid #bbf7d0; padding:4px 12px; border-radius:20px; color:#166534; font-weight:700;">${{s}}</span>`).join('')}}
                    </div>
                    ` : ''}}
                    
                    <h3 style="font-size:14px; color:#334155; margin-bottom:10px;">📜 인사이트 스크립트</h3>
                    <div style="background:#eff6ff; padding:20px; border-radius:6px; font-size:13px; line-height:1.7; color:#1e293b; white-space:pre-wrap; border:1px solid #bfdbfe;">
                        ${{scriptContent}}
                    </div>
                `;
                
                view.innerHTML = html;
            }}
            
            // Auto open first if exists
            if (TOPIC_DATA.length > 0) setTimeout(() => showTopicDetail(0), 500);
        </script>
        """
    else:
        topic_list_html = "<div style='padding:20px; text-align:center; color:#94a3b8;'>선정된 토픽이 없습니다.</div>"

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

            function toggleAdvanced() {{
                const menu = document.getElementById('advanced-menu');
                const arrow = document.getElementById('adv-arrow');
                if (menu.classList.contains('open')) {{
                    menu.classList.remove('open');
                    arrow.textContent = '▼';
                }} else {{
                    menu.classList.add('open');
                    arrow.textContent = '▲';
                }}
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
                
                <div style="display:flex; gap:10px; align-items:center; margin-left:10px;">
                    <div class="stat-counter" title="Latest Run Date">📅 {status_data['run_date']}</div>
                    <div class="stat-counter" style="background:#ecfdf5; color:#059669; border:1px solid #10b981;">
                        SPEAK: <strong>{len(speak_topics)}</strong>
                    </div>
                    <div class="stat-counter" style="background:#fff7ed; color:#d97706; border:1px solid #f59e0b;">
                        WATCH: <strong>{len(watch_topics)}</strong>
                    </div>
                    <a href="#" onclick="activate('insight-script')" style="font-size:11px; color:#3b82f6; text-decoration:none; font-weight:bold; margin-left:5px;">[최신 리포트 열기]</a>
                </div>
            </div>
            
            <div style="display:flex; gap:10px; align-items:center;">
                <div class="conf-badge bg-green-100 text-green-800">{I18N_KO['NORMAL']}</div>
                <div class="conf-badge bg-blue-100 text-blue-800 border border-blue-300" title="Content Depth Preset">{I18N_KO['PRESET']}: {I18N_KO['STANDARD']}</div>
                <div class="status-badge status-{status_data['raw_status']}">{status_data['status']}</div>
            </div>
        </div>
        
        <div class="dashboard-container">
            
            <!-- LEFT: Navigation Panel -->
            <div class="nav-panel">
                <div style="font-size: 13px; font-weight: 800; color: #f8fafc; padding: 20px 25px; border-bottom: 1px solid #1e293b; margin-bottom: 10px; display: flex; align-items: center; justify-content: space-between;">
                    <span>HOIN INSIGHT v2.0</span>
                    <span title="System Status: {display_status}" style="font-size:10px; cursor:help;">{status_icon_char}</span>
                </div>
                
                <div class="nav-label">PRODUCTION FLOW</div>
                <div class="nav-item active" onclick="activate('speak-today')"><span class="nav-icon">🎬</span> 오늘 발화 가능 (SPEAK)</div>
                <div class="nav-item" onclick="activate('watch-today')"><span class="nav-icon">🔭</span> 오늘 관찰 (WATCH)</div>
                <div class="nav-item" onclick="activate('evidence-today')"><span class="nav-icon">📊</span> 오늘 근거 (EVIDENCE)</div>
                <div class="nav-item" onclick="activate('topic-gate')"><span class="nav-icon">🔥</span> 토픽 게이트</div>
                <div class="nav-item" onclick="activate('topic-archive')"><span class="nav-icon">📅</span> 아카이브</div>
                
                <div class="advanced-toggle" onclick="toggleAdvanced()">
                    <span>ADVANCED TOOLS</span>
                    <span id="adv-arrow">▼</span>
                </div>
                
                <div id="advanced-menu" class="advanced-content">
                    <div class="nav-label">ENGINE & OPS</div>
                    <div class="nav-item" onclick="activate('today-insight')"><span class="nav-icon">⭐</span> 기존 인사이트 뷰</div>
                    <div class="nav-item" onclick="activate('architecture-diagram')"><span class="nav-icon">🟦</span> {I18N_KO['ARCHITECTURE']}</div>
                    <div class="nav-item" onclick="activate('ops-scoreboard')"><span class="nav-icon">📈</span> {I18N_KO['OPS_SCOREBOARD']}</div>
                    <div class="nav-item" onclick="activate('data-status')"><span class="nav-icon">📡</span> {I18N_KO['DATA_STATUS']}</div>
                    <div class="nav-item" onclick="activate('system-evolution')"><span class="nav-icon">🚀</span> {I18N_KO['SYSTEM_EVOLUTION']}</div>
                    
                    <div class="nav-label">WORKFLOW</div>
                    <div class="nav-item" onclick="activate('narrative-queue')"><span class="nav-icon">🎬</span> {I18N_KO['NARRATIVE_QUEUE']}</div>
                    <div class="nav-item" onclick="activate('youtube-inbox')"><span class="nav-icon">📺</span> {I18N_KO['YOUTUBE_INBOX']}</div>
                    <div class="nav-item" onclick="activate('revival-engine')"><span class="nav-icon">♻️</span> {I18N_KO['REVIVAL_ENGINE']}</div>
                    
                    <div class="nav-label">LOGS & RAW</div>
                    <div class="nav-item" onclick="activate('rejection-ledger')"><span class="nav-icon">🚫</span> {I18N_KO['REJECTION_LIST']}</div>
                    <div class="nav-item" onclick="activate('topic-candidates')"><span class="nav-icon">📂</span> {I18N_KO['TOPIC_CANDIDATES']}</div>
                    <div class="nav-item" onclick="activate('final-decision')"><span class="nav-icon">⚖️</span> {I18N_KO['FINAL_DECISION_RAW']}</div>
                    <div class="nav-item" onclick="activate('insight-script')"><span class="nav-icon">📜</span> {I18N_KO['INSIGHT_SCRIPT_RAW']}</div>
                </div>
            </div>

            <!-- CENTER: Main Process Flow (Tabs) -->
            <div class="main-panel">
                <div class="sections-wrapper">
                    
                    <!-- NEW TAB: SPEAK TODAY -->
                    <div id="speak-today" class="tab-content active" style="display:block;">
                        {synth_html}

                        <h2 style="font-size:22px; font-weight:800; color:#1e293b; margin-bottom:25px; display:flex; align-items:center; gap:10px;">
                            <span style="background:#3b82f6; color:white; padding:4px 12px; border-radius:8px; font-size:14px;">SPEAKABLE</span>
                            오늘 발화 가능 토픽
                        </h2>
                        
                        {speak_topics_html}
                    </div>

                    <!-- NEW TAB: WATCH TODAY -->
                    <div id="watch-today" class="tab-content" style="display:none;">
                        <h2 style="font-size:22px; font-weight:800; color:#1e293b; margin-bottom:25px; display:flex; align-items:center; gap:10px;">
                            <span style="background:#f59e0b; color:white; padding:4px 12px; border-radius:8px; font-size:14px;">WATCHING</span>
                            오늘 관찰 토픽
                        </h2>
                        
                        {watch_topics_html}
                    </div>

                    <!-- NEW TAB: EVIDENCE TODAY -->
                    <div id="evidence-today" class="tab-content" style="display:none;">
                        <h2 style="font-size:22px; font-weight:800; color:#1e293b; margin-bottom:25px;">[참고: 오늘 발화 토픽의 근거 데이터]</h2>
                        
                        {evidence_today_html}
                    </div>

                    <!-- TAB 0: Today's Insight (LEGACY HOME) -->
                    <div id="today-insight" class="tab-content" style="display:none;">
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
                                        {leader_stocks_html}
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

                    <!-- TAB 0-1: Topic List (NEW) -->
                    <div id="topic-list" class="tab-content" style="display:none;">
                        <h2 style="font-size: 20px; font-weight: 700; color: #1e293b; margin-bottom: 25px;">📊 금일 선정 토픽 (Top 5)</h2>
                        <p style="font-size:13px; color:#64748b; margin-bottom:20px;">
                            호인 엔진이 오늘 감지한 이상징후 중 우선순위가 높은 5가지 토픽입니다.
                        </p>
                        {topic_list_html}
                    </div>

                    <!-- TAB: Narrative Queue (NEW) -->
                    <div id="narrative-queue" class="tab-content" style="display:none;">
                        <h2 style="font-size: 20px; font-weight: 700; color: #1e293b; margin-bottom: 10px;">🎬 내러티브 큐 (Narrative Queue)</h2>
                        <p style="font-size:13px; color:#64748b; margin-bottom:25px;">
                            Economic Hunter 스타일의 연출을 위한 단기 내러티브 토픽 및 스크립트 대기열입니다.
                            각 카드를 클릭하여 <strong>전체 스크립트 및 연출 가이드</strong>를 확인하세요.
                        </p>
                        
                        <!-- Topic Cards Grid -->
                        <div style="display:grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap:20px;">
                            {narrative_cards_html} 
                        </div>

                        <!-- Narrative Detail Modal -->
                        <div id="narrativeDetailModal" class="modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5); z-index:1000; justify-content:center; align-items:center;">
                            <div style="background:white; width:90%; max-width:800px; height:85%; border-radius:12px; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 10px 25px rgba(0,0,0,0.2);">
                                
                                <!-- Header -->
                                <div style="padding:20px; border-bottom:1px solid #e2e8f0; display:flex; justify-content:space-between; align-items:center; background:#f8fafc;">
                                    <div>
                                        <div style="font-size:11px; font-weight:bold; color:#64748b; margin-bottom:5px;">NARRATIVE TOPIC DETAIL</div>
                                        <h2 id="modal-title" style="margin:0; font-size:20px; color:#1e293b;">-</h2>
                                    </div>
                                    <button onclick="closeNarrativeModal()" style="background:none; border:none; font-size:24px; color:#94a3b8; cursor:pointer;">&times;</button>
                                </div>

                                <!-- Body -->
                                <div style="flex:1; overflow-y:auto; padding:25px;">
                                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:25px; margin-bottom:25px;">
                                        <!-- Info Column -->
                                        <div>
                                            <div style="margin-bottom:15px;">
                                                <div style="font-size:11px; font-weight:bold; color:#64748b; margin-bottom:5px;">CORE NARRATIVE</div>
                                                <div id="modal-core" style="font-size:13px; color:#334155; line-height:1.5; font-weight:600;">-</div>
                                            </div>
                                            <div style="margin-bottom:15px;">
                                                <div style="font-size:11px; font-weight:bold; color:#64748b; margin-bottom:5px;">OBSERVED METRICS (EVIDENCE)</div>
                                                <div id="modal-metrics" style="display:flex; flex-wrap:wrap; gap:5px;">-</div>
                                            </div>
                                            <div style="margin-bottom:15px;">
                                                <div style="font-size:11px; font-weight:bold; color:#64748b; margin-bottom:5px;">TRIGGER & DRIVER</div>
                                                <div style="background:#f1f5f9; padding:10px; border-radius:6px; font-size:12px;">
                                                    <div style="margin-bottom:5px;"><span style="color:#64748b;">Trigger:</span> <span id="modal-trigger" style="font-weight:bold;">-</span></div>
                                                    <div><span style="color:#64748b;">Driver:</span> <span id="modal-driver" style="font-weight:bold; color:#7c3aed;">-</span></div>
                                                </div>
                                            </div>
                                        </div>
                                        
                                        <!-- Script Column -->
                                        <div style="display:flex; flex-direction:column;">
                                            <div style="font-size:11px; font-weight:bold; color:#64748b; margin-bottom:5px; display:flex; justify-content:space-between;">
                                                <span>GENERATED SCRIPT (Human-readable)</span>
                                                <span style="color:#3b82f6; cursor:pointer;" onclick="copyScript()">Copy</span>
                                            </div>
                                            <textarea id="modal-script" style="flex:1; width:100%; border:1px solid #cbd5e1; border-radius:6px; padding:15px; font-size:13px; line-height:1.6; color:#334155; resize:none; font-family:sans-serif; background:#fafafa;" readonly></textarea>
                                        </div>
                                    </div>
                                </div>

                                <!-- Footer -->
                                <div style="padding:15px 25px; border-top:1px solid #e2e8f0; background:#f8fafc; display:flex; justify-content:flex-end; gap:10px;">
                                    <button onclick="approveTopic()" style="background:#16a34a; color:white; border:none; padding:10px 20px; border-radius:6px; font-weight:bold; cursor:pointer;">✅ 승인 (영상 제작)</button>
                                    <button onclick="rejectTopic()" style="background:#dc2626; color:white; border:none; padding:10px 20px; border-radius:6px; font-weight:bold; cursor:pointer;">❌ 거절 (Archive)</button>
                                </div>
                            </div>
                        </div>

                        <script>
                            function openNarrativeModal(topicId) {{
                                const t = window.NARRATIVE_DATA[topicId];
                                if(!t) return;

                                document.getElementById('modal-title').textContent = t.topic_anchor;
                                document.getElementById('modal-core').textContent = t.core_narrative;
                                document.getElementById('modal-trigger').textContent = t.trigger_event;
                                document.getElementById('modal-driver').textContent = t.narrative_driver;
                                document.getElementById('modal-script').value = t.script_kr;
                                
                                const mDiv = document.getElementById('modal-metrics');
                                mDiv.innerHTML = t.observed_metrics.map(m => `<span style="background:#e0f2fe; color:#0369a1; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:bold;">` + m + `</span>`).join('');

                                document.getElementById('narrativeDetailModal').style.display = 'flex';
                            }}

                            function closeNarrativeModal() {{
                                document.getElementById('narrativeDetailModal').style.display = 'none';
                            }}
                            
                            function copyScript() {{
                                const copyText = document.getElementById("modal-script");
                                copyText.select();
                                document.execCommand("copy");
                                alert("스크립트가 복사되었습니다.");
                            }}

                            function approveTopic() {{
                                alert("승인되었습니다! (Simulated)");
                                closeNarrativeModal();
                            }}
                            
                            function rejectTopic() {{
                                if(confirm("이 토픽을 거절하시겠습니까?")) {{
                                    alert("거절되었습니다. (Simulated)");
                                    closeNarrativeModal();
                                }}
                            }}
                        </script>
                    </div>

                    <!-- TAB 0-2: Topic Archive (History) -->
                    {topic_archive_view_html}

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

    # [Topic Gate Tab]
    html += f"""
                    <div id="topic-gate" class="tab-content" style="display:none;">
                        <h2 style="font-size: 20px; font-weight: 700; color: #1e293b; margin-bottom: 25px;">🔥 Topic Gate (이벤트 기반 토픽)</h2>
                        {topic_gate_html}
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

    html += f"""
        <div style="height: 50px;"></div>
        </div> <!-- End sections-wrapper -->
    </div> <!-- End Main Panel -->
</div>


<!-- MODAL -->
<div id="scriptModal" class="modal">
    <div class="modal-content" style="max-width:800px;">
         <div style="display:flex; justify-content:space-between; margin-bottom:20px;">
             <h2 style="margin:0;">Insight Script</h2>
             <button onclick="closeModal()" style="border:none; background:none; font-size:20px; cursor:pointer;">✕</button>
         </div>
         <p id="script-modal-content">Script content here...</p>
         <div style="text-align:right; margin-top:20px;">
             <button onclick="copyScript()" style="padding:8px 16px; background:#eff6ff; color:#3b82f6; border:1px solid #bfdbfe; border-radius:6px; cursor:pointer; font-weight:bold;">Copy Text</button>
         </div>
    </div>
</div>

<script>
    // [Global Dashboard Data]
    window.HOIN_DASHBOARD = {{
        run_date: "{ymd}",
        topic_details: {json.dumps(topic_details, ensure_ascii=False)}
    }};

    function closeModal() {{
        document.getElementById('scriptModal').classList.remove('modal-active');
        document.getElementById('scriptModal').style.display = "none";
    }}
    
    function copyScript() {{
        const el = document.getElementById('script-modal-content');
        if (!el) return;
        navigator.clipboard.writeText(el.innerText).then(() => alert('Copied topic script!'));
    }}
    
    function showTopicScript(tid) {{
        const modal = document.getElementById("scriptModal");
        const content = document.getElementById("script-modal-content");
        if (modal && content) {{
            const details = window.HOIN_DASHBOARD.topic_details[tid];
            if (details && details.script_text) {{
                content.innerHTML = '<div style="background:#f8fafc; padding:20px; border-radius:8px; border:1px solid #e2e8f0; white-space:pre-wrap; font-family:monospace; font-size:13px;">' + details.script_text + '</div>';
            }} else {{
                content.innerHTML = "<div style='padding:20px; text-align:center; color:#94a3b8;'>스크립트 데이터 없음: topic_details 매핑 누락 (" + tid + ")</div>";
            }}
            modal.style.display = "block";
            modal.classList.add('modal-active');
        }}
    }}

    // [Deep Logic Report Viewer]
    function showDeepLogicReport(tid) {{
        var modal = document.getElementById("reportModal");
        var content = document.getElementById("reportContent");
        
        if (modal && content) {{
            const details = window.HOIN_DASHBOARD.topic_details[tid];
            if (details && details.evidence_trace) {{
                // Fallback for missing reportContent in some layouts
                content.innerHTML = '<div style="background:#1e293b; color:#38bdf8; padding:20px; border-radius:8px; font-family:monospace; font-size:12px; overflow:auto;"><pre>' + 
                                    JSON.stringify(details.evidence_trace, null, 2) + 
                                    '</pre></div>';
            }} else if (window.REPORT_DATA && window.REPORT_DATA[tid]) {{
                // Legacy backward compatibility
                content.innerHTML = window.REPORT_DATA[tid];
            }} else {{
                content.innerHTML = "<div style='padding:20px; text-align:center; color:#94a3b8;'>근거 데이터 없음: topic_details 매핑 누락 (" + tid + ")</div>";
            }}
            modal.style.display = "block";
        }}
    }}
    
    function closeReportModal() {{
        var modal = document.getElementById("reportModal");
        if (modal) modal.style.display = "none";
    }}

    function generatePopupYaml(evoId, vid) {{
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
    }}
    
    // Close modals when clicking outside
    window.onclick = function(event) {{
        var reportModal = document.getElementById("reportModal");
        var scriptModal = document.getElementById("scriptModal");
        
        if (event.target == reportModal) {{
            reportModal.style.display = "none";
        }}
        if (event.target == scriptModal) {{
            scriptModal.classList.remove('modal-active');
        }}
    }}
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
