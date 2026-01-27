
from typing import Dict, List, Any

class TopicCardRenderer:
    """
    Step 82: Renders the "Human View Layer" for Economic Hunter Topics.
    Translates structured signals into cognitive UI cards.
    """

    @staticmethod
    def render_top1_card(data: Dict[str, Any]) -> str:
        """
        Renders the dominant Top-1 Topic Card.
        """
        if not data or not data.get('top_signal'):
            return TopicCardRenderer._render_empty_state()

        signal = data['top_signal']
        
        # Data Extraction
        title = signal.get('title', 'Unknown Signal')
        why_now = signal.get('why_now', '')
        trigger_type = signal.get('trigger', 'Unknown')
        intensity = signal.get('intensity', 'N/A')
        rhythm = signal.get('rhythm', 'N/A')
        pressure_type = signal.get('pressure_type', 'Structural')
        esc_count = signal.get('escalation_count', 0)
        scope_hint = signal.get('scope_hint', 'Single-Sector')
        date = data.get('date', 'Today')
        
        # Badge Logic
        whynow_badge_cls = "badge-whynow-default"
        if "Escalated" in why_now or esc_count > 0: whynow_badge_cls = "badge-whynow-escalated"
        elif "SmartMoney" in trigger_type: whynow_badge_cls = "badge-whynow-smartmoney"
        
        # Intensity Visuals
        intensity_icon = "⚡"
        if intensity == "DEEP_HUNT": intensity_icon = "🌊"
        elif intensity == "STRIKE": intensity_icon = "🎯"
        
        # Escalation Indicator
        esc_html = ""
        if esc_count > 0:
            esc_html = f'<span class="escalation-mark">🔥 +{esc_count} Accelerated</span>'

        return f"""
        <div class="topic-card-top1">
            <div class="top1-header-label">🟣 오늘의 구조적 핵심 이슈 (Top-1)</div>
            
            <div class="top1-body">
                <div class="top1-meta-row">
                    <span class="badge-whynow {whynow_badge_cls}">{trigger_type}</span>
                    <span class="badge-pressure">{pressure_type}</span>
                    <span class="badge-scope">{scope_hint}</span>
                    <span class="meta-date">{date}</span>
                </div>
                
                <h1 class="top1-title">{title}</h1>
                
                <div class="top1-context">
                    <div class="context-item">
                        <span class="context-label">WHY_NOW</span>
                        <span class="context-text">{why_now}</span>
                    </div>
                    <div class="context-item">
                        <span class="context-label">RHYTHM</span>
                        <span class="context-text"><strong>{intensity} {intensity_icon}</strong> // {rhythm}</span>
                    </div>
                </div>
                
                <div class="top1-footer">
                    {esc_html}
                    <button class="action-btn" onclick="openSignalDetail('top1_current')">🔍 분석 원문 보기</button>
                </div>
            </div>
        </div>
        """

    @staticmethod
    def render_snapshot_list(snapshots: List[Dict[str, Any]]) -> str:
        """
        Renders the list of previous snapshots.
        """
        if not snapshots:
            return ""

        # Sort Logic: Escalation > Intensity > Recency (Date desc)
        # Intensity mapping for sort
        int_map = {"FLASH": 1, "STRIKE": 2, "DEEP_HUNT": 3}
        
        def sort_key(s):
            sig = s.get('top_signal', {})
            esc = sig.get('escalation_count', 0)
            inte = int_map.get(sig.get('intensity', 'FLASH'), 0)
            date = s.get('date', '0000-00-00')
            return (esc, inte, date)

        sorted_snaps = sorted(snapshots, key=sort_key, reverse=True)
        
        cards_html = ""
        for s in sorted_snaps:
            sig = s.get('top_signal', {})
            title = sig.get('title', 'Unknown')
            date = s.get('date', 'Unknown')
            pressure = sig.get('pressure_type', 'Structural')
            esc_count = sig.get('escalation_count', 0)
            
            esc_badge = ""
            if esc_count > 0:
                esc_badge = f'<span class="list-esc-badge">🔥 +{esc_count}</span>'
            
            cards_html += f"""
            <div class="snapshot-list-item">
                <div class="list-date">{date}</div>
                <div class="list-body">
                    <div class="list-title">{title}</div>
                    <div class="list-meta">
                        <span class="list-pressure">{pressure}</span>
                        {esc_badge}
                    </div>
                </div>
                <button class="list-action-btn" onclick="openSignalDetail('archive_{date}')">View</button>
            </div>
            """
            
        return f"""
        <div class="snapshot-list-container">
            <h3 class="list-header">📅 Recent Structural Signals</h3>
            <div class="snapshot-list">
                {cards_html}
            </div>
        </div>
        """

    @staticmethod
    def _render_empty_state() -> str:
        return """
        <div class="empty-state-card">
            <div class="empty-icon">☕️</div>
            <h3>오늘은 구조적으로 확정된 이슈 시그널이 없습니다.</h3>
            <p>Scanning for potential triggers...</p>
        </div>
        """

    @staticmethod
    def get_css() -> str:
        return """
        /* Top-1 Card Styles */
        .topic-card-top1 {
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            border: 1px solid #e2e8f0;
            border-left: 4px solid #7c3aed; /* Purple */
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 10px 25px -5px rgba(124, 58, 237, 0.1), 0 8px 10px -6px rgba(0,0,0,0.05);
            margin-bottom: 40px;
            position: relative;
            overflow: hidden;
        }
        
        .top1-header-label {
            font-size: 11px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #7c3aed;
            margin-bottom: 16px;
        }
        
        .top1-meta-row {
            display: flex;
            gap: 8px;
            align-items: center;
            margin-bottom: 16px;
            flex-wrap: wrap;
        }
        
        /* Badges */
        .badge-whynow {
            font-size: 11px; font-weight: 700; padding: 4px 8px; border-radius: 4px;
            background: #f3e8ff; color: #6b21a8;
        }
        .badge-whynow-escalated { background: #fee2e2; color: #991b1b; }
        .badge-whynow-smartmoney { background: #dcfce7; color: #166534; }
        
        .badge-pressure {
            font-size: 11px; font-weight: 700; padding: 4px 8px; border-radius: 4px;
            background: #f1f5f9; color: #475569; border: 1px solid #e2e8f0;
        }
        
        .badge-scope {
            font-size: 11px; font-weight: 600; padding: 4px 8px; border-radius: 4px;
            background: #ffffff; color: #64748b; border: 1px dashed #cbd5e1;
        }
        
        .meta-date {
            margin-left: auto;
            font-size: 12px; color: #94a3b8; font-family: monospace;
        }
        
        /* Content */
        .top1-title {
            font-size: 26px;
            font-weight: 800;
            color: #1e293b;
            margin: 0 0 20px 0;
            line-height: 1.3;
            letter-spacing: -0.5px;
        }
        
        .top1-context {
            background: #ffffff;
            border-radius: 8px;
            padding: 16px;
            border: 1px solid #f1f5f9;
        }
        
        .context-item {
            display: flex;
            margin-bottom: 8px;
            align-items: baseline;
        }
        .context-item:last-child { margin-bottom: 0; }
        
        .context-label {
            width: 80px;
            font-size: 11px;
            font-weight: 700;
            color: #94a3b8;
            flex-shrink: 0;
        }
        
        .context-text {
            font-size: 14px;
            color: #334155;
            line-height: 1.5;
        }
        
        /* Footer */
        .top1-footer {
            margin-top: 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .escalation-mark {
            font-size: 12px;
            font-weight: 700;
            color: #ef4444;
            display: flex;
            align-items: center;
            gap: 4px;
        }
        
        .action-btn {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 600;
            color: #475569;
            cursor: pointer;
            transition: all 0.2s;
        }
        .action-btn:hover {
            background: #f8fafc;
            border-color: #cbd5e1;
            transform: translateY(-1px);
        }
        
        .empty-state-card {
            text-align: center;
            padding: 60px 20px;
            background: #f8fafc;
            border-radius: 12px;
            border: 2px dashed #e2e8f0;
        }
        .empty-icon { font-size: 40px; margin-bottom: 20px; }
        
        /* Snapshot List */
        .snapshot-list-container { margin-top: 30px; }
        .list-header { font-size: 14px; color: #64748b; margin-bottom: 15px; text-transform: uppercase; font-weight: 700; }
        
        .snapshot-list-item {
            display: flex;
            align-items: center;
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 10px;
            transition: transform 0.2s;
        }
        .snapshot-list-item:hover { transform: translateX(4px); border-color: #cbd5e1; }
        
        .list-date {
            width: 90px;
            font-size: 12px;
            color: #94a3b8;
            font-weight: 600;
            flex-shrink: 0;
        }
        
        .list-body { flex: 1; padding: 0 15px; }
        
        .list-title {
            font-size: 14px;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 4px;
        }
        
        .list-meta { display: flex; align-items: center; gap: 8px; }
        .list-pressure { font-size: 11px; color: #64748b; background: #f1f5f9; padding: 2px 6px; border-radius: 4px; }
        .list-esc-badge { font-size: 11px; color: #ef4444; font-weight: 700; }
        
        .list-action-btn {
            padding: 6px 12px;
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            color: #475569;
            font-size: 11px;
            font-weight: 600;
            cursor: pointer;
        }
        .list-action-btn:hover { background: #f1f5f9; color: #1e293b; }
        """

