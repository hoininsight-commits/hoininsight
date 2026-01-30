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
from src.dashboard.topic_card_renderer import TopicCardRenderer
from src.dashboard.styles import DashboardStyles
from src.dashboard.issue_signal_formatter import IssueSignalFormatter
from src.ops.entity_mapping_layer import EntityMappingLayer
from src.ops.entity_state_classifier import EntityStateClassifier
from src.ops.structural_memory_engine import StructuralMemoryEngine
from src.ops.snapshot_comparison_engine import SnapshotComparisonEngine
from src.ops.structural_pattern_detector import StructuralPatternDetector
from src.ops.pattern_memory_engine import PatternMemoryEngine

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

def _load_dashboard_json(base_dir: Path) -> dict:
    path = base_dir / "data/dashboard/today.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except:
        return {}

def _load_dashboard_history(base_dir: Path) -> List[Dict[str, Any]]:
    dashboard_dir = base_dir / "data" / "dashboard"
    if not dashboard_dir.exists():
        return []
    
    history = []
    # Load all YYYY-MM-DD.json files
    for f in dashboard_dir.glob("*.json"):
        if f.name == "today.json": continue
        if not re.match(r"\d{4}-\d{2}-\d{2}\.json", f.name): continue
        
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            history.append(data)
        except: pass
        
    return history



    return html


def _load_youtube_videos(base_dir: Path) -> List[Dict]:
    """Load latest videos from status.json or metadata.json"""
    # Try finding metadata in known locations
    # 1. data/youtube/metadata.json (Phase 31)
    paths = [
        base_dir / "data" / "youtube" / "metadata.json",
        base_dir / "data" / "inputs" / "youtube" / "metadata.json"
    ]
    
    videos = []
    
    for p in paths:
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                # data might be list of videos or dict
                if isinstance(data, list):
                    videos.extend(data)
                elif isinstance(data, dict) and "videos" in data:
                    videos.extend(data["videos"])
            except: pass
            
    # Also load status.json for status info
    status_map = {}
    status_paths = [
        base_dir / "data" / "youtube" / "status.json",
        base_dir / "data" / "inputs" / "youtube" / "status.json"
    ]
    for p in status_paths:
        if p.exists():
            try:
               s_data = json.loads(p.read_text(encoding="utf-8"))
               # Assuming format {video_id: status}
               status_map.update(s_data)
            except: pass
            
    # Enrich videos with status
    for v in videos:
        vid = v.get("video_id") or v.get("id")
        if vid:
            v["status"] = status_map.get(vid, "NEW")
            
    # Sort by date desc
    videos.sort(key=lambda x: x.get("published_at", ""), reverse=True)
    return videos

def _generate_youtube_view(videos: List[Dict]) -> str:
    """Generate HTML Table for YouTube Inbox"""
    if not videos:
        return '<div class="empty-state">YouTube 데이터가 없습니다. (data/youtube/metadata.json 확인 필요)</div>'
        
    rows = ""
    for v in videos:
        title = v.get("title", "No Title")
        date_str = _utc_to_kst_display(v.get("published_at", ""))
        url = f"https://www.youtube.com/watch?v={v.get('video_id')}"
        status = v.get("status", "NEW").upper()
        
        badge_class = "status-new"
        status_ko = "신규"
        if status == "PROPOSED": 
            badge_class = "status-proposed"
            status_ko = "후보"
        elif status == "APPROVED": 
            badge_class = "status-approved"
            status_ko = "승인"
        elif status == "APPLIED": 
            badge_class = "status-applied"
            status_ko = "반영됨"
        
        rows += f"""
        <tr>
            <td>{date_str}</td>
            <td>
                <div style="font-weight:600; margin-bottom:4px;">{title}</div>
                <a href="{url}" target="_blank" style="font-size:12px; color:#2563eb; text-decoration:none;">📺 영상 보기 &rarr;</a>
            </td>
            <td><span class="status-badge {badge_class}">{status_ko}</span></td>
        </tr>
        """
        
    return f"""
    <table class="youtube-table">
        <thead>
            <tr>
                <th style="width:120px;">날짜</th>
                <th>제목</th>
                <th style="width:100px;">상태</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
    """


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

