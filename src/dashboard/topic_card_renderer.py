
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
        Supports both Step 66 (Engine Object) and Step 85 (Static JSON) schemas.
        """
        if not data:
            return TopicCardRenderer._render_empty_state()

        # Step 85 Schema detection
        is_static = "badges" in data and "topic_id" in data
        
        human_interpretation = "" # Initialize
        if is_static:
            signal = data
            title = signal.get('title', 'Unknown Topic')
            # Handle summary as list
            summary_list = signal.get('summary', [])
            summary_text = "<br> ".join(summary_list)
            
            wn = signal.get('why_now', {})
            why_now_text = f"[{wn.get('type', 'N/A')}] {wn.get('anchor', '')}"
            trigger_type = wn.get('type', 'Structural')
            
            badges = signal.get('badges', {})
            intensity = badges.get('intensity', 'FLASH')
            rhythm = badges.get('rhythm', 'N/A')
            pressure_type = "Structural"
            esc_count = 0 # Static JSON doesn't track escalation in same way yet
            scope_hint = badges.get('scope', 'Global')
            date = signal.get('date', 'Today')
        else:
            # Step 66 Schema
            if not data.get('top_signal'):
                return TopicCardRenderer._render_empty_state()
            signal = data['top_signal']
            title = signal.get('title', 'Unknown Signal')
            why_now_text = signal.get('why_now', '')
            trigger_type = signal.get('trigger', 'Unknown')
            intensity = signal.get('intensity', 'N/A')
            rhythm = signal.get('rhythm', 'N/A')
            pressure_type = signal.get('pressure_type', 'Structural')
            esc_count = signal.get('escalation_count', 0)
            scope_hint = signal.get('scope_hint', 'Single-Sector')
            date = data.get('date', 'Today')
        
        # Badge Logic
        whynow_badge_cls = "badge-whynow-default"
        if "Escalated" in why_now_text or esc_count > 0: whynow_badge_cls = "badge-whynow-escalated"
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
                <!-- [STEP 95] Decision Snapshot Block (10-second Summary) -->
                {TopicCardRenderer.render_decision_snapshot(data)}

                <!-- [STEP 96] Action Posture Layer -->
                {TopicCardRenderer.render_action_posture(data)}
                
                <!-- [STEP 93] Rewritten Judgment Status Line (Human Language) -->
                <div class="judgment-status-line" style="font-size: 15px; font-weight: bold; color: #7e22ce; margin-bottom: 8px;">
                    판단 상태: {data.get('judgment_stack', {}).get('state_label', '새로운 흐름 포착')}
                </div>
                
                <!-- [STEP 92] Narrative Drift Label (Muted) -->
                <div class="narrative-drift-label" style="font-size: 11px; color: #94a3b8; margin-bottom: 20px;">
                    {data.get('narrative_drift', {}).get('label', 'Narrative Stable (Recurring Structure)')}
                </div>

                <h1 class="top1-title" style="margin-bottom: 20px;">{title}</h1>

                <!-- [STEP 90-A] Human Interpretation Block (Judgment First) -->
                <div class="top1-interpretation" style="margin: 0 0 20px 0; padding: 0; background: transparent;">
                    <div style="font-size: 15px; color: #1e293b; line-height: 1.8; white-space: pre-line; font-weight: 500;">
                        {data.get('human_interpretation', '엔진이 구조적 유효성을 분석 중입니다.').replace('왜 지금 이 토픽인가', '').strip()}
                    </div>
                </div>

                <div style="height: 1px; background: #e2e8f0; margin-bottom: 20px;"></div>

                <!-- [STEP 90-A] Cognitive Badges (Evidence Layer) -->
                <div class="top1-meta-row" style="margin-bottom: 20px;">
                    <span class="badge-whynow {whynow_badge_cls}" style="font-size: 11px;">지금 다루는 이유: {trigger_type}</span>
                    <span class="badge-pressure" style="font-size: 11px;">압력 유형: {pressure_type}</span>
                    <span class="badge-scope" style="font-size: 11px;">범위: {scope_hint}</span>
                    <span class="badge-intensity" style="font-size: 11px; background: #f1f5f9; color: #475569; border: 1px solid #e2e8f0; padding: 2px 8px; border-radius: 4px;">강도: {intensity} {intensity_icon}</span>
                    <span class="meta-date">{date}</span>
                </div>
                
                <div class="top1-context">
                    <div class="context-item">
                        <span class="context-label">구조적 리듬</span>
                        <span class="context-text">{rhythm}</span>
                    </div>
                </div>
                
                <div class="top1-footer">
                    {esc_html}
                    <button class="action-btn" onclick="openSignalDetail('top1_current')">🔍 분석 원문 보기</button>
                    <a href="topics/items/{date}__top1.json" target="_blank" style="font-size:11px; color:#9333ea; text-decoration:none; margin-left: 10px;">[원문 JSON 보기]</a>
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
                <button class="list-action-btn" onclick="openSignalDetail('archive_{date}')">상세 보기</button>
            </div>
            """
            
        return f"""
        <div class="snapshot-list-container">
            <h3 class="list-header">📅 최근 구조적 시그널 이력</h3>
            <div class="snapshot-list">
                {cards_html}
            </div>
        </div>
        """

    @staticmethod
    def render_entity_state_panel(entities: List[Dict[str, Any]]) -> str:
        """
        Step 84: Renders the 'Decision Surface' (State Classification).
        """
        if not entities:
            return ""

        cards_html = ""
        for e in entities:
            name = e.get("name", "Unknown")
            # Role Localization Map
            role_map = {
                "EXECUTOR": "주도자 (Executor)",
                "BENEFICIARY": "수혜자 (Beneficiary)",
                "VICTIM": "피해자 (Victim)",
                "HEDGE": "헤지 수단 (Hedge)",
                "BOTTLENECK": "병목점 (Bottleneck)",
                "STRUCTURAL EXECUTOR": "구조적 주도자"
            }
            raw_role = e.get("role", "EXECUTOR").replace("STRUCTURAL ", "")
            role = role_map.get(raw_role, raw_role)
            
            state = e.get("state", "OBSERVE")
            justification = e.get("state_justification", [])
            
            # State Colors
            state_class = f"state-{state.lower()}"
            
            # Justification Lines
            just_html = "".join([f'<div class="just-line">{line}</div>' for line in justification])
            
            cards_html += f"""
            <div class="state-card {state_class}">
                <div class="state-header">
                    <div class="state-badge">{state}</div>
                    <div class="state-entity-name">{name}</div>
                    <div class="state-role">{role}</div>
                </div>
                <div class="state-justification">
                    {just_html}
                </div>
            </div>
            """
            
        return f"""
        <div class="state-panel-container">
            <h3 class="entity-section-header">
                🧭 현재 인식해야 할 결정 국면 (Decision Surface)
            </h3>
            <div class="state-grid">
                {cards_html}
            </div>
            <div class="entity-disclaimer">
                ⚠️ 이 상태는 행동 지시가 아닙니다. 구조적 상황을 인식하기 위한 판단 보조 정보입니다.
            </div>
        </div>
        """

    @staticmethod
    def render_entity_pool(entities: List[Dict[str, Any]]) -> str:
        """
        Renders the grid of Tradeable Entities (EntityMappingLayer output).
        """
        if not entities:
            return "" # Or render a placeholder if strictness allows
            
        cards_html = ""
        for e in entities:
            name = e.get("name", "Unknown")
            # Role Localization Map
            role_map = {
                "EXECUTOR": "주도자 (Executor)",
                "BENEFICIARY": "수혜자 (Beneficiary)",
                "VICTIM": "피해자 (Victim)",
                "HEDGE": "헤지 수단 (Hedge)",
                "BOTTLENECK": "병목점 (Bottleneck)",
                "STRUCTURAL EXECUTOR": "구조적 주도자"
            }
            
            raw_role = e.get("role", "STRUCTURAL EXECUTOR").replace("STRUCTURAL ", "")
            role = role_map.get(raw_role, raw_role)
            
            constraints = e.get("constraints", [])
            logic = e.get("logic_summary", "")
            
            # Badge Colors based on Role
            role_class = "role-default"
            if "BENEFICIARY" in raw_role: role_class = "role-beneficiary"
            elif "VICTIM" in raw_role: role_class = "role-victim"
            elif "HEDGE" in raw_role: role_class = "role-hedge"
            elif "BOTTLENECK" in raw_role: role_class = "role-bottleneck"
            
            # Constraint Tags
            tags_html = ""
            for t in constraints:
                tag_label = t.replace("_LOCKED", "")
                tags_html += f'<span class="constraint-tag">{tag_label}</span>'
                
            cards_html += f"""
            <div class="entity-card">
                <div class="entity-header">
                    <span class="entity-role {role_class}">{role}</span>
                    <div class="entity-name">{name}</div>
                </div>
                <div class="entity-tags">
                   {tags_html}
                </div>
                <div class="entity-logic">
                    {logic}
                </div>
            </div>
            """
            
        return f"""
        <div class="entity-pool-container">
            <h3 class="entity-section-header">
                🎯 이 이슈에서 말할 수밖에 없는 대상들 (Mapping)
            </h3>
            <div class="entity-grid">
                {cards_html}
            </div>
            <div class="entity-disclaimer">
                ⚠️ 이 엔티티는 추천이 아닙니다. 본 토픽을 설명할 때 언급되지 않을 수 없는 구조적 대상입니다. (Target Mapping by Economic Hunter)
            </div>
        </div>
        """

    @staticmethod
    def _render_empty_state() -> str:
        return """
        <div class="empty-state-card">
            <span class="empty-icon-small">☕️</span>
            <span class="empty-text">오늘은 구조적으로 확정된 이슈 시그널이 없습니다. <strong>잠재적 신호 모니터링 중... (시스템 스캐닝)</strong></span>
        </div>
        """

    @staticmethod
    def get_css() -> str:
        return """
        /* Top-1 Card Styles */
        .topic-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 30px;
        }
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
            word-break: keep-all;
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
            padding: 12px 20px;
            background: #f8fafc;
            border-radius: 8px;
            border: 1px dashed #cbd5e1;
            word-break: keep-all;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            margin-bottom: 20px;
        }
        .empty-icon-small { font-size: 18px; }
        .empty-text { font-size: 13px; color: #64748b; font-weight: 500; }
        
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
        
        /* Entity Pool */
        .entity-pool-container { margin-top: 40px; border-top: 2px dashed #e2e8f0; padding-top: 30px; }
        .entity-section-header { font-size: 16px; color: #1e293b; margin-bottom: 20px; font-weight: 800; display: flex; align-items: center; gap: 8px; }
        
        .entity-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 16px;
            margin-bottom: 20px;
        }
        
        .entity-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);
            transition: all 0.2s;
        }
        .entity-card:hover { transform: translateY(-3px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05); border-color: #cbd5e1; }
        
        .entity-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; flex-direction: column-reverse; gap: 8px; }
        
        .entity-name {
            font-size: 16px;
            font-weight: 800;
            color: #1e293b;
            letter-spacing: -0.3px;
        }
        
        .entity-role {
            font-size: 10px; font-weight: 800; padding: 3px 6px; border-radius: 4px; text-transform: uppercase;
        }
        .role-beneficiary { background: #dcfce7; color: #166534; }
        .role-victim { background: #fee2e2; color: #991b1b; }
        .role-hedge { background: #fef9c3; color: #854d0e; }
        .role-bottleneck { background: #e0f2fe; color: #075985; }
        .role-default { background: #f1f5f9; color: #475569; }
        
        .entity-tags { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 15px; }
        .constraint-tag {
            font-size: 10px; font-weight: 600; color: #64748b;
            background: #f8fafc; border: 1px solid #e2e8f0; padding: 2px 6px; border-radius: 4px;
        }
        
        .entity-logic {
            font-size: 13px;
            color: #475569;
            line-height: 1.5;
            padding-top: 12px;
            border-top: 1px solid #f1f5f9;
        }
        
        .entity-disclaimer {
            font-size: 11px;
            color: #94a3b8;
            text-align: center;
            margin-top: 20px;
            background: #f8fafc;
            padding: 10px;
            border-radius: 8px;
        }
        
        /* State Panel */
        .state-panel-container { margin-top: 30px; border-top: 2px dashed #e2e8f0; padding-top: 30px; }
        .state-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 16px;
            margin-bottom: 20px;
        }
        .state-card {
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 16px;
            background: #fff;
            border-left: 4px solid #cbd5e1; /* Default Gray */
        }
        .state-observe { border-left-color: #94a3b8; }
        .state-track { border-left-color: #3b82f6; background: #eff6ff; }
        .state-pressure { border-left-color: #f97316; background: #fff7ed; }
        .state-resolution { border-left-color: #a855f7; background: #faf5ff; }
        
        .state-header { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }
        .state-badge {
            font-size: 10px; font-weight: 800; padding: 2px 6px; border-radius: 4px; color: #fff; background: #94a3b8;
        }
        .state-observe .state-badge { background: #94a3b8; }
        .state-track .state-badge { background: #3b82f6; }
        .state-pressure .state-badge { background: #f97316; }
        .state-resolution .state-badge { background: #a855f7; }
        
        .state-entity-name { font-weight: 800; font-size: 15px; color: #1e293b; }
        .state-role { font-size: 10px; color: #64748b; margin-left: auto; text-transform: uppercase; }
        
        .state-entity-name { font-weight: 800; font-size: 15px; color: #1e293b; }
        .state-role { font-size: 10px; color: #64748b; margin-left: auto; text-transform: uppercase; }
        
        .state-justification { font-size: 12px; color: #475569; line-height: 1.5; }
        .just-line { margin-bottom: 4px; padding-left: 8px; border-left: 2px solid #e2e8f0; }
        
        /* Memory Delta Panel */
        .memory-delta-container { 
            background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; 
            padding: 16px; margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
            display: flex; align-items: center; justify-content: space-between;
        }
        .delta-status-group { display: flex; align-items: center; gap: 12px; }
        .delta-icon { font-size: 24px; }
        .delta-text { display: flex; flex-direction: column; }
        .delta-title { font-size: 14px; font-weight: 800; color: #1e293b; }
        .delta-sub { font-size: 11px; color: #64748b; }
        
        .delta-badges { display: flex; gap: 8px; }
        .delta-badge { padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; color: #fff; }
        .badge-intensified { background: #dc2626; }
        .badge-eased { background: #10b981; }
        .badge-sustained { background: #64748b; }
        .badge-new { background: #3b82f6; }
        .badge-recurring { background: #7c3aed; }
        """

    @staticmethod
    def render_memory_delta_panel(comparison: Dict[str, Any]) -> str:
        """
        Step 85: Renders the Structural Memory Delta (Comparison Result).
        """
        if not comparison:
            return "" # Or a default "No Memory" state
            
        status = comparison.get("delta_status", "NEW_TOPIC")
        intensity_delta = comparison.get("intensity_delta", "UNCHANGED")
        d1_date = comparison.get("d1_date", "Unknown")
        
        # Icon & Badge Logic
        icon = "🆕"
        status_text = "신규 구조적 토픽 발굴"
        status_sub = "최근 관측된 적 없는 새로운 구조입니다."
        badge_html = '<div class="delta-badge badge-new">신규 (NEW)</div>'
        
        if status == "RECURRING":
            icon = "🔁"
            status_text = "반복되는 구조 (재진입)" 
            status_sub = f"어제({d1_date})와 동일한 논리 구조가 재확인되었습니다."
            badge_html = '<div class="delta-badge badge-recurring">구조 반복</div>'
            
            if intensity_delta == "INTENSIFIED":
                 badge_html += '<div class="delta-badge badge-intensified">🔺 강도 심화</div>'
            elif intensity_delta == "EASED":
                 badge_html += '<div class="delta-badge badge-eased">🔻 강도 완화</div>'
            else:
                 badge_html += '<div class="delta-badge badge-sustained">⏸ 강도 유지</div>'
        
        # Entity Shifts
        shifts = comparison.get("entity_shifts", [])
        shift_html = ""
        if shifts:
            shift_list = []
            for s in shifts[:2]: # Show max 2 shifts
                if s.get("type") == "NEW_ENTITY":
                    shift_list.append(f"Adding {s['name']}")
                else:
                    shift_list.append(f"{s['name']}: {s['from']}→{s['to']}")
            if shift_list:
                shift_html = f'<div class="delta-sub" style="color:#f59e0b; margin-top:2px;">타겟 대상 변경: {", ".join(shift_list)}</div>'

        return f"""
        <div class="memory-delta-container">
            <div class="delta-status-group">
                <div class="delta-icon">{icon}</div>
                <div class="delta-text">
                    <div class="delta-title">{status_text}</div>
                    <div class="delta-sub">{status_sub}</div>
                    {shift_html}
                </div>
            </div>
            <div class="delta-badges">
                {badge_html}
            </div>
        </div>
        """


    @staticmethod
    def render_judgment_memory_view(data: Dict[str, Any]) -> str:
        """
        Step 93: Judgment Memory View.
        Summarizes multi-day continuity in short, natural sentences.
        """
        if not data:
            return ""
        stack = data.get("judgment_stack", {})
        summary = stack.get("memory_summary", [])
        if not summary or not isinstance(summary, list):
            return ""

        sentences_html = "".join([f'<div style="margin-bottom: 8px; font-size: 14.5px; color: #334155; line-height: 1.6;">🧠 {s}</div>' for s in summary])

        return f"""
        <div class="judgment-memory-container" style="margin-top: 10px; margin-bottom: 30px; padding: 20px; background: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 12px; box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);">
            <div style="font-size: 11px; font-weight: bold; color: #64748b; margin-bottom: 12px; letter-spacing: 0.1em; text-transform: uppercase;">판단 이력 (Judgment Memory)</div>
            <div class="memory-sentences">
                {sentences_html}
            </div>
            <div style="margin-top: 15px; font-size: 11px; color: #94a3b8; font-style: italic;">
                * 이 요약은 최근 7일간의 구조적 판단 누적치를 기반으로 생성되었습니다.
            </div>
        </div>
        """

