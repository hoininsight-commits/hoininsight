
import os

path = "src/dashboard/dashboard_generator.py"
with open(path, 'r') as f:
    lines = f.readlines()

# Find the start of the HTML container construction
# We look for `html += f"""` that starts the container or nav panel logic.
# Around line 1156: `    <div class="dashboard-container">`
start_idx = -1
for i, line in enumerate(lines):
    if '<div class="dashboard-container">' in line:
        start_idx = i
        break

if start_idx == -1:
    print("Could not find start index")
    exit(1)

# We will truncate from start_idx - 1 (to includes `html += f"""` line if needed)
# But actually, looking at the file, line 1156 is inside a triple quote string started at 1102.
# Wait, no. Line 1102 starts `html = f"""`.
# Line 1156 is just part of that huge string.

# We need to find where `html = f"""` ends.
# It seems the `html` variable initialization goes on for a long time.
# Let's find where the initial `html` string definitions end and procedural additions begin.

# Line 1102: `    html = f"""`
# ...
# Line 1203: `        </div>` (Nav Panel ends)
# ...
# It seems the entire HTML structure is built in one go until line 1373 `decision_card_html = ...`
# The code is mixed.

# Let's look for a safe anchor point BEFORE the HTML construction becomes messy.
# Line 1100: `    sidebar_html += applied_html`
# This is a good place. All data is ready.

anchor_idx = -1
for i, line in enumerate(lines):
    if "sidebar_html += applied_html" in line:
        anchor_idx = i
        break

if anchor_idx == -1:
    print("Could not find anchor index")
    exit(1)

# Keep lines up to anchor_idx + 1
header_lines = lines[:anchor_idx+1]

# Now we append the NEW logic for HTML construction.
# This logic will reconstruct the dashboards using the variables prepared above.

new_logic = r'''
    
    # [Layout Fix] Re-assembling the HTML with proper Tab Structure
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
                <div style="font-size: 13px; font-weight: 800; color: #f8fafc; padding: 20px 25px; border-bottom: 1px solid #1e293b; margin-bottom: 10px;">
                    HOIN INSIGHT v1.0
                </div>
                
                <div class="nav-label">MAIN VIEW</div>
                <div class="nav-item active" onclick="activate('architecture-diagram')"><span class="nav-icon">🟦</span> 아키텍처</div>
                
                <div class="nav-label">OPERATIONS</div>
                <div class="nav-item" onclick="activate('ops-scoreboard')"><span class="nav-icon">📈</span> 운영 지표</div>
                <div class="nav-item" onclick="activate('change-effectiveness')"><span class="nav-icon">📊</span> 변경 효과</div>

                <div class="nav-label">WORKFLOW</div>
                <div class="nav-item" onclick="activate('youtube-inbox')"><span class="nav-icon">📺</span> 유튜브 인박스</div>
                <div class="nav-item" onclick="activate('narrative-queue')"><span class="nav-icon">📝</span> 내러티브 큐</div>
                <div class="nav-item" onclick="activate('revival-engine')"><span class="nav-icon">♻️</span> 부활 엔진</div>
                
                <div class="nav-label">ARCHIVE / LOGS</div>
                <div class="nav-item" onclick="activate('rejection-ledger')"><span class="nav-icon">🚫</span> 거절/보류 리스트</div>
                <div class="nav-item" onclick="activate('topic-candidates')"><span class="nav-icon">📂</span> 토픽 후보군</div>
                
                <div class="nav-label">OUTPUT</div>
                <div class="nav-item" onclick="activate('final-decision')"><span class="nav-icon">⚖️</span> 최종 의사결정</div>
                <div class="nav-item" onclick="activate('insight-script')"><span class="nav-icon">📜</span> 인사이트 스크립트</div>
            </div>

            <!-- CENTER: Main Process Flow (Tabs) -->
            <div class="main-panel">
                <div class="sections-wrapper">
                    
                    <!-- TAB 1: Architecture Diagram -->
                    <div id="architecture-diagram" class="tab-content active" style="display:block;">
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

    # [Change Effectiveness Tab]
    html += f"""
                    <div id="change-effectiveness" class="tab-content" style="display:none;">
                        <h2 style="font-size: 20px; font-weight: 700; color: #1e293b; margin-bottom: 25px;">📊 변경 효과 분석</h2>
                        {effectiveness_html}
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

    # [Narrative Queue Tab]
    html += f"""
                    <div id="narrative-queue" class="tab-content" style="display:none;">
                        <h2 style="font-size: 20px; font-weight: 700; color: #1e293b; margin-bottom: 25px;">📝 내러티브 큐</h2>
                        {queue_html}
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
                    </div>
                    
                </div> <!-- End sections wrapper -->
            </div> <!-- End Main Panel -->
            
            <!-- RIGHT SIDEBAR (Correct Placement) -->
            <div class="sidebar">
                <div class="sidebar-title">
                    데이터 수집 현황판
                </div>
                {sidebar_html}
                <div class="footer">
                    Hoin Engine 자동 생성<br>{ymd}
                </div>
            </div>
            
        </div> <!-- End Dashboard Container -->
        
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
            function closeModal() {{
                document.getElementById('scriptModal').classList.remove('modal-active');
            }}
            function copyScript() {{
                const text = document.querySelector('#insight-script pre') ? document.querySelector('#insight-script pre').innerText : document.querySelector('#insight-script div').innerText;
                navigator.clipboard.writeText(text).then(() => alert('Copied!'));
            }}
        </script>
    </body>
    </html>
    """
    
    return html

if __name__ == "__main__":
    import os
    import sys
    from pathlib import Path
    
    # Pass current directory as base_dir
    base_dir = Path(os.getcwd())
    sys.path.append(str(base_dir))
    
    os.makedirs("data/dashboard", exist_ok=True)
    os.makedirs("dashboard", exist_ok=True)
    
    html = generate_dashboard(base_dir)
    
    with open("dashboard/index.html", "w") as f:
        f.write(html)
    
    print("[Dashboard] Generated dashboard/index.html")
'''

# Combine
final_content = "".join(header_lines) + new_logic

with open(path, 'w') as f:
    f.write(final_content)

print("[FixLayout] Successfully rewrote dashboard_generator.py layout block.")
