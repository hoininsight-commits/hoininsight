from .models import DashboardSummary, DecisionCard, RejectLog, HoinEvidenceItem, UnifiedLinkRow
from typing import List

class DashboardRenderer:
    """
    (IS-27) Renders a static HTML page for IssueSignal Dashboard.
    """
    def render(self, summary: DashboardSummary) -> str:
        # [IS-51] Stamps
        import subprocess
        from datetime import datetime, timedelta, timezone
        
        def get_git_hash():
            try:
                return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()
            except:
                return "unknown"
        
        commit_hash = get_git_hash()
        engine_version = "v2.5.1"
        
        # Calculate KST Time for Pipeline Run
        utc_now = datetime.now(timezone.utc)
        kst_now_dt = utc_now + timedelta(hours=9)
        pipeline_time_kst = kst_now_dt.strftime("%Y-%m-%d %H:%M:%S")

        html = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IssueSignal Unified Ops Center</title>
    <style>
        :root {{
            --bg: #f1f5f9;
            --header-bg: #ffffff;
            --card-bg: #ffffff;
            --text-main: #0f172a;
            --text-sub: #475569;
            --emerald: #059669;
            --blue: #2563eb;
            --purple: #7c3aed;
            --red: #dc2626;
            --border: #e2e8f0;
            --amber: #d97706;
            --amber-light: #fffbeb;
            --amber-border: #fcd34d;
        }}
        body {{ font-family: 'Pretendard', system-ui, sans-serif; background: var(--bg); color: var(--text-main); margin: 0; padding: 0; }}
        
        /* Premium Light Header */
        .top-header {{ 
            background: var(--header-bg); 
            padding: 0 40px; 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            color: var(--text-main); 
            height: 70px; 
            box-shadow: 0 1px 3px rgba(0,0,0,0.1); 
            z-index: 100;
            border-bottom: 1px solid var(--border);
        }}
        .header-brand {{ font-size: 20px; font-weight: 900; display:flex; align-items:center; gap:12px; color: #1e293b; }}
        .header-meta {{ font-size: 11px; color: var(--text-sub); font-family: monospace; text-align: right; display: flex; gap: 15px; letter-spacing: 0.05em; }}
        
        /* Navigation Tabs */
        .nav-tabs {{ 
            background: white; 
            border-bottom: 1px solid var(--border); 
            display: flex; 
            gap: 10px; 
            padding: 0 40px; 
            position: sticky; 
            top: 0; 
            z-index: 99; 
            height: 54px; 
            align-items: end;
        }}
        .tab-btn {{ 
            padding: 16px 24px; 
            border: none; 
            background: none; 
            font-weight: 700; 
            font-size: 14px; 
            cursor: pointer; 
            color: var(--text-sub); 
            border-bottom: 3px solid transparent; 
            transition: 0.2s; 
        }}
        .tab-btn:hover {{ color: var(--text-main); background: #f8fafc; }}
        .tab-btn.active {{ color: var(--blue); border-bottom-color: var(--blue); }}
        
        .container {{ padding: 50px 40px; max-width: 1100px; margin: 0 auto; display: none; }}
        .container.active {{ display: block; }}
        
        .section-title {{ font-size: 20px; font-weight: 900; color: #1e293b; margin: 60px 0 30px 0; display: flex; align-items: center; gap: 12px; }}
        .section-title::before {{ content: ''; display: inline-block; width: 5px; height: 20px; background: var(--blue); border-radius: 3px; }}
        
        /* High-Visibility Card Styles */
        .topic-card-top1 {{
            background: #ffffff;
            border: 1px solid var(--border);
            border-top: 8px solid var(--blue);
            border-radius: 16px; padding: 40px; 
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 10px 10px -5px rgba(0, 0, 0, 0.02); 
            margin-bottom: 50px;
        }}
        .topic-header-label {{ font-size: 12px; font-weight: 800; color: var(--text-sub); text-transform: uppercase; margin-bottom: 15px; display:flex; align-items:center; gap:10px; }}
        .topic-title {{ font-size: 34px; font-weight: 900; color: #0f172a; margin: 15px 0 25px 0; line-height: 1.3; letter-spacing: -0.02em; }}
        
        .auth-sentence {{ background:#eff6ff; border-left:5px solid var(--blue); padding:20px 30px; color:#1e40af; font-weight:800; font-size:18px; line-height:1.6; border-radius: 0 12px 12px 0; margin-bottom: 30px; }}
        
        .one-liner {{ font-size: 17px; line-height: 1.8; font-weight: 600; color: #334155; margin-bottom: 30px; }}
        
        /* Content Package Block */
        .content-package {{ background: #ffffff; border: 2px solid #e2e8f0; border-radius: 14px; overflow: hidden; margin-top: 40px; }}
        .cp-header {{ background: #f8fafc; padding: 18px 25px; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; font-weight: 900; color: #1e293b; }}
        
        /* Copy Button - High Visibility */
        .copy-btn {{ 
            background: white; border: 1px solid #cbd5e1; padding: 8px 16px; border-radius: 8px; 
            cursor: pointer; font-weight: 700; font-size: 13px; color: #334155; 
            transition: all 0.2s; display: flex; align-items: center; justify-content: center; gap: 8px;
        }}
        .copy-btn:hover {{ border-color: #94a3b8; background: #f1f5f9; }}
        .copy-btn-primary {{ background: #2563eb; border-color: #2563eb; color: white; }}
        .copy-btn-primary:hover {{ background: #1d4ed8; border-color: #1d4ed8; }}

        /* Meta Pills */
        .meta-pill {{ background: #f1f5f9; color: #475569; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; }}
        .meta-pill.purple {{ background: #f3e8ff; color: #6b21a8; }}

        /* Unified Table Styles - Light Theme */
        .unified-table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 16px; overflow: hidden; border: 1px solid var(--border); box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }}
        .unified-table th {{ background: #f8fafc; padding: 18px 20px; text-align: left; font-size: 12px; font-weight: 900; color: #475569; text-transform: uppercase; border-bottom: 1px solid var(--border); letter-spacing: 0.05em; }}
        .unified-table td {{ padding: 20px; border-bottom: 1px solid var(--border); font-size: 14px; color: #1e293b; }}
        
        .badge-status {{ padding: 4px 10px; border-radius: 6px; font-weight: 800; font-size: 12px; display: inline-block; }}
        .status-matched {{ background: #dcfce7; color: #166534; }}
        .status-no-ev {{ background: #f1f5f9; color: #475569; }}
        
        /* Drawer */
        .evidence-drawer {{ background: #f8fafc; padding: 30px; border-top: 1px solid #e2e8f0; display: none; }}
        .evidence-item {{ background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; margin-bottom: 15px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
        
        .expand-btn {{ background: transparent; color: var(--blue); border: none; font-weight: 700; cursor: pointer; font-size: 13px; display: flex; align-items: center; gap: 6px; }}
        .expand-btn:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="top-header">
        <div class="header-brand">
            <span style="background:rgba(255,255,255,0.1); padding:4px 8px; border-radius:6px; font-size:16px;">🛰️</span> 
            HOIN Unified Ops Center
        </div>
        <div>
            <div class="header-meta">
                <span>DATA: {summary.date}</span>
                <span>RUN: {pipeline_time_kst}</span>
            </div>
            <div class="header-meta" style="margin-top:2px;">
                <span>커밋: {commit_hash}</span>
                <span>엔진: {engine_version}</span>
            </div>
        </div>
    </div>

    <div class="nav-tabs">
        <button class="tab-btn active" onclick="switchTab('issuesignal', this)">이슈시그널 운영센터</button>
        <button class="tab-btn" onclick="switchTab('hoinevidence', this)">호인 분석 데이터</button>
        <button class="tab-btn" onclick="switchTab('linkview', this)">통합 근거 연결뷰</button>
    </div>

    <!-- Tab 1: IssueSignal -->
    <div id="issuesignal" class="container active">
        
        <div class="summary-grid" style="display:grid; grid-template-columns:repeat(auto-fit, minmax(180px,1fr)); gap:15px; margin-bottom:40px;">
            {self._render_counters(summary.counts)}
        </div>

        <div class="section-title">✨ 오늘의 최종 가공 인텔리전스</div>
        {self._render_top_cards(summary.top_cards)}

        <div class="section-title">🔭 사전 트리거 감시망 (관찰 중)</div>
        {self._render_watchlist(summary.watchlist)}

        <div class="section-title">🚫 품질 하한선 미달 및 반려 기록</div>
        <div style="background:white; padding:20px; border:1px solid #e2e8f0; border-radius:8px;">
            {self._render_reject_logs(summary.reject_logs)}
        </div>
    </div>

    <!-- Tab 2: Hoin Evidence -->
    <div id="hoinevidence" class="container">
        <div class="section-title">🧬 호인 아티팩트 (최신 분석 데이터)</div>
        <div style="display:grid; gap:20px;">
            {self._render_hoin_evidence(summary.hoin_evidence)}
        </div>
        {f"<div class='empty-state' style='padding:40px; text-align:center; color:var(--text-sub);'>{summary.date}에 감지된 호인 아티팩트가 없습니다.</div>" if not summary.hoin_evidence else ""}
    </div>

    <!-- Tab 3: Link View -->
    <div id="linkview" class="container">
        <div class="filter-bar" style="margin-bottom:20px; display:flex; gap:15px; align-items:center; font-size:13px; color:#475569;">
            <b>상태 필터:</b>
            <select id="statusFilter" onchange="filterLinkView()" style="padding:4px 8px; border:1px solid #cbd5e1; border-radius:4px;">
                <option value="ALL">전체 상태</option>
                <option value="TRUST_LOCKED">발화 확정</option>
                <option value="HOLD">보류</option>
                <option value="REJECT">반려</option>
            </select>
            <label style="display:flex; align-items:center; gap:5px;"><input type="checkbox" id="evOnly" onchange="filterLinkView()"> 증거 연결됨</label>
            <label style="display:flex; align-items:center; gap:5px;"><input type="checkbox" id="proofOnly" onchange="filterLinkView()"> 실체 검증됨</label>
        </div>
        {self._render_link_view(summary.link_view)}
    </div>

    <script>
        function switchTab(tabId, btn) {{
            // Hide all tabs
            document.querySelectorAll('.container').forEach(c => c.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            // Show new tab
            document.getElementById(tabId).classList.add('active');
            btn.classList.add('active');
        }}

        function toggleElement(id) {{
            const el = document.getElementById(id);
            const isHidden = el.style.display === 'none';
            el.style.display = isHidden ? 'block' : 'none';
            
            // Toggle arrow if exists
            const arrow = document.getElementById(id + '-arrow');
            if (arrow) {{
                arrow.innerText = isHidden ? '▴' : '▾';
            }}
        }}

        function toggleRow(id) {{
            const row = document.getElementById('drawer-' + id);
            // Check computed style
            if(row.style.display === 'table-row') {{
                row.style.display = 'none';
            }} else {{
                row.style.display = 'table-row';
            }}
        }}

        function filterLinkView() {{
            const status = document.getElementById('statusFilter').value;
            const evOnly = document.getElementById('evOnly').checked;
            const proofOnly = document.getElementById('proofOnly').checked;
            const rows = document.querySelectorAll('.link-row');
            
            rows.forEach(row => {{
                const rStatus = row.getAttribute('data-status');
                const hasEv = row.getAttribute('data-has-ev') === 'true';
                const hasProof = row.getAttribute('data-has-proof') === 'true';
                let visible = true;
                
                if (status !== 'ALL' && rStatus !== status) visible = false;
                if (evOnly && !hasEv) visible = false;
                if (proofOnly && !hasProof) visible = false;
                
                row.style.display = visible ? 'table-row' : 'none';
                if (!visible) {{
                    const id = row.id.split('-')[1];
                    const drawer = document.getElementById('drawer-' + id);
                    if(drawer) drawer.style.display = 'none';
                }}
            }});
        }}

        function copyToClipboard(text) {{
            if(!text || text === '-' || text === 'undefined') return;
            navigator.clipboard.writeText(text).then(() => {{
                alert('콘텐츠가 클립보드에 복사되었습니다.');
            }}).catch(err => {{
                console.error('Copy failed: ', err);
            }});
        }}
    </script>
</body>
</html>
        """
        return html

    def _render_counters(self, counts: dict) -> str:
        items = []
        status_map = {
            "TRUST_LOCKED": "확정",
            "EDITORIAL_CANDIDATE": "후보",
            "REJECT": "반려",
            "PRE_TRIGGER": "감시",
            "HOLD": "보류",
            "SILENT_DROP": "침묵",
            "EDITORIAL_LIGHT": "구조 해설"
        }
        colors = {
            "TRUST_LOCKED": "#10B981",
            "REJECT": "#EF4444",
            "PRE_TRIGGER": "#3B82F6",
            "HOLD": "#F59E0B",
            "SILENT_DROP": "#94A3B8"
        }
        for status, count in counts.items():
            if status not in status_map: continue
            color = colors.get(status, "#6B7280")
            items.append(f"""
            <div style="background:white; border-left:4px solid {color}; border-radius:8px; padding:15px; border:1px solid #e2e8f0; border-left-width:4px; box-shadow:0 1px 2px rgba(0,0,0,0.05);">
                <div style="font-size: 11px; font-weight:700; color: #64748b;">{status_map[status]}</div>
                <div style="font-size: 24px; font-weight: 800; margin-top: 5px; color: #0f172a;">{count}</div>
            </div>
            """)
        return "\n".join(items)

    def _render_top_cards(self, cards: List[DecisionCard]) -> str:
        # [IS-67-UX] Operator Decision Mode: Single Top Priority Card
        if not cards:
            return """
            <div style="background:#fff1f2; border:1px solid #fecdd3; padding:40px; border-radius:12px; margin-bottom:40px; text-align:center;">
                <div style="font-size:3em; margin-bottom:15px;">❌</div>
                <div style="font-weight:800; color:#e11d48; font-size:1.5em; margin-bottom:10px;">오늘 발화할 토픽 없음</div>
                <div style="font-size:1.1em; color:#be123c;">사유: 운영 품질 하한선(WHY-NOW/신호 강도) 미달</div>
            </div>
            """
            
        # We only focus on Rank 0 for the Top Priority Card
        c = cards[0]
        
        # [IS-70] Low-Intensity Editorial Layer
        if c.status == "EDITORIAL_LIGHT":
            return self._render_light_card(c)

        # [IS-67-UX] Handle SILENT/HOLD status as "No Topic"
        if c.status in ["SILENT", "HOLD"] and not c.blocks.get('content_package', {}).get('long_form'):
            return f"""
            <div style="background:#fff1f2; border:1px solid #fecdd3; padding:40px; border-radius:12px; margin-bottom:40px; text-align:center;">
                <div style="font-size:3em; margin-bottom:15px;">❌</div>
                <div style="font-weight:800; color:#e11d48; font-size:1.5em; margin-bottom:10px;">{c.title}</div>
                <div style="font-size:1.1em; color:#be123c;">오늘의 발화 상태: 보류</div>
                <div style="font-size:0.9em; color:#be123c; margin-top:5px;">{c.decision_rationale}</div>
            </div>
            """

        cp = c.blocks.get('content_package', {})
        long_form = cp.get('long_form', '-')
        text_card = cp.get('text_card', '-')
        
        # Risk factors summary
        risk_text = c.risk_factors[0] if c.risk_factors else "시장 변동성 확인 필요"

        # Evidence Summary for Collapse
        evidence_summary = []
        if c.trigger_quote: evidence_summary.append("인용구(Quote)")
        if c.blocks.get('flow_evidence'): evidence_summary.append("수급 데이터(Flow)")
        if c.blocks.get('corporate_facts'): evidence_summary.append("기업 공시(Corp)")
        ev_summary_label = " + ".join(evidence_summary) if evidence_summary else "데이터 분석 결과"

        return f"""
        <div class="topic-card-top1" style="border-top: 8px solid var(--blue);">
            <!-- Header Group -->
            <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:20px;">
                <div>
                    <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px;">
                        <span style="background:var(--blue); color:white; padding:4px 12px; border-radius:4px; font-size:12px; font-weight:800;">📌 오늘의 1순위 발화</span>
                        <span style="font-size:12px; color:var(--text-sub); font-weight:600;">추천 형식: 롱폼 / 숏츠 / 텍스트</span>
                    </div>
                    <h1 style="font-size:32px; font-weight:900; color:#0f172a; margin:0; line-height:1.2;">{c.title}</h1>
                </div>
                <div style="text-align:right;">
                    <div style="background:#f1f5f9; padding:8px 12px; border-radius:8px; margin-bottom:10px;">
                        <div style="font-size: 11px; font-weight: 700; color: #64748b; margin-bottom: 4px;">주인공 ({c.actor_type})</div>
                        <div style="font-size: 14px; font-weight: 800; color: #1e293b;">{c.actor} <span style="font-size:11px; color:var(--blue); font-weight:700;">#{c.actor_tag}</span></div>
                    </div>
                    {self._render_decision_tree(c)}
                </div>
            </div>

            {self._render_structural_continuity(c)}

            <!-- WHY-NOW Banner -->
            <div style="background:linear-gradient(to right, #eff6ff, #ffffff); border-left:5px solid var(--blue); padding:18px 25px; border-radius:0 12px 12px 0; margin-bottom:25px;">
                <div style="font-size:12px; font-weight:800; color:var(--blue); margin-bottom:6px; text-transform:uppercase;">💡 지금 말해야 하는 이유 (WHY-NOW)</div>
                <div style="font-size:18px; font-weight:700; color:#1e3a8a; line-height:1.5;">"{c.authority_sentence}"</div>
            </div>

            <!-- Ticker Path & Bottleneck (IS-69) -->
            <div style="margin-bottom:25px; background:#ffffff; border:1px solid #e2e8f0; padding:20px; border-radius:12px;">
                <div style="font-size:15px; font-weight:800; color:#1e293b; margin-bottom:15px; line-height:1.4; display:flex; align-items:center; gap:8px;">
                    <span style="font-size:18px;">🔗</span> 
                    <span>병목 연결: {c.bottleneck_link}</span>
                </div>
                {self._render_ticker_path_results(c)}
            </div>

            <!-- Risk Factor -->
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:30px; padding:10px 15px; background:#fff7ed; border-radius:8px; border:1px solid #ffedd5;">
                <span style="font-size:14px;">⚠️</span>
                <span style="font-size:13px; font-weight:600; color:#9a3412;">리스크: {risk_text}</span>
            </div>

            <!-- Unified Content Package (Immediate Script Exposure) -->
            <div style="background:#ffffff; border:2px solid #e2e8f0; border-radius:12px; overflow:hidden;">
                <div style="background:#f8fafc; padding:15px 20px; border-bottom:1px solid #e2e8f0; display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:14px; font-weight:800; color:#1e293b;">📋 제작 스크립트 (즉시 사용 가능)</span>
                    <button class="copy-btn copy-btn-primary" onclick="copyToClipboard(document.getElementById('main-script').innerText)">전체 복사</button>
                </div>
                <div id="main-script" style="padding:25px; font-size:15px; line-height:1.8; color:#334155; white-space:pre-wrap; background:#ffffff;">{long_form}</div>
                
                <!-- Foldable Sub-Contents -->
                <div style="border-top:1px solid #e2e8f0; background:#f1f5f9; padding:10px 20px;">
                    <button onclick="toggleElement('sub-contents')" style="background:none; border:none; color:#475569; font-size:12px; font-weight:700; cursor:pointer; display:flex; align-items:center; gap:5px;">
                        기타 형식 (숏츠/텍스트) 보기 <span id="sub-arrow">▾</span>
                    </button>
                    <div id="sub-contents" style="display:none; padding-top:15px; padding-bottom:10px;">
                        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:15px; margin-bottom:15px;">
                            <div style="background:white; padding:15px; border-radius:8px; border:1px solid #e2e8f0;">
                                <div style="font-size:11px; font-weight:800; color:#e11d48; margin-bottom:10px;">🎬 숏츠 패키지</div>
                                <div style="font-size:12px; color:#475569; margin-bottom:5px;">15s: {cp.get('shorts_15s', '-')}</div>
                                <div style="font-size:12px; color:#475569; margin-bottom:5px;">30s: {cp.get('shorts_30s', '-')}</div>
                                <div style="font-size:12px; color:#475569;">45s: {cp.get('shorts_45s', '-')}</div>
                            </div>
                            <div style="background:white; padding:15px; border-radius:8px; border:1px solid #e2e8f0;">
                                <div style="font-size:11px; font-weight:800; color:#475569; margin-bottom:10px;">📌 텍스트 카드</div>
                                <div style="font-size:12px; color:#334155; white-space:pre-wrap;">{text_card}</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Evidence Collapse -->
            <div style="margin-top:25px; border:1px solid #e2e8f0; border-radius:8px; overflow:hidden;">
                <button onclick="toggleElement('evidence-block')" style="width:100%; text-align:left; background:#f8fafc; border:none; padding:12px 20px; font-size:13px; font-weight:700; color:var(--blue); cursor:pointer; display:flex; justify-content:space-between; align-items:center;">
                    <span>판단 근거 보기 ({ev_summary_label}) ▸</span>
                    <span style="font-size:11px; color:#94a3b8; font-weight:400;">데이터 검증 완료</span>
                </button>
                <div id="evidence-block" style="display:none; padding:20px; background:#ffffff; border-top:1px solid #e2e8f0;">
                    <div style="font-size:13px; line-height:1.7; color:#475569;">
                        {self._render_evidence_summary(c)}
                    </div>
                </div>
            </div>

            <div style="font-size: 11px; margin-top: 20px; color: #94a3b8; text-align:right;">
                데이터 보증 식별자: {c.signature or '-'} | 분석 모델: {c.card_version}
            </div>
        </div>
        """

    def _render_watchlist(self, cards: List[DecisionCard]) -> str:
        if not cards: return "<div style='color:var(--text-sub)'>관심 목록이 비어있습니다.</div>"
        rows = []
        for c in cards:
            rows.append(f"""
            <tr>
                <td><b>{c.title}</b></td>
                <td>{c.actor}</td>
                <td>{c.trigger_type}</td>
                <td style="color: var(--blue)">사전 트리거 감지</td>
            </tr>
            """)
        return f"""
        <table class="watchlist-table">
            <thead>
                <tr>
                    <th>항목 제목</th>
                    <th>주체</th>
                    <th>트리거 종류</th>
                    <th>현재 상태</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
        """

    def _render_reject_logs(self, logs: List[RejectLog]) -> str:
        if not logs: return "최근 기록된 개선/반려 내역이 없습니다."
        items = []
        for l in logs:
            items.append(f"""
            <div class="reject-item" style="padding:8px 0; border-bottom:1px solid #F3F4F6;">
                <span style="color:#9CA3AF; font-size:0.8em;">[{l.timestamp}]</span> 
                <span class="badge-status status-no-ev" style="margin:0 8px;">{l.reason_code}</span>
                <b style="color:#374151;">{l.topic_id}</b>: <span style="color:#4B5563;">{l.fact_text}</span>
            </div>
            """)
        return "\n".join(items)

    def _render_no_topic_alert(self, summary: DashboardSummary) -> str:
        if summary.counts.get("TRUST_LOCKED", 0) > 0:
            return ""
        
        top_reasons = []
        for log in summary.reject_logs:
            if log.reason_code not in top_reasons:
                top_reasons.append(log.reason_code)
        
        reasons_html = ", ".join([f"<b>{r}</b>" for r in top_reasons[:3]])
        return f"""
        <div style="background:#FFFBEB; border:1px solid #F59E0B; padding:20px; border-radius:12px; margin-bottom:30px; display:flex; gap:20px; align-items:center;">
            <div style="font-size:2em;">⚠️</div>
            <div>
                <div style="font-weight:bold; color:#92400E; font-size:1.1em; margin-bottom:5px;">오늘 확정된 발화 토픽이 없습니다.</div>
                <div style="font-size:0.9em; color:#B45309;">주요 보류 사유: {reasons_html if top_reasons else "데이터 신뢰도 검증 중"}</div>
            </div>
        </div>
        """

    def _render_hoin_evidence(self, items: List[HoinEvidenceItem]) -> str:
        res = []
        for i in items:
            bullets = "".join([f"<li>{b}</li>" for b in i.bullets])
            res.append(f"""
            <div class="card-base hoin-card">
                <div style="font-size: 0.75em; color: var(--purple); font-weight: bold; margin-bottom:5px;">[호인 아티팩트]</div>
                <div style="font-weight: bold; font-size: 1.1em; margin-bottom:8px;">{i.title}</div>
                <div style="font-size: 0.9em; color: var(--text-sub); margin-bottom:12px;">{i.summary}</div>
                <ul style="font-size:0.85em; padding-left:18px; margin-bottom:12px; color:#374151;">
                    {bullets}
                </ul>
                <div style="font-size: 0.75em; color: var(--text-sub); border-top: 1px solid var(--border); padding-top:8px;">
                    출처 파일: <code>{i.source_file}</code>
                </div>
            </div>
            """)
        return "\n".join(res)

    def _render_link_view(self, rows: List[UnifiedLinkRow]) -> str:
        html_rows = []
        for idx, r in enumerate(rows):
            c = r.issue_card
            status_class = "status-matched" if r.link_status == "MATCHED" else "status-no-ev"
            has_ev = 'true' if r.linked_evidence else 'false'
            has_proof = 'true' if any(p.proof_status == "PROOF_OK" for p in c.proof_packs) else 'false'
            
            status_map = {
                "TRUST_LOCKED": "확정",
                "EDITORIAL_CANDIDATE": "후보",
                "REJECT": "반려",
                "PRE_TRIGGER": "감시",
                "HOLD": "보류",
                "SILENT": "침묵",
                "EDITORIAL_LIGHT": "구조 해설"
            }
            ko_status = status_map.get(c.status, c.status)
            
            html_rows.append(f"""
            <tr class="link-row" id="row-{idx}" data-status="{c.status}" data-has-ev="{has_ev}" data-has-proof="{has_proof}">
                <td><span class="badge-status {status_class}">{r.link_status}</span></td>
                <td><b>{c.title}</b><br><small>{c.topic_id}</small></td>
                <td>{ko_status}</td>
                <td>{", ".join([t.get('symbol', '') for t in c.tickers])}</td>
                <td>
                    <button class="expand-btn" onclick="toggleRow('{idx}')">
                        {len(r.linked_evidence)}개 근거 항목 ▾
                    </button>
                </td>
            </tr>
            <tr class="expanded-row" id="drawer-{idx}">
                <td colspan="5">
                    <div class="evidence-drawer">
                        {self._render_drawer_content(r)}
                    </div>
                </td>
            </tr>
            """)
        
        return f"""
        <table class="unified-table">
            <thead>
                <tr>
                    <th width="120">연결 상태</th>
                    <th>이슈 제목</th>
                    <th width="120">현재 상태</th>
                    <th width="150">관련 종목</th>
                    <th width="120">호인 근거 데이터</th>
                </tr>
            </thead>
            <tbody>
                {''.join(html_rows)}
            </tbody>
        </table>
        """

    def _render_drawer_content(self, row: UnifiedLinkRow) -> str:
        items = []
        c = row.issue_card
        
        # 0. Source Clusters Summary (IS-32)
        if c.source_clusters:
            items.append(f"<div style='margin-bottom:15px; font-weight:bold; color:var(--emerald); border-bottom:1px solid var(--border); padding-bottom:5px;'>🌐 정보 출처 다양성 검증</div>")
            cluster_badges = []
            for sc in c.source_clusters:
                color = "#059669" if sc.cluster_type == "OFFICIAL" else "#2563EB"
                bg = "#ECFDF5" if sc.cluster_type == "OFFICIAL" else "#EFF6FF"
                cluster_badges.append(f"""
                <div style="display:inline-block; background:{bg}; color:{color}; border:1px solid {color}33; padding:2px 8px; border-radius:15px; font-size:0.75em; margin-right:5px; margin-bottom:5px;">
                    <b>{sc.cluster_id}</b>: {sc.origin_name}
                </div>
                """)
            items.append(f"<div style='margin-bottom:15px;'>{''.join(cluster_badges)}</div>")

        # 1. Trigger Quote Section (IS-31)
        items.append(f"<div style='margin-bottom:15px; font-weight:bold; color:var(--blue); border-bottom:1px solid var(--border); padding-bottom:5px;'>🗣️ 직접 발언 인용구 검증</div>")
        if not c.trigger_quote:
            items.append(f"<div style='color:var(--text-sub); margin-bottom:20px;'>검증된 인용구 증거가 없습니다.</div>")
        else:
            q = c.trigger_quote
            q_status_class = "status-matched" if q.verification_status == "PASS" else "status-no-ev"
            items.append(f"""
            <div class="evidence-item" style="border-left: 4px solid var(--blue); background:#EFF6FF; margin-bottom:20px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <span style="background:#DBEAFE; color:#1E40AF; padding:2px 6px; border-radius:4px; font-size:0.75em; font-weight:bold;">{q.fact_type}</span>
                    <span class="badge-status {q_status_class}">{ "검증 성공" if q.verification_status == "PASS" else "검증 보류" }: {q.reason_code}</span>
                </div>
                <div style="font-size:1.1em; font-weight:bold; line-height:1.4; color:#1E3A8A; margin:10px 0;">"{q.excerpt}"</div>
                <div style="font-size:0.75em; color:var(--text-sub);">
                    출처: <b>{q.source_kind}</b> ({q.source_date}) | <a href="{q.source_ref}" target="_blank" style="color:var(--blue); text-decoration:none;">원문 보기</a>
                </div>
            </div>
            """)

        # 1. Hoin Evidence Section
        items.append(f"<div style='margin-bottom:15px; font-weight:bold; color:var(--purple); border-bottom:1px solid var(--border); padding-bottom:5px;'>🧬 호인 근거 데이터</div>")
        if not row.linked_evidence:
            items.append(f"<div style='color:var(--text-sub); margin-bottom:20px;'>이 카드에 매칭된 호인 증거가 없습니다.</div>")
        else:
            items.append(f"<div style='margin-bottom:15px; font-weight:bold; color:var(--emerald); font-size:0.85em;'>매칭 근거: {row.match_reason}</div>")
            for ev in row.linked_evidence:
                bullets = "".join([f"<li>{b}</li>" for b in ev.bullets])
                items.append(f"""
                <div class="evidence-item" style="margin-bottom:10px;">
                    <div style="font-weight:bold; font-size:0.95em;">{ev.title}</div>
                    <div style="font-size:0.85em; color:var(--text-sub); margin:5px 0;">{ev.summary}</div>
                    <ul style="font-size:0.8em; margin:8px 0; padding-left:20px;">{bullets}</ul>
                    <div style="font-size:0.7em; color:var(--blue);">분석 파일: {ev.source_file}</div>
                </div>
                """)

        # 2. Proof Pack Section (IS-30)
        items.append(f"<div style='margin-top:20px; margin-bottom:15px; font-weight:bold; color:var(--amber); border-bottom:1px solid var(--border); padding-bottom:5px;'>🛡️ 종목별 실체 검증 팩 (Proof Packs)</div>")
        if not c.proof_packs:
            items.append(f"<div style='color:var(--text-sub)'>생성된 증거 팩트가 없습니다.</div>")
        else:
            for p in c.proof_packs:
                f_items = []
                for f in p.hard_facts:
                    f_items.append(f"""
                    <li style="margin-bottom:8px;">
                        <span style="background:#FEF3C7; color:#92400E; padding:1px 5px; border-radius:3px; font-size:0.75em; font-weight:bold;">{f.fact_type}</span>
                        <span style="font-size:0.85em;">{f.fact_claim}</span>
                        <div style="font-size:0.7em; color:var(--text-sub); margin-top:2px;">
                            출처: <b>{f.source_kind}</b> ({f.source_date}) | 참조: <code>{f.source_ref}</code>
                        </div>
                    </li>
                    """)
                
                p_status_class = "status-matched" if p.proof_status == "PROOF_OK" else "status-no-ev"
                items.append(f"""
                <div class="evidence-item" style="border-left: 4px solid var(--amber); background:#FFFBEB;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <div style="font-weight:bold; font-size:1em;">{p.ticker}: {p.company_name}</div>
                        <span class="badge-status {p_status_class}">{ "검증 성공" if p.proof_status == "PROOF_OK" else "검증 실패" }</span>
                    </div>
                    <div style="font-size:0.85em; color:#4B5563; margin-bottom:10px; font-style:italic;">"{p.why_irreplaceable_now}"</div>
                    <ul style="margin:0; padding-left:15px; color:#374151;">{''.join(f_items)}</ul>
                </div>
                """)
        
        return "".join(items)

    def _render_evidence_summary(self, c: DecisionCard) -> str:
        items = []
        
        # 1. Trigger Quote
        if c.trigger_quote:
            items.append(f"""
            <div style="margin-bottom:15px; border-bottom:1px solid #f1f5f9; padding-bottom:10px;">
                <b style="color:var(--blue);">🗣️ 직접 발언 근거 (인용구):</b><br>
                <div style="margin-top:5px; font-weight:700; color:#1e293b;">"{c.trigger_quote.excerpt}"</div>
                <div style="font-size:11px; color:var(--text-sub); margin-top:3px;">출처: {c.trigger_quote.source_kind} ({c.trigger_quote.source_date})</div>
            </div>
            """)
            
        # 2. Hard Facts (Corporate Actions/Macro)
        hard_facts_raw = c.blocks.get('flow_evidence', []) + c.blocks.get('corporate_facts', [])
        if hard_facts_raw:
            facts_html = []
            for f in hard_facts_raw[:5]:
                facts_html.append(f"<li>{f.get('fact_text', f.get('fact', '데이터 확인 불가'))}</li>")
            
            items.append(f"""
            <div style="margin-bottom:15px;">
                <b style="color:var(--emerald);">✅ 데이터 팩트 (공시/지표):</b>
                <ul style="margin:8px 0; padding-left:20px;">
                    {''.join(facts_html)}
                </ul>
            </div>
            """)
            
        # 3. Decision Rationale
        items.append(f"""
        <div style="background:#f8fafc; padding:12px; border-radius:6px; font-size:12px;">
            <b style="color:var(--purple);">⚙️ 시스템 판단 로직:</b><br>
            {c.decision_rationale}
        </div>
        
        <!-- Factor Bridge Evidence (IS-68) -->
        {self._render_actor_evidence(c)}
        """)
        
        return "".join(items)
    def _render_ticker_path_results(self, c: DecisionCard) -> str:
        results = c.ticker_path.get('ticker_results', [])
        if not results: return ""
        
        items = []
        for r in results:
            ticker_display = r['ticker']
            if r.get('exposure') == "마스킹":
                ticker_display = f"{ticker_display[0]}***" if ticker_display else "***"
            
            badge_color = "#2563eb" if r['confidence'] >= 80 else "#f59e0b"
            badge_text = "✅증거" if r['confidence'] >= 80 else "🟡보통"
            
            items.append(f"""
            <div style="background:white; border:1px solid #e2e8f0; border-radius:10px; padding:12px; flex:1; min-width:180px;">
                <div style="display:flex; justify-content:space-between; align-items:start; margin-bottom:8px;">
                    <div>
                        <div style="font-size:11px; color:#64748b; font-weight:700;">{r['event_type']}</div>
                        <b style="font-size:16px; color:#1e293b;">{r['company_name_ko']}</b>
                        <span style="font-size:12px; color:#94a3b8; margin-left:4px;">{ticker_display}</span>
                    </div>
                    <span style="font-size:10px; background:#f1f5f9; color:{badge_color}; padding:2px 6px; border-radius:4px; font-weight:800;">{badge_text}</span>
                </div>
                <div style="font-size:11px; color:#475569; line-height:1.4;">{r['bottleneck_link_ko']}</div>
            </div>
            """)
            
        return f"""
        <div style="margin-bottom:20px;">
            <div style="color:var(--text-sub); font-size:12px; margin-bottom:8px;">🎯 도출 종목 (실데이터 기반)</div>
            <div style="display:flex; gap:10px; flex-wrap:wrap;">
                {''.join(items)}
            </div>
        </div>
        """

    def _render_actor_evidence(self, c: DecisionCard) -> str:
        actor_ev = c.blocks.get('actor_bridge', {}).get('actor_evidence', [])
        if not actor_ev:
            return ""
            
        items = []
        for ev in actor_ev:
            grade_color = "#2563eb" if "증거" in ev.get('grade', '') else "#475569"
            items.append(f"""
            <div style="background:white; border:1px solid #e2e8f0; border-radius:8px; padding:12px; margin-top:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:5px;">
                    <b style="font-size:12px; color:#1e293b;">{ev.get('title')}</b>
                    <span style="font-size:10px; background:#f1f5f9; color:{grade_color}; padding:2px 6px; border-radius:4px; font-weight:800;">{ev.get('grade')}</span>
                </div>
                <div style="font-size:11px; color:#64748b;">출처: {ev.get('source')} ({ev.get('ts')})</div>
            </div>
            """)
        
        return f"""
        <div style="margin-top:20px; border-top: 1px solid #e2e8f0; padding-top:15px;">
            <b style="color:#2563eb; font-size:13px;">🏷️ 주인공 도출 근거:</b>
            {''.join(items)}
        </div>
        """
    def _render_structural_continuity(self, c: DecisionCard) -> str:
        if not c.bridge_info: return ""
        
        b = c.bridge_info
        return f"""
        <div style="background:#f5f3ff; border:1px solid #ddd6fe; border-radius:12px; padding:20px; margin-bottom:25px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <b style="font-size:14px; color:#5b21b6;">🧠 구조 연속성 추적 (STRUCTURAL CONTINUITY)</b>
                <span style="background:#7c3aed; color:white; font-size:10px; padding:2px 8px; border-radius:4px; font-weight:800;">🔵 구조 해설 → 🟣 현실화</span>
            </div>
            <div style="font-size:13px; color:#4c1d95; line-height:1.5;">
                연결된 구조 ID: <code style="background:#ede9fe; padding:2px 4px; border-radius:4px;">{b['structure_id']}</code><br>
                최초 언급일: <b>{b['timestamp'][:10]} ({b['days_ago']}일 전)</b><br>
                감지된 브릿지: <i>"{b['original_summary']}"</i>
            </div>
        </div>
        """

    def _render_light_card(self, c: DecisionCard) -> str:
        cp = c.blocks.get('content_package', {})
        long_form = cp.get('long_form', '-')
        
        return f"""
        <div class="topic-card-top1" style="border-top: 8px solid #64748b; background: #f8fafc;">
            <!-- Header Group -->
            <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:20px;">
                <div>
                    <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px;">
                        <span style="background:#475569; color:white; padding:4px 12px; border-radius:4px; font-size:12px; font-weight:800;">📘 오늘의 구조 해설 (EDITORIAL · LIGHT)</span>
                        <span style="font-size:12px; color:var(--text-sub); font-weight:600;">상태: 관찰 콘텐츠 (발화 가능)</span>
                    </div>
                    <h1 style="font-size:28px; font-weight:900; color:#1e293b; margin:0; line-height:1.2;">{c.title}</h1>
                </div>
                <div style="text-align:right;">
                    <div style="background:#e2e8f0; padding:8px 12px; border-radius:8px;">
                        <div style="font-size: 11px; font-weight: 700; color: #475569; margin-bottom: 4px;">주인공 ({c.actor_type})</div>
                        <div style="font-size: 14px; font-weight: 800; color: #1e293b;">{c.actor} <span style="font-size:11px; color:#64748b; font-weight:700;">#{c.actor_tag}</span></div>
                    </div>
                </div>
            </div>

            <!-- Caution Message -->
            <div style="background:#f1f5f9; border:1px solid #cbd5e1; padding:12px 15px; border-radius:8px; margin-bottom:25px; display:flex; align-items:center; gap:10px;">
                <span style="font-size:16px;">👁️</span>
                <span style="font-size:13px; font-weight:700; color:#475569;">주의: "본 콘텐츠는 종목/행동 지시가 아닌 구조 해설입니다."</span>
            </div>

            <!-- Narrative Content -->
            <div style="background:#ffffff; border:2px solid #e2e8f0; border-radius:12px; padding:25px; margin-bottom:20px;">
                <div style="font-size:15px; line-height:1.8; color:#334155; white-space:pre-wrap;">{long_form}</div>
                <div style="margin-top:20px; text-align:right;">
                    <button class="copy-btn" style="background:#64748b; color:white; border:none; padding:8px 16px; border-radius:6px; font-weight:700; cursor:pointer;" onclick="copyToClipboard(this.parentElement.previousElementSibling.innerText)">스크립트 복사</button>
                </div>
            </div>

            <div style="font-size: 11px; color: #94a3b8; text-align:right;">
                본 콘텐츠는 에디토리얼 공백 방지를 위한 구조 해설형 레이어(IS-70)에 의해 생성되었습니다.
            </div>
        </div>
        """
    def _render_decision_tree(self, c: DecisionCard) -> str:
        if not c.decision_tree_data: return ""
        
        nodes = []
        for node in c.decision_tree_data:
            icon = "✅" if node['status'] == 'PASS' else "❌" if node['status'] == 'FAIL' else "⚪"
            color = "#10b981" if node['status'] == 'PASS' else "#ef4444" if node['status'] == 'FAIL' else "#94a3b8"
            nodes.append(f"""
            <div style="display:flex; flex-direction:column; align-items:center;">
                <div style="font-size:14px; margin-bottom:4px;">{icon}</div>
                <div style="font-size:9px; font-weight:800; color:{color}; white-space:nowrap;">{node['name']}</div>
            </div>
            """)
        
        # Connectors logic simplified for UI
        tree_html = []
        for i, node_html in enumerate(nodes):
            tree_html.append(node_html)
            if i < len(nodes) - 1:
                tree_html.append('<div style="width:12px; height:1px; background:#e2e8f0; margin-top:10px;"></div>')

        return f"""
        <div style="background:white; border:1px solid #e2e8f0; padding:10px; border-radius:8px; display:inline-flex; align-items:flex-start; gap:5px;">
            <div style="font-size:9px; font-weight:800; color:#64748b; margin-right:8px; writing-mode:vertical-lr; transform:rotate(180deg);">의사결정 트리</div>
            {''.join(tree_html)}
        </div>
        """