# --- Task Progress Markers ---
# - [x] Update `src/dashboard/topic_exporter.py` <!-- id: 3 -->
#    - [x] Inject `decision_snapshot` into Top-1 JSON <!-- id: 4 -->
# - [x] Update `src/dashboard/topic_card_renderer.py` <!-- id: 5 -->
#    - [x] Render `Decision Snapshot` block at the top of Top-1 <!-- id: 6 -->
# - [ ] Create verification report `report_step95_decision_snapshot.md` <!-- id: 7 -->
# - [ ] Push changes to GitHub <!-- id: 8 -->
# --- End Task Progress Markers ---

    @staticmethod
    def render_decision_snapshot(data: Dict[str, Any]) -> str:
        """
        Step 95: Decision Speed Layer.
        Renders the 10-second summary block at the very top of Top-1.
        """
        snapshot = data.get("decision_snapshot", {})
        summary = snapshot.get("summary")
        if not summary:
            return ""

        why_today = snapshot.get("why_today", "")
        caution = snapshot.get("caution", "")

        return f"""
        <div class="decision-snapshot-block" style="background: #f3e8ff; border: 1px solid #d8b4fe; border-radius: 8px; padding: 12px 16px; margin-bottom: 20px;">
            <div style="display: flex; align-items: start; gap: 10px;">
                <div style="font-size: 18px;">⚡</div>
                <div style="flex: 1;">
                    <div style="font-size: 15px; font-weight: bold; color: #6b21a8; margin-bottom: 6px; line-height: 1.4;">
                        "{summary}"
                    </div>
                    <div style="font-size: 13.5px; color: #581c87; margin-bottom: 4px; line-height: 1.5;">
                        • {why_today}
                    </div>
                    <div style="font-size: 13px; color: #7e22ce; opacity: 0.8; line-height: 1.5;">
                        • {caution}
                    </div>
                </div>
            </div>
        </div>
        """

    @staticmethod
    def render_action_posture(data: Dict[str, Any]) -> str:
        """
        Step 96: Action Posture Layer.
        Renders the daily operator stance (OBSERVE, MONITOR, PREPARE, STAND_BY).
        """
        posture_data = data.get("action_posture", {})
        headline = posture_data.get("headline")
        description = posture_data.get("description", "")
        
        if not headline:
            return ""

        return f"""
        <div class="action-posture-block" style="background: #f8fafc; border-left: 4px solid #94a3b8; padding: 12px 16px; margin-bottom: 20px;">
            <div style="font-size: 14px; font-weight: bold; color: #475569; margin-bottom: 6px;">
                {headline}
            </div>
            <div style="font-size: 13.5px; color: #64748b; line-height: 1.5; margin-bottom: 8px; white-space: pre-line;">
                {description}
            </div>
            <div style="font-size: 11px; color: #cbd5e1; font-style: italic;">
                * 본 정보는 투자 조언이나 행동 지시가 아니며, 구조적 상황 인식을 돕기 위한 판단 보조 정보입니다.
            </div>
        </div>
        """