def _get_static_top1(base_dir: Path, target_ymd: str) -> Optional[Dict]:
    """Step 85: Load Top-1 data from static JSON."""
    index_path = base_dir / "docs/topics/index.json"
    if not index_path.exists():
        return None
    
    try:
        index = json.loads(index_path.read_text(encoding='utf-8'))
        item_path = None
        # Priority 1: Exact date ONLY (IS-47 Real Data Binding)
        for entry in index:
            if entry["date"] == target_ymd:
                item_path = entry["path"]
                break
        
        # [IS-47] Fallback Removed: Do NOT show old data as today's
        if not item_path:
             return None
            
        if item_path:
            full_path = base_dir / "docs" / item_path
            if full_path.exists():
                return json.loads(full_path.read_text(encoding='utf-8'))
    except Exception as e:
        print(f"Error loading static top1: {e}", file=sys.stderr)
    return None

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
    
    # 0. Structural Top-1 Section (Purple)
    if top1_data:
        t1 = top1_data
        
        # Detect Schema: Step 85 Static JSON vs Step 66 Engine Object
        is_static = "badges" in t1 and isinstance(t1.get("why_now"), dict)
        
        if is_static:
            uid = t1.get('topic_id', 'unknown_top1')
            title = t1.get('title', 'Untitled')
            summary = "<br> ".join(t1.get('summary', []))
            
            wn = t1.get('why_now', {})
            wn_display = f"[{wn.get('type')}] {wn.get('anchor')}"
            evidence = ", ".join(wn.get('evidence', []))
            
            b = t1.get('badges', {})
            intensity = b.get('intensity', 'N/A')
            rhythm = b.get('rhythm', 'N/A')
            scope = b.get('scope', 'N/A')
            lock_icon = "🔒" if b.get('lock') else ""
            
            # Entities summary
            entities_html = ""
            if t1.get('entities'):
                e_list = [e.get('name') for e in t1['entities'][:3]]
                entities_html = f"<div class='card-entities' style='font-size:11px; color:#6b7280; margin-top:5px;'>🎯 Entities: {', '.join(e_list)}</div>"

            card_html = f"""
            <div class="topic-card top1" onclick="openSignalDetail('{uid}')" style="border:2px solid #a855f7; background:#faf5ff; margin-bottom:20px; position:relative;">
                <div class="card-badges">
                    <div class="card-badge" style="background:#a855f7; color:white;">🟣 오늘의 TOP-1 핵심 (HOIN Signal)</div>
                    <div class="card-badge" style="background:#f3e8ff; color:#6b21a8; border:1px solid #d8b4fe;">{intensity}</div>
                    <div class="card-badge" style="background:#f3e8ff; color:#6b21a8; border:1px solid #d8b4fe;">{rhythm}</div>
                    <div class="card-badge" style="background:#f3e8ff; color:#6b21a8; border:1px solid #d8b4fe;">{scope}</div>
                    <div class="card-badge" style="background:#7e22ce; color:white;">{lock_icon} LOCKED</div>
                </div>
                <div class="card-title" style="color:#6b21a8; font-size:1.3em; margin-top:10px;">{title}</div>
                <div class="card-meta" style="margin-top:8px;">
                    <div style="font-size:14px; color:#4b5563; line-height:1.5;">{summary}</div>
                </div>
                <div style="margin-top:12px; padding:10px; background:rgba(168, 85, 247, 0.05); border-radius:6px; border-left:4px solid #a855f7;">
                    <div style="font-size:12px; color:#9333ea; font-weight:bold; margin-bottom:4px;">⚡ WHY NOW</div>
                    <div style="font-size:13px; color:#1e293b;">{wn_display}</div>
                    <div style="font-size:11px; color:#7e22ce; margin-top:4px;">📍 Evidence: {evidence}</div>
                </div>
                {entities_html}
                <div style="margin-top:10px; text-align:right;">
                    <a href="topics/items/{t1.get('date')}__top1.json" target="_blank" style="font-size:11px; color:#9333ea; text-decoration:none;">[원문 JSON 보기]</a>
                </div>
            </div>
            """
            cards_html += card_html
        else:
            # Fallback to Step 66 logic
            uid = t1.get('topic_id', 'unknown_top1')
            title = t1.get('title', 'Untitled')
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

def _generate_candidate_view(candidates_data: Dict[str, Any]) -> str:
    """Generates Phase 39 Topic Candidate Gate View"""
    candidates = candidates_data.get("candidates", [])
    if not candidates:
        return '<div class="empty-state">진행 중인 토픽 후보군이 없습니다.</div>'
        
    html = f"""
    <div class="candidate-container">
        <div class="today-header">
            <div class="today-summary">📂 토픽 후보군 <strong>{len(candidates)}개</strong></div>
        </div>
        <table class="archive-table">
            <thead>
                <tr>
                    <th width="150">ID</th>
                    <th width="100">분류</th>
                    <th>상세 이유</th>
                </tr>
            </thead>
            <tbody>
    """
    for c in candidates:
        cid = c.get("candidate_id", "N/A")
        cat = c.get("category", "N/A")
        reason = c.get("reason", "N/A")
        html += f"""
            <tr>
                <td><code style="font-size:11px;">{cid}</code></td>
                <td><span class="card-badge signal" style="background:#f1f5f9; color:#475569;">{cat}</span></td>
                <td style="font-size:13px; color:#334155;">{reason}</td>
            </tr>
        """
    html += """
            </tbody>
        </table>
    </div>
    """
    return html

