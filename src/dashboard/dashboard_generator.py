from __future__ import annotations

import json
import os
import logging
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

import sys
# [Fix] Ensure project root is in sys.path for direct execution imports
if __name__ == "__main__":
    # src/dashboard/dashboard_generator.py -> root is ../../
    root_path = Path(__file__).resolve().parent.parent.parent
    if str(root_path) not in sys.path:
        sys.path.insert(0, str(root_path))

from src.utils.markdown_parser import parse_markdown
from src.utils.i18n_ko import I18N_KO
from src.dashboard.issue_signal_formatter import IssueSignalFormatter

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
    """Generate HTML Table for Topic Archive (Operator-First Structure)"""
    topic_details_map = {}
    if not cards:
        return '<div style="padding:40px; text-align:center; color:#94a3b8;">저장된 과거 데이터가 없습니다.</div>'

    table_rows = ""
    
    for card_idx, c in enumerate(cards):
        date = c.get('_date', 'Unknown')
        top_topics = c.get("top_topics", [])
        
        # Fallback for old single-topic cards
        if not top_topics:
            single_topic = c.get('topic')
            if single_topic:
                top_topics = [c] # The card itself is the topic
            else:
                n_topics = c.get('narrative_topics', [])
                if n_topics:
                    top_topics = [{"title": n_topics[0].get('topic_anchor'), "level": "Narrative"}]

        for t_idx, topic in enumerate(top_topics):
            title = topic.get("title", topic.get("topic", "Untitled Topic"))
            level = str(topic.get("level", "L2"))
            
            # Type Logic (Operator First: 경사 스타일 / 이상징후)
            is_anomaly = topic.get("dataset_id") == "topic_gate" or level.lower() == "narrative"
            type_label = "이상징후" if is_anomaly else "경사 스타일"
            type_bg = "#f3e8ff" if is_anomaly else "#dbeafe"
            type_color = "#6b21a8" if is_anomaly else "#1e40af"
            
            # Importance Logic
            importance = "보통"
            if "l3" in level.lower(): importance = "높음"
            elif "l1" in level.lower(): importance = "낮음"
            
            table_rows += f"""
            <tr style="border-bottom:1px solid #f1f5f9;">
                <td style="padding:15px; color:#64748b; font-size:12px;">{date}</td>
                <td style="padding:15px; font-weight:700; color:#1e293b;">{title}</td>
                <td style="padding:15px;">
                    <span style="background:{type_bg}; color:{type_color}; padding:4px 8px; border-radius:4px; font-size:11px; font-weight:bold;">{type_label}</span>
                </td>
                <td style="padding:15px;">
                    <span style="color:#475569; font-size:12px; font-weight:600;">{importance}</span>
                </td>
            </tr>
            """

    html = f"""
    <div style="background:white; border-radius:12px; border:1px solid #e2e8f0; overflow:hidden; box-shadow:0 4px 6px -1px rgba(0,0,0,0.05);">
        <table style="width:100%; border-collapse:collapse; font-size:14px;">
            <thead style="background:#f8fafc; border-bottom:1px solid #e2e8f0;">
                <tr>
                    <th style="padding:15px; text-align:left; color:#64748b; font-weight:800; width:120px;">날짜</th>
                    <th style="padding:15px; text-align:left; color:#64748b; font-weight:800;">주제</th>
                    <th style="padding:15px; text-align:left; color:#64748b; font-weight:800; width:100px;">유형</th>
                    <th style="padding:15px; text-align:left; color:#64748b; font-weight:800; width:80px;">중요도</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
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

def _get_op_input_status(base_dir: Path, ymd: str) -> str:
    """Read operator fact input status and render compact HTML."""
    input_path = base_dir / "data" / "ops" / "fact_first_input_today.json"
    seed_path = base_dir / "data" / "facts" / "fact_first" / f"{ymd}.json"
    
    # Try seed_path first for Step 60
    target_path = seed_path if seed_path.exists() else input_path
    if not target_path.exists():
        return ""
    
    try:
        data = json.loads(target_path.read_text(encoding="utf-8"))
        # Support both schemas
        seeds = data.get("seeds", [])
        facts = data.get("facts", [])
        items = seeds + facts
        count = len(items) if items else data.get("count", 0)
        counts = data.get("counts_by_type", {})
        errors = data.get("errors", [])
        
        # Color logic
        bg_color = "#f0fdf4" if not errors else "#fef2f2"
        border_color = "#bbf7d0" if not errors else "#fecaca"
        icon = "🏹" if not errors else "⚠️"
        
        error_html = ""
        if errors:
            e_msg = errors[0].get('message', 'Unknown Error')
            error_html = f"<div style='font-size:11px; color:#dc2626; margin-top:2px;'>❌ Error: {e_msg}</div>"
            
        html = f"""
        <div style="background:{bg_color}; border:1px solid {border_color}; border-radius:8px; padding:8px 15px; margin-left:15px; font-size:12px; display:flex; flex-direction:column; justify-content:center;">
            <div style="display:flex; gap:8px; align-items:center;">
                <span style="font-weight:bold; color:#166534;">{icon} FACT SEED</span>
                <span style="font-weight:bold; color:#1e293b;">{count} 건</span>
                <span style="color:#64748b; font-size:11px;">(F:{counts.get('FLOW',0)} P:{counts.get('POLICY',0)} S:{counts.get('STRUCTURE',0)})</span>
            </div>
            {error_html}
        </div>
        """
        return html
    except Exception:
        return ""

def _generate_today_topic_view(final_card: Dict, signals: List[Dict[str, Any]], video_candidates: set = None, top1_data: Dict = None) -> str:
    """Step 66: Simplified card view for Today's Topics (Updated for Top-1 Purple)"""
    if video_candidates is None: video_candidates = set()
    
    cards_html = ""
    
    # 0. Structural Top-1 Section (Purple) - THE ONLY THING ABOVE FOLD
    if top1_data:
        t1 = top1_data
        orig = t1.get('original_card', {})
        
        # Strict Validation for Top-1
        if orig.get("structure_type") in ["STRUCTURAL_DAMAGE", "STRUCTURAL_REDEFINITION"]:
            uid = orig.get('topic_id', 'unknown_top1')
            title = t1.get('title', 'Untitled')
            
            # Format Title Korean (Step 69)
            f = IssueSignalFormatter.format_card(orig)
            title = f.get('title_display', title)
            
            summary = t1.get('one_line_summary', '')
            
            card_html = f"""
            <div class="topic-card top1" onclick="openSignalDetail('{uid}')" style="border:2px solid #a855f7; background:#faf5ff; margin-bottom:20px;">
                <div class="card-badges">
                    <div class="card-badge" style="background:#a855f7; color:white;">🟣 오늘의 구조적 핵심 이슈 (HOIN Signal)</div>
                </div>
                <div class="card-title" style="color:#6b21a8; font-size:1.2em;">{title}</div>
                <div class="card-meta">
                    <span class="meta-item importance">Global Priority</span>
                    <span class="meta-divider">|</span>
                    <span class="meta-item" style="color:#7e22ce;">{summary}</span>
                </div>
                <div style="margin-top:8px; font-size:12px; color:#9333ea; font-weight:bold;">
                     ⚡ Why Now: {t1.get('why_now', '')}
                </div>
            </div>
            """
            cards_html += card_html
    
    # 1. Process HOIN IssueSignal Topics (Green)
    for s in signals:
        # Step 68: Format Card for Display
        f = IssueSignalFormatter.format_card(s)
        
        title = f.get('title_display')
        importance = s.get('importance_level', '보통')
        card_type = s.get('structure_card_type', '이슈시그널')
        summary = s.get('one_line_summary', '')
        badge = f.get('badge_display', '')
        
        # Generate ID
        uid = s.get('topic_id', 'unknown_signal')
        
        # Video Badge Logic
        video_badge = ""
        if uid in video_candidates:
            video_badge = '<span class="card-badge video" style="background:#fecaca; color:#dc2626; margin-left:4px;">🎥 영상후보</span>'

        card_html = f"""
        <div class="topic-card" onclick="openSignalDetail('{uid}')">
            <div class="card-badges">
                <div class="card-badge signal">{card_type}</div>
                {video_badge}
            </div>
            <div class="card-title">
                {title} {badge}
            </div>
            <div class="card-meta">
                <span class="meta-item importance">{importance}</span>
                <span class="meta-divider">|</span>
                <span class="meta-item">{summary}</span>
            </div>
        </div>
        """
        cards_html += card_html

    # 2. Process HOIN Engine Topics (Blue)
    if final_card:
        topics = final_card.get('top_topics', [])
        # Fallback for old structure
        if not topics and final_card.get('topic'):
            topics = [final_card]
            
        for idx, t in enumerate(topics):
            title = t.get('title', t.get('topic', 'Untitled Engine Topic'))
            level = str(t.get('level', 'L2')).upper()
            
            # Map importance
            imp_kr = "보통"
            if "L3" in level: imp_kr = "높음"
            elif "L1" in level: imp_kr = "낮음"
            
            summary = t.get('rationale', 'No rationale provided.')[:50] + "..."
            
            # Generate ID for detail view mapping
            uid = f"engine_topic_{idx}"
            
            card_html = f"""
            <div class="topic-card" onclick="openEngineDetail('{uid}')">
                <div class="card-badge engine">호인엔진</div>
                <div class="card-title">{title}</div>
                <div class="card-meta">
                    <span class="meta-item importance">{imp_kr}</span>
                    <span class="meta-divider">|</span>
                    <span class="meta-item">{summary}</span>
                </div>
            </div>
            """
            cards_html += card_html

    if not cards_html:
        cards_html = '<div class="empty-state">오늘 선정된 중요 토픽이 없습니다.</div>'

    total_count = len(signals) + (len(final_card.get('top_topics', [])) if final_card else 0)
    
    return f"""
    <div class="today-container">
        <div class="today-header">
            <div class="today-date">{_utc_to_kst_display(_utc_ymd() + 'T00:00:00Z').split(' ')[0]}</div>
            <div class="today-summary">오늘의 핵심 토픽 <strong>{total_count}개</strong></div>
        </div>
        <div class="card-grid">
            {cards_html}
        </div>
    </div>
    """