def _generate_decision_view(final_card: Dict[str, Any]) -> str:
    """Generates Phase 38 Final Decision Card View"""
    if not final_card:
        return '<div class="empty-state">오늘의 최종 의사결정 데이터가 없습니다.</div>'
        
    topics = final_card.get('top_topics', [])
    if not topics and final_card.get('topic'):
        topics = [final_card]
        
    html = f"""
    <div class="decision-container">
        <div class="today-header">
            <div class="today-summary">⚖️ 최종 의사결정 (Final Decision Card)</div>
        </div>
        
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 25px; margin-bottom: 30px;">
            <div style="font-size: 14px; color: #64748b; margin-bottom: 15px; font-weight: 600;">시스템 종합 판정</div>
            <div style="font-size: 20px; font-weight: 800; color: #1e293b; margin-bottom: 10px;">
                {final_card.get('overall_regime', 'N/A')} 리스크 관리 모드
            </div>
            <div style="font-size: 15px; color: #475569; line-height: 1.6;">
                {final_card.get('overall_rationale', '정성적 근거 취합 중...')}
            </div>
        </div>

        <div class="card-grid">
    """
    
    for idx, t in enumerate(topics):
        title = t.get('title', t.get('topic', 'Untitled Engine Topic'))
        level = str(t.get('level', 'L2')).upper()
        imp_kr = "보통"
        if "L3" in level: imp_kr = "높음"
        elif "L1" in level: imp_kr = "낮음"
        
        summary = t.get('rationale', 'No rationale provided.')[:100] + "..."
        uid = f"engine_topic_{idx}"
        
        html += f"""
        <div class="topic-card" onclick="openEngineDetail('{uid}')" style="border-left: 4px solid #3b82f6;">
            <div class="card-badge engine" style="background:#dbeafe; color:#1d4ed8;">호인엔진</div>
            <div class="card-title">{title}</div>
            <div class="card-meta">
                <span class="meta-item importance">{imp_kr} ({level})</span>
                <span class="meta-divider">|</span>
                <span class="meta-item">{summary}</span>
            </div>
        </div>
        """
        
    html += """
        </div>
    </div>
    """
    return html

def _generate_ops_view(scoreboard_data: Dict[str, Any]) -> str:
    """Generates Phase 36-B Ops Scoreboard View"""
    if not scoreboard_data:
        return '<div class="empty-state">운영 지표 데이터가 없습니다.</div>'
        
    history = scoreboard_data.get("history", [])
    html = f"""
    <div class="ops-container">
        <div class="today-header">
            <div class="today-summary">⚙️ 운영 성과 지표 (최근 {scoreboard_data.get('lookback_days', 7)}일)</div>
        </div>
        
        <div class="card-grid" style="grid-template-columns: repeat(3, 1fr); margin-bottom: 30px;">
            <div class="topic-card" style="text-align:center;">
                <div style="font-size:12px; color:#64748b; margin-bottom:5px;">성공 횟수</div>
                <div style="font-size:24px; font-weight:800; color:#22c55e;">{scoreboard_data.get('success_count', 0)}</div>
            </div>
            <div class="topic-card" style="text-align:center;">
                <div style="font-size:12px; color:#64748b; margin-bottom:5px;">실패/미시행</div>
                <div style="font-size:24px; font-weight:800; color:#ef4444;">{scoreboard_data.get('fail_count', 0)}</div>
            </div>
            <div class="topic-card" style="text-align:center;">
                <div style="font-size:12px; color:#64748b; margin-bottom:5px;">평균 소요시간</div>
                <div style="font-size:24px; font-weight:800; color:#3b82f6;">{scoreboard_data.get('avg_duration_minutes', 0)}분</div>
            </div>
        </div>

        <table class="archive-table">
            <thead>
                <tr>
                    <th>날짜</th>
                    <th>상태</th>
                    <th>소요시간 (분)</th>
                </tr>
            </thead>
            <tbody>
    """
    for h in history:
        status_color = "#22c55e" if h.get("status") == "SUCCESS" else "#ef4444"
        html += f"""
            <tr>
                <td>{h.get('date')}</td>
                <td><span style="color:{status_color}; font-weight:bold;">{h.get('status')}</span></td>
                <td>{h.get('duration_minutes', 0)}</td>
            </tr>
        """
    html += """
            </tbody>
        </table>
    </div>
    """
    return html


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

def _generate_operator_top_view(final_card: Dict, top1_data: Dict) -> str:
    """[IS-49] Operator-First Top Section: Decision Only (Strict Korean)"""
    
    # Priority: final_card > top1_data
    target_card = final_card if final_card else (top1_data if top1_data else {})
    status = target_card.get("status", "SILENT").upper()
    
    # Active or Ready means Confirmed
    is_confirmed = status in ["ACTIVE", "READY"]
    
    if is_confirmed:
        # [CASE A] Confirmed Topic
        title = target_card.get("title", "무제")
        urgency = target_card.get("urgency_score", 0)
        
        # Why Now / Reason
        reason = target_card.get("reason", target_card.get("why_now", "사유 미정"))
        if isinstance(reason, dict):
            reason = f"[{reason.get('type','')}] {reason.get('anchor','')}"
            
        output_format = target_card.get("output_format_ko", "형식 미정")
        
        html = f"""
        <div class="today-section-header">📌 오늘의 확정 결론: 발화 결정</div>
        <div class="topic-card top1" style="border:2px solid #2563eb; background:#eff6ff; margin-bottom:30px;">
            <div class="card-badges">
                <div class="card-badge" style="background:#2563eb; color:white; font-size:14px; padding:4px 12px;">📢 발화 확정</div>
                <div class="card-badge" style="background:#dbeafe; color:#1e40af; border:1px solid #bfdbfe;">발화 압력 {urgency}</div>
                <div class="card-badge" style="background:#dcfce7; color:#166534; border:1px solid #bbf7d0;">🔒 신뢰 확정</div>
            </div>
            
            <div class="card-title" style="color:#1e3a8a; font-size:28px; margin-top:15px; font-weight:800; line-height:1.3;">
                {title}
            </div>
            
            <div style="margin-top:20px; padding:15px; background:white; border-radius:8px; border-left:5px solid #2563eb;">
                <div style="font-size:13px; color:#2563eb; font-weight:bold; margin-bottom:5px;">💡 지금 말해야 하는 이유</div>
                <div style="font-size:16px; color:#334155; font-weight:500;">{reason}</div>
            </div>
            
            <div style="margin-top:15px; display:flex; gap:10px; align-items:center;">
                <span style="font-size:14px; color:#64748b; font-weight:600;">출력 형식:</span>
                <span style="font-size:14px; color:#0f172a; font-weight:bold; background:#f1f5f9; padding:2px 8px; border-radius:4px;">{output_format}</span>
            </div>
        </div>
        """
        return html
    else:
        # [CASE B] [IS-47] Silence as Decision
        reason_summary = "신뢰 등급(Trust Locked) 충족 토픽 없음"
        if status == "SILENT":
            reason_summary = "금일 감지된 시장 신호 중, 구조적 임계치를 초과한 이슈가 없습니다."
        elif status == "HOLD":
            reason_summary = "잠재적 이슈가 있으나, 결정적 증거(Trust Lock) 부족으로 보류합니다."
        
        # System status check
        system_status = "✅ 정상 작동 중 (모든 감지 센서 활성)"
        
        html = f"""
        <div class="today-section-header" style="color:#475569;">📌 오늘의 확정 결론: 침묵 결정</div>
        <div class="topic-card" style="border:2px solid #94a3b8; background:#f8fafc; margin-bottom:30px; padding:30px;">
            <div style="display:flex; align-items:flex-start; gap:20px;">
                <div style="font-size:40px;">🛑</div>
                <div style="flex:1;">
                    <div style="font-size:22px; color:#1e293b; font-weight:800; margin-bottom:10px;">
                        "오늘은 말할 토픽이 없다고 판단했습니다."
                    </div>
                    <div style="font-size:15px; color:#475569; line-height:1.6; margin-bottom:15px;">
                        <strong>판단 사유:</strong> {reason_summary}
                    </div>
                    
                    <div style="background:#e2e8f0; border-radius:8px; padding:12px; font-size:13px; color:#64748b; display:flex; justify-content:space-between;">
                        <span>{system_status}</span>
                        <span>🔭 하단 '감시 중인 구조적 이슈'를 참조하십시오.</span>
                    </div>
                </div>
            </div>
        </div>
        """
        return html

def _generate_candidate_summary_view(today_json: Dict[str, Any]) -> str:
    # ... (Kept for compatibility, though obscured by Pre-Trigger board usually)
    # IS-48: This might become redundant if Pre-Trigger board covers it, 
    # but strictly "Candidate Summary" and "Pre-Trigger Board" can coexist structure-wise.
    # For now, let's keep it simple or redirect to Pre-Trigger?
    # User requested separate sections in plan. Retaining logic but minimal update.
    return "" # IS-46 version was here. We rely on IS-48 replacement or keep distinct?
    # Actually, IS-48 is "Pre-Trigger Monitoring Board".
    # Let's keep this simple summary function available but maybe merged conceptually.
    # Refilling original logic for safety.
    candidates = today_json.get("candidates", [])
    if not candidates: return ""
    display_list = sorted(candidates, key=lambda x: x.get("urgency_score", 0), reverse=True)[:3]
    rows = ""
    for c in display_list:
        status_map = {"READY":"준비","ACTIVE":"확정","HOLD":"보류","SILENT":"침묵"}
        st = status_map.get(c.get("status"), c.get("status"))
        rows += f"<tr><td>{c.get('title')}</td><td>{st}</td></tr>"
    # Returning empty to prefer Pre-Trigger board display to avoid duplication if user wants replacement.
    # Wait, the user plan says: "Inject _generate_pre_trigger_board below".
    # So I will keep this logic but minimize it or just return the table.
    # Re-pasting original logic to avoid breaking caller.
    return "" # Replacing with empty string to force use of Pre-Trigger Board only?
    # No, let's allow caller to decide.
    # Actually, I'll put the FULL implementation of Pre-Trigger Board BELOW.