def _generate_simple_archive_view(cards: List[Dict]) -> str:
    """Step 62: Generate simplified list for Topic Archive"""
    if not cards:
        return '<div class="empty-state">저장된 데이터가 없습니다.</div>'

    rows = ""
    for c_idx, c in enumerate(cards):
        date = c.get('_date', 'Unknown')
        topics = c.get('top_topics', [])
        if not topics and c.get('topic'): topics = [c]
        
        for t_idx, t in enumerate(topics):
            title = t.get('title', t.get('topic', 'Untitled'))
            level = str(t.get('level', 'L2'))
            imp_kr = "보통"
            if "L3" in level: imp_kr = "높음"
            elif "L1" in level: imp_kr = "낮음"
            
            # Unique ID for detail map
            uid = f"archive_{c_idx}_{t_idx}"
            
            rows += f"""
            <tr onclick="openArchiveDetail('{uid}')">
                <td class="col-date">{date}</td>
                <td class="col-title">{title}</td>
                <td class="col-type"><span class="badge engine">호인엔진</span></td>
                <td class="col-imp">{imp_kr}</td>
            </tr>
            """
            
    return f"""
    <div class="archive-container">
        <table class="archive-table">
            <thead>
                <tr>
                    <th width="100">날짜</th>
                    <th>주제</th>
                    <th width="80">방식</th>
                    <th width="60">중요도</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </div>
    """

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
    """Step 62: Simplified HOIN Dashboard Generation"""
    ymd = _utc_ymd()
    
    # 1. Load Data (Minimal Loading for UI)
    
    # [A] HOIN Engine Topics (Final Decision)
    final_card = {}
    try:
        card_base = base_dir / "data" / "decision" / ymd.replace("-","/")
        card_path = card_base / "final_decision_card.json"
        if card_path.exists():
            final_card = json.loads(card_path.read_text(encoding="utf-8"))
    except: pass
    
    # [B] HOIN IssueSignal Topics (Step 64)
    signals = []
    try:
        # Load the Processed IssueSignal Cards (Step 64) ONLY
        signal_path = base_dir / "data" / "ops" / "issuesignal_today.json"
        
        if signal_path.exists():
            signal_data = json.loads(signal_path.read_text(encoding="utf-8"))
            raw_cards = signal_data.get("cards", [])
            
            # Strict Filtering (Step 69)
            for c in raw_cards:
                # 1. Structure Check
                if c.get("structure_type") not in ["STRUCTURAL_DAMAGE", "STRUCTURAL_REDEFINITION"]:
                    continue
                
                # 2. Source Check (No tests)
                s_ids = c.get("evidence_refs", {}).get("source_ids", [])
                if not s_ids or any(x in ["test", "mock", "sample"] for x in s_ids):
                    continue
                    
                signals.append(c)
    except: pass
    
    # [C] Check Video Candidates (Step 65)
    video_candidates = set()
    video_reasons = {}
    try:
        vid_path = base_dir / "data" / "ops" / "video_candidates_today.json"
        if vid_path.exists():
            v_data = json.loads(vid_path.read_text(encoding="utf-8"))
            for vc in v_data.get("candidates", []):
                tid = vc.get("topic_id")
                video_candidates.add(tid)
                video_reasons[tid] = vc.get("why_video_natural", "")
    except: pass
    
    # [D] Structural Top-1 (Step 66) & Narrative (Step 67)
    top1_data = None
    narrative_data = None
    try:
        top1_path = base_dir / "data" / "ops" / "structural_top1_today.json"
        if top1_path.exists():
             t1 = json.loads(top1_path.read_text(encoding="utf-8"))
             if t1.get("top1_topics"):
                 top1_data = t1["top1_topics"][0]
                 
        # Load Narrative (Step 67)
        narrative_path = base_dir / "data" / "ops" / "issue_signal_narrative_today.json"
        if narrative_path.exists():
            nd = json.loads(narrative_path.read_text(encoding="utf-8"))
            narrative_data = nd.get("narrative")
    except: pass

    # [E] Historical Archive
    historical_cards = _load_historical_cards(base_dir)

    today_view_html = _generate_today_topic_view(final_card, signals, video_candidates, top1_data)
    
    # [Strict Filter Check]
    # If no signals and no top1, show specific empty state
    if not signals and not top1_data:
        today_view_html = """
        <div class="empty-state" style="padding:40px; text-align:center; color:#64748b;">
            <div style="font-size:48px; margin-bottom:10px;">📭</div>
            <h3>오늘 생성된 이슈시그널 토픽이 없습니다.</h3>
            <p>HOIN Engine이 유의미한 구조적 변화를 감지하지 못했습니다.</p>
        </div>
        """
    archive_view_html = _generate_simple_archive_view(historical_cards)

    # 3. Build Details Map (JSON for JS)
    # We need to pre-generate HTML content for the modal for each topic
    details_map = {}
    
    # (1) Signals
    # (1) Signals
    for s in signals:
        sid = s.get('topic_id')
        
        evidence = s.get('evidence_refs', {})
        drivers = ", ".join(evidence.get('structural_drivers', []))
        risk = evidence.get('risk_factor', '-')
        
        # Video Reason Injection
        video_section = ""
        if sid in video_reasons:
            video_section = f"""
            <div class="detail-section" style="background:#fff1f2; border:1px solid #fecaca;">
                <h3 style="color:#e11d48;">🎥 영상 제작 선정 이유</h3>
                <p>
                    {video_reasons[sid]}
                </p>
            </div>
            """
            
        # Top-1 Badge in Modal
        top1_badge = ""
        is_top1 = False
        if top1_data and top1_data.get('original_card', {}).get('topic_id') == sid:
            is_top1 = True
            top1_badge = '<span class="detail-badge" style="background:#a855f7; color:white; margin-right:5px;">🟣 Global TOP-1</span>'

        if is_top1 and narrative_data:
            # Override content with Narrative
            n = narrative_data
            sections = n.get('sections', {})
            
            # Step 71: Economic Hunter 4-Step Structure
            details_map[sid] = f"""
            <div class="detail-header">
                {top1_badge}
                <span class="detail-badge signal">{n.get('narrative_type', 'ECONOMIC_HUNTER')}</span>
                <h2>{n.get('title', '제목 없음')}</h2>
            </div>
            {video_section}
            
            <!-- Step 1: The Hook -->
            <div class="detail-section" style="border-left: 4px solid #a855f7; background-color: #faf5ff;">
                <h3 style="color: #6b21a8;">1. The Hook (시선 강탈)</h3>
                <p class="script-text" style="font-weight:bold; font-size: 1.1em;">
                    {sections.get('hook', n.get('opening_hook', ''))}
                </p>
            </div>

            <!-- Step 2: Core Tension -->
            <div class="detail-section">
                <h3>2. Core Tension (구조적 역학)</h3>
                <p class="script-text">
                    {sections.get('tension', n.get('core_story', '')).replace(chr(10), '<br>')}
                </p>
            </div>

            <!-- Step 3: The Hunt -->
            <div class="detail-section">
                <h3>3. The Hunt (결정적 증거)</h3>
                <p class="script-text" style="white-space: pre-wrap; background: #f8fafc; padding: 10px; border-radius: 6px;">
                    {sections.get('hunt', '')}
                </p>
            </div>

            <!-- Step 4: Action -->
            <div class="detail-section" style="border: 2px solid #22c55e; background-color: #f0fdf4;">
                <h3 style="color: #15803d;">4. Action (행동 지침)</h3>
                <p class="script-text" style="font-weight:bold; color: #166534;">
                    {sections.get('action', n.get('why_now', ''))}
                </p>
            </div>
            """
        else:
            # Standard IssueSignal Detail (Updated Step 68)
            f = IssueSignalFormatter.format_card(s)
            script_html = f.get('script_sections', '')
            title_display = f.get('title_display')
            
            details_map[sid] = f"""
            <div class="detail-header">
                {top1_badge}
                <span class="detail-badge signal">{s.get('structure_card_type', '이슈시그널')}</span>
                <h2>{title_display}</h2>
            </div>
            {video_section}
            {script_html}
            """

    # (2) Engine Topics
    if final_card:
        topics = final_card.get('top_topics', [])
        if not topics and final_card.get('topic'): topics = [final_card]
        
        for idx, t in enumerate(topics):
            uid = f"engine_topic_{idx}"
            
            # Evidence Build
            evidence_html = ""
            # Try to find evidence list
            ev_list = t.get('evidence', []) # Fallback
            # Or use key_data_html equivalent string
            
            title = t.get('title', t.get('topic', 'Untitled'))
            level = str(t.get('level', 'L2')).upper()
            imp_kr = "보통"
            if "L3" in level: imp_kr = "높음"
            elif "L1" in level: imp_kr = "낮음"
            
            script = t.get('script_draft') or t.get('script_body') or t.get('rationale') or "스크립트 생성 대기중"

            details_map[uid] = f"""
            <div class="detail-header">
                <span class="detail-badge engine">호인엔진</span>
                <h2>{title}</h2>
            </div>
            <div class="detail-section">
                <h3>📜 자연어 상세 스크립트</h3>
                <p class="script-text">{script}</p>
            </div>
            <div class="detail-section">
                <h3>🎯 선정 이유 (Context)</h3>
                <p>{t.get('rationale', '설명 없음')}</p>
            </div>
            <div class="detail-section">
                <h3>🚀 중요도 설명</h3>
                <p>
                    이 토픽은 <strong>{imp_kr} ({level})</strong> 중요도로 판정되었습니다.
                    <br>
                    {t.get('importance_desc', '')}
                </p>
            </div>
            <div class="detail-section">
                <h3>📊 데이터 기반 근거</h3>
                <div class="raw-data-box">
                    {t.get('evidence_data', 'RAW 데이터 없음')}
                </div>
            </div>
            """

    # (3) Historical Archive Details
    for c_idx, c in enumerate(historical_cards):
        topics = c.get('top_topics', [])
        if not topics and c.get('topic'): topics = [c]
        
        for t_idx, t in enumerate(topics):
            uid = f"archive_{c_idx}_{t_idx}"
            
            title = t.get('title', t.get('topic', 'Untitled'))
            level = str(t.get('level', 'L2')).upper()
            imp_kr = "보통"
            if "L3" in level: imp_kr = "높음"
            elif "L1" in level: imp_kr = "낮음"
            
            script = t.get('script_draft') or t.get('script_body') or t.get('rationale') or "스크립트 정보 없음"
            
            details_map[uid] = f"""
            <div class="detail-header">
                <span class="detail-badge engine">호인엔진 (아카이브)</span>
                <h2>{title}</h2>
            </div>
            <div class="detail-section">
                <h3>📜 과거 스크립트</h3>
                <p class="script-text">{script}</p>
            </div>
            <div class="detail-section">
                <h3>🎯 선정 이유</h3>
                <p>{t.get('rationale', '설명 없음')}</p>
            </div>
            <div class="detail-section">
                <h3>🚀 중요도</h3>
                <p>{imp_kr} ({level})</p>
            </div>
            """

    # 4. Construct Final HTML
    html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>HOIN Insight - Operator View</title>
        <style>
            :root {{
                --bg-color: #f8fafc;
                --text-primary: #0f172a;
                --text-secondary: #64748b;
                --accent-blue: #2563eb; 
                --accent-green: #059669;
                --card-bg: #ffffff;
                --border-color: #e2e8f0;
            }}
            * {{ box-sizing: border-box; }}
            body {{
                margin: 0;
                padding: 0;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                background-color: var(--bg-color);
                color: var(--text-primary);
                display: flex;
                height: 100vh;
                overflow: hidden;
            }}
            /* Sidebar */
            .sidebar {{
                width: 240px;
                background: white;
                border-right: 1px solid var(--border-color);
                display: flex;
                flex-direction: column;
                padding: 20px;
            }}
            .logo {{
                font-size: 18px;
                font-weight: 800;
                color: var(--text-primary);
                margin-bottom: 40px;
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            .menu-item {{
                padding: 12px 16px;
                margin-bottom: 8px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 600;
                color: var(--text-secondary);
                transition: all 0.2s;
            }}
            .menu-item:hover {{ background: #f1f5f9; color: var(--text-primary); }}
            .menu-item.active {{
                background: #eff6ff;
                color: var(--accent-blue);
            }}
            
            /* Main Content */
            .main-content {{
                flex: 1;
                padding: 40px;
                overflow-y: auto;
            }}
            
            /* Today View */
            .today-header {{
                margin-bottom: 30px;
            }}
            .today-date {{
                font-size: 13px;
                color: var(--text-secondary);
                margin-bottom: 5px;
                font-weight: 600;
            }}
            .today-summary {{
                font-size: 24px;
                font-weight: 800;
                color: var(--text-primary);
            }}
            
            .card-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 20px;
            }}
            
            .topic-card {{
                background: var(--card-bg);
                border: 1px solid var(--border-color);
                border-radius: 12px;
                padding: 20px;
                cursor: pointer;
                transition: transform 0.2s, box-shadow 0.2s;
                position: relative;
                overflow: hidden;
            }}
            .topic-card:hover {{
                transform: translateY(-2px);
                box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05);
                border-color: #cbd5e1;
            }}
            
            .card-badge {{
                display: inline-block;
                font-size: 11px;
                font-weight: 700;
                padding: 4px 8px;
                border-radius: 4px;
                margin-bottom: 12px;
            }}
            .card-badge.engine {{ background: #eff6ff; color: #1e40af; }}
            .card-badge.signal {{ background: #ecfdf5; color: #065f46; }}
            
            .card-title {{
                font-size: 16px;
                font-weight: 700;
                margin-bottom: 15px;
                line-height: 1.4;
                color: #1e293b;
            }}
            
            .card-meta {{
                display: flex;
                align-items: center;
                font-size: 12px;
                color: #64748b;
            }}
            .meta-item.importance {{ font-weight: 600; color: #334155; }}
            .meta-divider {{ margin: 0 8px; color: #cbd5e1; }}
            
            /* Archive View */
            .archive-table {{
                width: 100%;
                border-collapse: collapse;
                background: white;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            }}
            .archive-table th {{
                background: #f8fafc;
                text-align: left;
                padding: 12px 16px;
                font-size: 12px;
                color: #64748b;
                border-bottom: 1px solid #e2e8f0;
            }}
            .archive-table td {{
                padding: 16px;
                border-bottom: 1px solid #f1f5f9;
                font-size: 14px;
                cursor: pointer;
            }}
            .archive-table tr:hover td {{ background: #f8fafc; }}
            
            /* Modal */
            .modal {{
                display: none;
                position: fixed;
                top: 0; left: 0;
                width: 100%; height: 100%;
                background: rgba(0,0,0,0.5);
                z-index: 1000;
                justify-content: center;
                align-items: center;
            }}
            .modal.active {{ display: flex; }}
            .modal-content {{
                background: white;
                width: 90%;
                max-width: 600px;
                max-height: 85vh;
                border-radius: 16px;
                overflow-y: auto;
                padding: 30px;
                box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1);
            }}
            .detail-header {{ margin-bottom: 25px; border-bottom: 1px solid #e2e8f0; padding-bottom: 15px; }}
            .detail-badge {{ 
                font-size: 11px; font-weight: 700; padding: 4px 8px; border-radius: 4px; margin-bottom: 8px; display: inline-block; 
            }}
            .detail-badge.engine {{ background: #eff6ff; color: #1e40af; }}
            .detail-badge.signal {{ background: #ecfdf5; color: #065f46; }}
            
            .detail-header h2 {{ margin: 10px 0 0 0; font-size: 20px; font-weight: 800; color: #1e293b; }}
            
            .detail-section {{ margin-bottom: 25px; }}
            .detail-section h3 {{ font-size: 13px; color: #64748b; margin-bottom: 8px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }}
            .detail-section p {{ font-size: 15px; line-height: 1.6; color: #334155; margin: 0; }}
            .script-text {{ white-space: pre-wrap; }}
            
            .raw-data-box {{
                background: #f1f5f9;
                padding: 10px;
                border-radius: 6px;
                font-family: monospace;
                font-size: 12px;
                color: #475569;
                overflow-x: auto;
            }}
            .data-list {{ padding-left: 20px; font-size: 14px; color: #334155; }}
            .data-list li {{ margin-bottom: 5px; }}
            
            .empty-state {{ text-align: center; padding: 40px; color: #94a3b8; font-size: 14px; }}
            
            /* Utility */
            .hidden {{ display: none; }}
        </style>
    </head>
    <body>
        <div class="sidebar">
            <div class="logo">🔴 HOIN Insight</div>
            <div class="menu-item active" onclick="switchTab('today', this)">오늘 선정 토픽</div>
            <div class="menu-item" onclick="switchTab('archive', this)">전체 토픽 목록</div>
        </div>
        
        <div class="main-content">
            <div id="tab-today">
                {today_view_html}
            </div>
            <div id="tab-archive" class="hidden">
                <div class="today-header">
                    <div class="today-summary">전체 토픽 목록</div>
                </div>
                {archive_view_html}
            </div>
        </div>

        <!-- Detail Modal -->
        <div id="detail-modal" class="modal" onclick="closeModal(event)">
            <div class="modal-content">
                <div id="modal-body-content"></div>
                <div style="margin-top:30px; text-align:right;">
                    <button onclick="document.getElementById('detail-modal').classList.remove('active')" 
                            style="padding:10px 20px; border:1px solid #e2e8f0; background:white; border-radius:8px; cursor:pointer; font-weight:600; color:#475569;">
                        닫기
                    </button>
                </div>
            </div>
        </div>

        <script>
            // Data Map
            const DETAILS_MAP = {json.dumps(details_map)};
            
            function switchTab(tabName, el) {{
                // Update Menu
                document.querySelectorAll('.menu-item').forEach(i => i.classList.remove('active'));
                el.classList.add('active');
                
                // Update Content
                document.getElementById('tab-today').classList.add('hidden');
                document.getElementById('tab-archive').classList.add('hidden');
                
                document.getElementById('tab-' + tabName).classList.remove('hidden');
            }}
            
            function openSignalDetail(id) {{
                showModal(DETAILS_MAP[id]);
            }}
            
            function openEngineDetail(id) {{
                showModal(DETAILS_MAP[id]);
            }}
            
            function openArchiveDetail(id) {{
                showModal(DETAILS_MAP[id]);
            }}
            
            function showModal(html) {{
                if(!html) return;
                document.getElementById('modal-body-content').innerHTML = html;
                document.getElementById('detail-modal').classList.add('active');
            }}
            
            function closeModal(e) {{
                if(e.target.id === 'detail-modal') {{
                    e.target.classList.remove('active');
                }}
            }}
        </script>
    </body>
    </html>
    """
    
    (base_dir / "dashboard" / "index.html").write_text(html, encoding="utf-8")
    print(f"[Dashboard] Generated dashboard/index.html with simplified UI (Step 62)")
    return html


if __name__ == "__main__":
    # Adjust path if running directly from src/dashboard/
    # Assumes git root is parent of src
    # File is at src/dashboard/dashboard_generator.py
    # Git root is ../../
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent
    generate_dashboard(project_root)