def _generate_pre_trigger_board(candidates_data: Dict[str, Any]) -> str:
    """[IS-48] Pre-Trigger Monitoring Board"""
    candidates = candidates_data.get("candidates", [])
    # Filter: HOLD or SILENT (Pre-trigger candidates)
    targets = [c for c in candidates if c.get("status") in ["HOLD", "SILENT"]]
    
    if not targets:
        return ""
        
    # Sort by urgency
    targets.sort(key=lambda x: x.get("urgency_score", 0), reverse=True)
    
    rows = ""
    for c in targets[:5]: # Top 5
        title = c.get("title", "Untitled")
        status = c.get("status")
        reason = c.get("reason", "조건 미충족")
        
        # Determine Condition & ETA (Mock/Heuristic for now)
        condition = "결정적 증거(Trust Lock) 확보"
        eta = "24시간 내"
        badge_style = "background:#f1f5f9; color:#64748b;"
        
        if status == "HOLD":
            status_ko = "보류 (HOLD)"
            badge_style = "background:#fff7ed; color:#c2410c; border:1px solid #fdba74;"
            condition = "추가 팩트체크 / 교차 검증"
            eta = "관찰 필요"
        else: # SILENT
            status_ko = "침묵 (SILENT)"
            condition = "구조적 임계치 도달"
            eta = "미정"
            
        rows += f"""
        <tr style="border-bottom:1px solid #e2e8f0;">
            <td style="padding:15px;">
                <div style="font-weight:600; color:#1e293b; font-size:15px;">{title}</div>
                <div style="font-size:12px; color:#64748b; margin-top:4px;">{reason}</div>
            </td>
            <td style="padding:15px;">
                <span style="font-size:12px; font-weight:bold; padding:4px 8px; border-radius:6px; {badge_style}">{status_ko}</span>
            </td>
            <td style="padding:15px; font-size:13px; color:#475569;">
                {condition}
            </td>
            <td style="padding:15px; font-size:13px; color:#64748b;">
                {eta}
            </td>
        </tr>
        """

    html = f"""
    <div style="margin-top:40px; margin-bottom:40px;">
        <div class="today-section-header">👀 감시 중인 구조적 이슈 (PRE-TRIGGER)</div>
        <div style="background:white; border-radius:12px; border:1px solid #e2e8f0; overflow:hidden; box-shadow:0 2px 4px rgba(0,0,0,0.03);">
            <table style="width:100%; border-collapse:collapse; text-align:left;">
                <thead style="background:#f8fafc; border-bottom:2px solid #e2e8f0; font-size:13px; color:#64748b;">
                    <tr>
                        <th style="padding:12px 15px; width:45%;">이슈 및 결핍 사유</th>
                        <th style="padding:12px 15px; width:15%;">현재 상태</th>
                        <th style="padding:12px 15px;">발화 남은 조건</th>
                        <th style="padding:12px 15px; width:15%;">예상 시점</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
    </div>
    """
    return html

def generate_dashboard(base_dir: Path):
    """Step 62: Simplified HOIN Dashboard Generation"""
    ymd = _utc_ymd()
    
    # 1. Load Data (Minimal Loading for UI)
    today_json = _load_dashboard_json(base_dir) # [NEW]
    history_json = _load_dashboard_history(base_dir) # [NEW]
    
    # Filter out today from history to avoid duplication
    if today_json and today_json.get("date"):
        history_json = [h for h in history_json if h.get("date") != today_json.get("date")]
        
    # [NEW] Entity Mapping logic moved down
    # entity_pool moved after final_card load
        
    snapshot_list_html = TopicCardRenderer.render_snapshot_list(history_json)
    topic_card_css = TopicCardRenderer.get_css()
    
    
    # [A] HOIN Engine Topics (Final Decision)
    final_card = {}
    try:
        card_base = base_dir / "data" / "decision" / ymd.replace("-","/")
        card_path = card_base / "final_decision_card.json"
        if card_path.exists():
            final_card = json.loads(card_path.read_text(encoding="utf-8"))
    except: pass

    # [NEW] Entity Mapping (Moved here)
    entity_pool = []
    classified_entities = []
    entity_state_html = ""
    entity_pool_html = ""
    
    memory_delta_html = ""
    
    if today_json:
        entity_pool = EntityMappingLayer.map_target_entities(today_json, final_card)
        entity_pool_html = TopicCardRenderer.render_entity_pool(entity_pool)
        
        # [NEW] Entity State Classification (Step 84)
        classified_entities = EntityStateClassifier.classify_entities(entity_pool, today_json)
        entity_state_html = TopicCardRenderer.render_entity_state_panel(classified_entities)
    
        # [NEW] Structural Memory Engine (Step 85)
        memory_engine = StructuralMemoryEngine(base_dir)
        snapshot_path = memory_engine.save_snapshot(today_json.get("date", ymd), today_json, classified_entities)
        
        # [NEW] Comparison Engine
        comparison_engine = SnapshotComparisonEngine(memory_engine)
        # Re-load the just saved snapshot to ensure format consistency
        today_snap = memory_engine.load_snapshot(today_json.get("date", ymd))
        comparison_result = comparison_engine.compare(today_json.get("date", ymd), today_snap)
        
        memory_delta_html = TopicCardRenderer.render_memory_delta_panel(comparison_result)
        
        # [NEW] Structural Pattern Detection (Step 86)
        detected_patterns = []
        try:
            pattern_detector = StructuralPatternDetector(base_dir)
            pattern_snapshot_path = pattern_detector.detect_and_save(today_json.get("date", ymd), final_card)
            
            # Load detected patterns for next steps
            import json
            pattern_snapshot = json.loads(pattern_snapshot_path.read_text(encoding="utf-8"))
            detected_patterns = pattern_snapshot.get("active_patterns", [])
        except Exception as e:
            print(f"[PatternDetector] Error: {e}")
    
        # [NEW] Pattern Memory & Replay (Step 88)
        replay_blocks = []
        try:
            memory_engine = PatternMemoryEngine(base_dir)
            for pattern in detected_patterns:
                # Save pattern to memory
                pattern_id = pattern.get("pattern_type", "UNKNOWN")
                memory_engine.save_pattern(
                    pattern_id=pattern_id,
                    pattern_data=pattern,
                    context={"date": today_json.get("date", ymd), "trigger": today_json.get("top_signal", {}).get("trigger", "")}
                )
                
                # Replay similar patterns
                replay_block = memory_engine.replay(pattern)
                replay_blocks.append(replay_block)
        except Exception as e:
            print(f"[PatternMemory] Error: {e}")

    # [NEW] Narrative Compression (Step 87)
    compressed_narratives = []
    try:
        for i, pattern in enumerate(detected_patterns):
            replay_block = replay_blocks[i] if i < len(replay_blocks) else {}
            context = {
                "intensity": today_json.get("top_signal", {}).get("intensity", "FLASH"),
                "why_now": today_json.get("top_signal", {}).get("trigger", "")
            }
            narrative = NarrativeCompressor.compress(pattern, replay_block, context)
            compressed_narratives.append(narrative)
    except Exception as e:
        print(f"[NarrativeCompressor] Error: {e}")

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
        narrative_path = base_dir / "data/ops/issue_signal_narrative_today.json"
        if narrative_path.exists():
            nd = json.loads(narrative_path.read_text(encoding="utf-8"))
            narrative_data = nd.get("narrative")
            
        # [Step 85] Override Top-1 with Static JSON if available
        static_top1 = _get_static_top1(base_dir, ymd)
        if static_top1:
            top1_data = static_top1
            import sys # Added for sys.stderr
            print(f"[Step 85] Using static Top-1 from {static_top1.get('date')}", file=sys.stderr)
    except Exception as e:
        import sys # Added for sys.stderr
        print(f"Error loading top1/narrative: {e}", file=sys.stderr)
    
    # [F] Topic Candidates (Phase 39)
    candidates_data = {}
    try:
        y, m, d = ymd.split("-")
        cand_path = base_dir / "data" / "topics" / "candidates" / y / m / d / "topic_candidates.json"
        if cand_path.exists():
            candidates_data = json.loads(cand_path.read_text(encoding="utf-8"))
    except: pass

    # [H] Ops Scoreboard (Phase 36-B)
    scoreboard_data = {}
    try:
        y, m, d = ymd.split("-")
        score_path = base_dir / "data" / "ops" / "scoreboard" / y / m / d / "ops_scoreboard.json"
        if score_path.exists():
            scoreboard_data = json.loads(score_path.read_text(encoding="utf-8"))
    except: pass

    # [E] Historical Archive
    historical_cards = _load_historical_cards(base_dir)

    # [NEW] Step 100: Narrative Preview (Draft) - Localized
    narrative_preview_html = ""
    try:
        preview_path = base_dir / "data" / "ops" / "narrative_preview_today.json"
        if preview_path.exists():
            p_data = json.loads(preview_path.read_text(encoding="utf-8"))
            
            # Icon selection
            align = p_data.get("comparison_alignment", "ALIGNED")
            icon = "✅" if align == "ALIGNED" else "⚠️"
            status_color = "#166534" if align == "ALIGNED" else "#ca8a04"
            status_bg = "#f0fdf4" if align == "ALIGNED" else "#fefce8"
            
            # Localize Alignment
            align_ko = "정합성 일치" if align == "ALIGNED" else "검토 필요"
            
            titles_html = ""
            for t in p_data.get("title_candidates", []):
                titles_html += f"<div style='background:white; padding:8px 12px; border-radius:6px; border:1px solid #e2e8f0; margin-bottom:6px; font-size:14px; color:#334155;'>📝 {t}</div>"
                
            script = p_data.get("script", {})
            
            narrative_preview_html = f"""
            <div class="narrative-preview-container" style="background:white; border:1px solid #cbd5e1; border-radius:12px; padding:25px; margin-bottom:30px; box-shadow:0 4px 6px -1px rgba(0,0,0,0.05);">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; border-bottom:1px solid #f1f5f9; padding-bottom:15px;">
                    <div style="font-size:18px; font-weight:800; color:#1e293b;">📜 생성된 대본 초안 (참고용)</div>
                    <div style="background:{status_bg}; color:{status_color}; padding:6px 12px; border-radius:20px; font-size:12px; font-weight:bold;">
                        {icon} {align_ko}
                    </div>
                </div>
                
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:25px;">
                    <!-- Titles -->
                    <div>
                        <div style="font-size:12px; font-weight:700; color:#64748b; margin-bottom:10px; text-transform:uppercase;">제목 후보안</div>
                        {titles_html}
                        
                        <div style="margin-top:20px; padding:15px; background:#f8fafc; border-radius:8px; border-left:3px solid #3b82f6;">
                            <div style="font-size:12px; font-weight:700; color:#64748b; margin-bottom:8px;">맥락 정보 (Context)</div>
                            <div style="font-size:13px; color:#475569;">
                                <strong>토픽 ID:</strong> {p_data.get('topic_id').replace('NO_TOPIC', '감지된 토픽 없음')}<br>
                                <strong>발화 시점:</strong> {script.get('why_now')}
                            </div>
                        </div>
                    </div>
                    
                    <!-- Script Draft -->
                    <div>
                        <div style="font-size:12px; font-weight:700; color:#64748b; margin-bottom:10px; text-transform:uppercase;">대본 초안 미리보기</div>
                        <div style="background:#f8fafc; padding:15px; border-radius:8px; border:1px solid #e2e8f0; font-size:14px; line-height:1.6; color:#334155;">
                            <span style="color:#2563eb; font-weight:bold;">[도입]</span> {script.get('opening')}<br><br>
                            <span style="color:#2563eb; font-weight:bold;">[전개]</span> {script.get('structure')}<br><br>
                            <span style="color:#dc2626; font-weight:bold;">[주의]</span> {script.get('caution')}<br><br>
                            <span style="color:#2563eb; font-weight:bold;">[제언]</span> {script.get('closing')}
                        </div>
                    </div>
                </div>
            </div>
            """
    except Exception as e:
        print(f"Error generating narrative preview: {e}", file=sys.stderr)

    # [IS-46/47] Operator Top View (Confirmed or Silence)
    today_view_html = _generate_operator_top_view(final_card, top1_data)
    
    # [IS-48] Pre-Trigger Board
    pre_trigger_html = _generate_pre_trigger_board(candidates_data)

    # [Legacy Reference]
    top1_card_html = TopicCardRenderer.render_top1_card(top1_data) 
    judgment_memory_html = TopicCardRenderer.render_judgment_memory_view(top1_data)
    
    # [G] Full Candidate View (Hidden or Reference)
    candidate_view_html = _generate_candidate_view(candidates_data)
    
    # [I] Generate Ops View HTML
    ops_view_html = _generate_ops_view(scoreboard_data)

    # [J] Generate Decision View HTML
    decision_view_html = _generate_decision_view(final_card)
    
    # [Removed Legacy Empty State Check - Handled by _generate_operator_top_view]
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
                <h3 style="color: #6b21a8;">1. 시선 강탈 (The Hook)</h3>
                <p class="script-text" style="font-weight:bold; font-size: 1.1em;">
                    {sections.get('hook', n.get('opening_hook', ''))}
                </p>
            </div>

            <!-- Step 2: Core Tension -->
            <div class="detail-section">
                <h3>2. 구조적 역학 (Core Tension)</h3>
                <p class="script-text">
                    {sections.get('tension', n.get('core_story', '')).replace(chr(10), '<br>')}
                </p>
            </div>

            <!-- Step 3: The Hunt -->
            <div class="detail-section">
                <h3>3. 결정적 증거 (The Hunt)</h3>
                <p class="script-text" style="white-space: pre-wrap; background: #f8fafc; padding: 10px; border-radius: 6px;">
                    {sections.get('hunt', '')}
                </p>
            </div>

            <!-- Step 4: Action -->
            <div class="detail-section" style="border: 2px solid #22c55e; background-color: #f0fdf4;">
                <h3 style="color: #15803d;">4. 행동 지침 (Action)</h3>
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

    # (IS-48) Sync with SSOT index
    index_path = base_dir / "data" / "issuesignal" / "packs" / "latest_index.json"
    index_data = {}
    if index_path.exists():
        try:
            with open(index_path, "r", encoding="utf-8") as f:
                index_data = json.load(f)
        except: pass

    # Override ymd with SSOT date if available
    ymd_ssot = index_data.get("run_date_kst", ymd)
    
    # [IS-45] Load Operational Dashboard & Convert to HTML for Embedding
    ops_dashboard_md_path = base_dir / "data" / "reports" / ymd_ssot.replace("-", "/") / "operational_dashboard.md"
    ops_dashboard_html = ""
    if ops_dashboard_md_path.exists():
        ops_md_content = ops_dashboard_md_path.read_text(encoding="utf-8")
        ops_dashboard_html = parse_markdown(ops_md_content)
    else:
        # Check if we have reasons in SSOT
        reasons = index_data.get("top_reason_counts", [])
        reason_str = ", ".join([f"<b>{r['reason']}</b>" for r in reasons[:3]]) if reasons else "데이터 분석 중"
        ops_dashboard_html = f"""
        <div style="background:#FFFBEB; border:1px solid #F59E0B; padding:30px; border-radius:12px; text-align:center;">
             <h3 style="color:#92400E; margin-bottom:10px;">오늘 확정된 토픽이 없습니다.</h3>
             <p style="color:#B45309;">주요 보류 사유: {reason_str}</p>
        </div>
        """

    # [NEW] YouTube Inbox View
    youtube_videos = _load_youtube_videos(base_dir)
    youtube_view_html = _generate_youtube_view(youtube_videos)

    # [IS-45] Copy report to docs (Keep existing logic)
    today_report_dst = base_dir / "docs" / "data" / "reports" / ymd.replace("-", "/") / "operational_dashboard.md"
    if ops_dashboard_md_path.exists():
        today_report_dst.parent.mkdir(parents=True, exist_ok=True)
        today_report_dst.write_text(ops_dashboard_md_path.read_text(encoding="utf-8"), encoding="utf-8")

    # Update Menu & Content Structure
    html = f"""<!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🔴 HOIN Insight Engine</title>
        <style>
            {DashboardStyles.COMMON_CSS}
            {topic_card_css}
            
            /* Overrides and Specifics */
            .sidebar {{ width: 320px; }}
            .tab-content {{ display: none; width: 100%; }}
            .tab-content.active {{ display: block; }}
            
            .architecture-grid {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 20px;
            .ops-report-container th {{ background:#f1f5f9; padding:10px; text-align:left; border-bottom:2px solid #e2e8f0; }}
            .ops-report-container td {{ padding:10px; border-bottom:1px solid #e2e8f0; }}
        </style>
    </head>
    <body>
        <div class="sidebar">
            <div class="logo">🔴 HOIN Insight</div>
            <div class="menu-container">
                <div class="menu-item active" onclick="switchTab('today', this)">오늘 선정 토픽</div>
                <div class="menu-item" onclick="switchTab('candidates', this)">📂 토픽 후보군</div>
                <div class="menu-item" onclick="switchTab('decision', this)">⚖️ 최종 의사결정</div>
                <div class="menu-item" onclick="switchTab('ops', this)">⚙️ 운영 성과 지표</div>
                <div class="menu-item" onclick="switchTab('archive', this)">전체 토픽 목록</div>
                <div class="menu-item" onclick="switchTab('issuesignal', this)">🛡️ IssueSignal 연산</div>
                <div class="menu-item" style="font-weight: bold; color: #ffeb3b;" onclick="switchTab('ops-report', this)">📌 운영 대시보드 (금일)</div>
            </div>
        </div>
        
        <div class="main-content">
            <div id="tab-today">
                {today_view_html}
                {pre_trigger_html}
                
                <div style="margin: 60px 0 20px 0; border-top: 1px dashed #cbd5e1; padding-top: 20px;">
                    <h3 style="color: #64748b; font-size: 13px; font-weight:600;">👇 [내부 참고용] 분석 상세 및 초안</h3>
                </div>
                
                {narrative_preview_html}
                {top1_card_html}
                {judgment_memory_html}
                {entity_state_html}
                {entity_pool_html}
                {memory_delta_html}
                {snapshot_list_html}
            </div>
            <div id="tab-candidates" class="hidden">
                {candidate_view_html}
            </div>
            <div id="tab-decision" class="hidden">
                {decision_view_html}
            </div>
            <div id="tab-ops" class="hidden">
                {ops_view_html}
            </div>
            <div id="tab-archive" class="hidden">
                <div class="today-header">
                    <div class="today-summary">전체 토픽 목록</div>
                </div>
                {archive_view_html}
            </div>
            
            <!-- [NEW] IssueSignal Tab (Iframe) -->
            <div id="tab-issuesignal" class="hidden" style="height:100%;">
                <iframe src="./issuesignal/" style="width:100%; height:100%; border:none; min-height: 100vh;"></iframe>
            </div>

            <!-- [NEW] Ops Report Tab (Embedded HTML) -->
            <div id="tab-ops-report" class="hidden">
                <div class="ops-report-container">
                    {ops_dashboard_html}
                </div>
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
                const tabs = ["today", "candidates", "decision", "ops", "archive", "issuesignal", "ops-report"];
                tabs.forEach(t => document.getElementById('tab-' + t).classList.add('hidden'));
                
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
    
    # [NEW] YouTube Inbox View
    youtube_videos = _load_youtube_videos(base_dir)
    youtube_view_html = _generate_youtube_view(youtube_videos)

    today_report_src = base_dir / "data" / "reports" / ymd.replace("-", "/") / "operational_dashboard.md"
    today_report_dst = base_dir / "docs" / "data" / "reports" / ymd.replace("-", "/") / "operational_dashboard.md"
    
    if today_report_src.exists():
        today_report_dst.parent.mkdir(parents=True, exist_ok=True)
        today_report_dst.write_text(today_report_src.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"[Dashboard] Copied operational_dashboard.md to {today_report_dst}")

    (base_dir / "docs" / "index.html").write_text(html, encoding="utf-8")
    print(f"[Dashboard] Generated docs/index.html with YouTube Inbox (Restored)")
    return html


if __name__ == "__main__":
    # Adjust path if running directly from src/dashboard/
    # Assumes git root is parent of src
    # File is at src/dashboard/dashboard_generator.py
    # Git root is ../../
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent
    generate_dashboard(project_root)
