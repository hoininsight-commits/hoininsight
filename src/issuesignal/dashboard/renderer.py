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
            --bg: #f8fafc;
            --header-bg: #0f172a;
            --card-bg: #FFFFFF;
            --text-main: #1e293b;
            --text-sub: #64748b;
            --emerald: #10b981;
            --blue: #3b82f6;
            --purple: #7c3aed;
            --red: #ef4444;
            --border: #e2e8f0;
            --amber: #f59e0b;
            --amber-light: #fffbeb;
            --amber-border: #fcd34d;
        }}
        body {{ font-family: 'Pretendard', system-ui, sans-serif; background: var(--bg); color: var(--text-main); margin: 0; padding: 0; }}
        
        /* Premium Header */
        .top-header {{ 
            background: var(--header-bg); 
            padding: 0 40px; 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            color: white; 
            height: 64px; 
            box-shadow: 0 4px 12px rgba(0,0,0,0.1); 
            z-index: 100;
        }}
        .header-brand {{ font-size: 18px; font-weight: 800; display:flex; align-items:center; gap:10px; }}
        .header-meta {{ font-size: 11px; color: rgba(255,255,255,0.6); font-family: monospace; text-align: right; display: flex; gap: 15px; letter-spacing: 0.05em; }}
        
        /* Navigation Tabs */
        .nav-tabs {{ 
            background: white; 
            border-bottom: 1px solid var(--border); 
            display: flex; 
            gap: 5px; 
            padding: 0 40px; 
            position: sticky; 
            top: 0; 
            z-index: 99; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.02); 
            height: 50px; 
            align-items: end;
        }}
        .tab-btn {{ 
            padding: 14px 20px; 
            border: none; 
            background: none; 
            font-weight: 600; 
            font-size: 13px; 
            cursor: pointer; 
            color: var(--text-sub); 
            border-bottom: 2px solid transparent; 
            transition: 0.2s; 
            letter-spacing: 0.03em; 
        }}
        .tab-btn:hover {{ color: var(--text-main); background: #f1f5f9; border-radius: 6px 6px 0 0; }}
        .tab-btn.active {{ color: var(--blue); border-bottom-color: var(--blue); background: none; }}
        
        .container {{ padding: 40px; max-width: 1000px; margin: 0 auto; display: none; }}
        .container.active {{ display: block; }}
        
        .section-title {{ font-size: 18px; font-weight: 800; color: #1e293b; margin: 50px 0 25px 0; display: flex; align-items: center; gap: 10px; text-transform: uppercase; letter-spacing: 0.05em; }}
        .section-title::before {{ content: ''; display: inline-block; width: 4px; height: 18px; background: var(--blue); border-radius: 2px; }}
        
        /* Premium Card Styles (Ported from TopicCardRenderer) */
        .topic-card-top1 {{
            background: linear-gradient(135deg, #ffffff 0%, #faf5ff 100%);
            border: 1px solid #e2e8f0; border-top: 5px solid #7c3aed;
            border-radius: 12px; padding: 30px; 
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); 
            margin-bottom: 40px;
            position: relative;
        }}
        .topic-header-label {{ font-size: 11px; font-weight: 800; color: #64748b; text-transform: uppercase; margin-bottom: 12px; display:flex; align-items:center; gap:8px; }}
        .topic-title {{ font-size: 28px; font-weight: 800; color: #1e293b; margin: 10px 0 20px 0; line-height: 1.25; }}
        
        .auth-sentence {{ background:#ECFDF5; border-left:4px solid #059669; padding:15px 20px; color:#065F46; font-weight:700; font-size:15px; line-height:1.6; border-radius: 0 8px 8px 0; margin-bottom: 25px; }}
        
        .one-liner {{ font-size: 16px; line-height: 1.7; font-weight: 500; color: #334155; margin-bottom: 25px; }}
        
        /* Content Package Block */
        .content-package {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; margin-top: 30px; }}
        .cp-header {{ font-size: 13px; font-weight: 700; color: #1e293b; margin-bottom: 15px; display: flex; align-items: center; gap: 6px; text-transform: uppercase; }}
        .cp-row {{ display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }}
        .cp-desc {{ font-size: 12px; color: #64748b; }}
        
        /* Copy Button - Premium Style */
        .copy-btn {{ 
            background: white; border: 1px solid #cbd5e1; padding: 6px 12px; border-radius: 6px; 
            cursor: pointer; font-weight: 600; font-size: 12px; color: #475569; 
            min-width: 130px; text-align: center; transition: all 0.2s; display: flex; align-items: center; justify-content: center; gap: 6px;
        }}
        .copy-btn:hover {{ border-color: #94a3b8; background: #f1f5f9; color: #1e293b; }}
        .copy-btn-primary {{ background: #eff6ff; border-color: #bfdbfe; color: #2563eb; }}
        .copy-btn-primary:hover {{ background: #dbeafe; border-color: #93c5fd; }}
        .copy-btn-shorts {{ background: #fff1f2; border-color: #fecdd3; color: #e11d48; }}
        .copy-btn-shorts:hover {{ background: #ffe4e6; border-color: #fda4af; }}

        /* Meta Pills */
        .meta-pill {{ background: #f1f5f9; color: #475569; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; }}
        .meta-pill.purple {{ background: #f3e8ff; color: #6b21a8; }}

        /* Unified Table Styles */
        .unified-table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 12px; overflow: hidden; border: 1px solid var(--border); box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }}
        .unified-table th {{ background: #f8fafc; padding: 12px 16px; text-align: left; font-size: 11px; font-weight: 800; color: #64748b; text-transform: uppercase; border-bottom: 1px solid var(--border); letter-spacing: 0.05em; }}
        .unified-table td {{ padding: 16px; border-bottom: 1px solid var(--border); font-size: 13px; color: #334155; }}
        .unified-table tr:last-child td {{ border-bottom: none; }}
        
        .status-badge {{ padding: 3px 8px; border-radius: 4px; font-weight: 700; font-size: 11px; display: inline-block; }}
        .status-success {{ background: #dcfce7; color: #166534; }}
        .status-matched {{ background: #dbeafe; color: #1e40af; }}
        .status-no-ev {{ background: #f3f4f6; color: #6b7280; }}
        
        /* Drawer */
        .evidence-drawer {{ background: #fbfcfe; padding: 20px 30px; border-top: 1px solid #e2e8f0; display: none; }}
        .evidence-item {{ background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; margin-bottom: 10px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }}
        
        .expand-btn {{ background: transparent; color: #3b82f6; border: none; font-weight: 600; cursor: pointer; font-size: 12px; display: flex; align-items: center; gap: 4px; }}
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
                <span>COMMIT: {commit_hash}</span>
                <span>ENG: {engine_version}</span>
            </div>
        </div>
    </div>

    <div class="nav-tabs">
        <button class="tab-btn active" onclick="switchTab('issuesignal', this)">IssueSignal Operator</button>
        <button class="tab-btn" onclick="switchTab('hoinevidence', this)">Hoin Artifacts</button>
        <button class="tab-btn" onclick="switchTab('linkview', this)">Evidence Link View</button>
    </div>

    <!-- Tab 1: IssueSignal -->
    <div id="issuesignal" class="container active">
        {self._render_no_topic_alert(summary)}
        
        <div class="summary-grid" style="display:grid; grid-template-columns:repeat(auto-fit, minmax(180px,1fr)); gap:15px; margin-bottom:40px;">
            {self._render_counters(summary.counts)}
        </div>

        <div class="section-title">✨ 오늘의 확정 인텔리전스 (TRUST_LOCKED)</div>
        {self._render_top_cards(summary.top_cards)}

        <div class="section-title">🔭 사전 트리거 감시망 (WATCHLIST)</div>
        {self._render_watchlist(summary.watchlist)}

        <div class="section-title">🚫 개선 필요 및 반려 로그 (REJECT)</div>
        <div style="background:white; padding:20px; border:1px solid #e2e8f0; border-radius:8px;">
            {self._render_reject_logs(summary.reject_logs)}
        </div>
    </div>

    <!-- Tab 2: Hoin Evidence -->
    <div id="hoinevidence" class="container">
        <div class="section-title">🧬 LATEST HOIN ARTIFACTS</div>
        <div style="display:grid; gap:20px;">
            {self._render_hoin_evidence(summary.hoin_evidence)}
        </div>
        {f"<div class='empty-state' style='padding:40px; text-align:center; color:var(--text-sub);'>{summary.date}에 감지된 호인 아티팩트가 없습니다.</div>" if not summary.hoin_evidence else ""}
    </div>

    <!-- Tab 3: Link View -->
    <div id="linkview" class="container">
        <div class="filter-bar" style="margin-bottom:20px; display:flex; gap:15px; align-items:center; font-size:13px; color:#475569;">
            <b>VIEW FILTER:</b>
            <select id="statusFilter" onchange="filterLinkView()" style="padding:4px 8px; border:1px solid #cbd5e1; border-radius:4px;">
                <option value="ALL">All Status</option>
                <option value="TRUST_LOCKED">TRUST_LOCKED (Confirmed)</option>
                <option value="HOLD">HOLD</option>
                <option value="REJECT">REJECT</option>
            </select>
            <label style="display:flex; align-items:center; gap:5px;"><input type="checkbox" id="evOnly" onchange="filterLinkView()"> Evidence Attached Only</label>
            <label style="display:flex; align-items:center; gap:5px;"><input type="checkbox" id="proofOnly" onchange="filterLinkView()"> Verified Proof Only</label>
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
            "TRUST_LOCKED": "확정 (Confirmed)",
            "REJECT": "반려 (Rejected)",
            "PRE_TRIGGER": "감시 (Watching)",
            "HOLD": "보류 (Hold)",
            "SILENT_DROP": "침묵 (Silent)"
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
                <div style="font-size: 11px; font-weight:700; color: #64748b; text-transform:uppercase;">{status_map[status]}</div>
                <div style="font-size: 24px; font-weight: 800; margin-top: 5px; color: #0f172a;">{count}</div>
            </div>
            """)
        return "\n".join(items)

    def _render_top_cards(self, cards: List[DecisionCard]) -> str:
        # [IS-52] Daily Issue Lock Loop UI with Premium Restoration
        if not cards:
            return """
            <div style="background:#fffbeb; border:1px solid #fcd34d; padding:40px; border-radius:12px; margin-bottom:40px; text-align:center; box-shadow:0 4px 6px -1px rgba(0,0,0,0.05);">
                <div style="font-size:3em; margin-bottom:15px;">❌</div>
                <div style="font-weight:800; color:#92400e; font-size:1.5em; margin-bottom:10px;">오늘 발화할 토픽 없음</div>
                <div style="font-size:1.1em; color:#b45309;">사유: 신뢰도 검증 미달 및 중복 트리거</div>
                <div style="margin-top:20px; font-size:0.9em; color:#d97706;">
                    * HOIN 엔진의 엄격한 검증 기준(IS-26)을 통과한 이슈가 없습니다.
                </div>
            </div>
            """
            
        items = []
        for c in cards:
            # Prepare Content Package
            cp = c.blocks.get('content_package', {})
            long_form = cp.get('long_form', '-')
            shorts = cp.get('shorts_ready', [])
            text_card = cp.get('text_card', '-')
            shorts_text = " / ".join(shorts) if shorts else "-"

            # Narrative Block
            narrative_html = ""
            if c.blocks and 'narrative_reconstruction' in c.blocks:
                nr = c.blocks['narrative_reconstruction']
                narrative_html = f"""
                <div style="margin-top:25px; padding-top:25px; border-top:1px dashed #e2e8f0;">
                    <div style="font-size:11px; font-weight:800; color:#475569; margin-bottom:10px; text-transform:uppercase; letter-spacing:0.05em;">
                        📜 역사적 패턴 재구성 (IS-50)
                    </div>
                    <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:15px;">
                         <div style="font-size:12px; margin-bottom:10px; color:#64748b;">
                            유사 사례: <b>{nr['past_case_id']}</b> ({nr['reference_date']}) | 패턴: <span style="color:#ef4444; font-weight:bold;">{nr['pattern_tag']}</span>
                        </div>
                        <div style="font-size:14px; line-height:1.6; color:#334155; white-space: pre-line;">
                            {nr['narrative_text']}
                        </div>
                    </div>
                </div>
                """

            items.append(f"""
            <div class="topic-card-top1">
                <!-- Header -->
                <div class="topic-header-label">
                     <span>🟣 오늘의 구조적 핵심 이슈 (Top-1)</span>
                </div>
                
                <div style="display:flex; justify-content:space-between; align-items:start;">
                    <div>
                        <span class="status-badge status-success" style="padding:4px 10px; font-size:11px;">발화 확정 (TRUST_LOCKED)</span>
                        <h1 class="topic-title">{c.title}</h1>
                    </div>
                    <div style="text-align:right;">
                        <div style="display:flex; gap:6px; justify-content:flex-end;">
                            <span class="meta-pill">{c.actor}</span>
                            <span class="meta-pill purple">{c.trigger_type}</span>
                        </div>
                        <div style="margin-top:5px; font-size:11px; color:#94a3b8;">ID: {c.topic_id}</div>
                    </div>
                </div>

                <!-- Why Now -->
                <div class="auth-sentence">
                    💡 지금 말해야 하는 이유:<br>
                    "{c.authority_sentence}"
                </div>

                <!-- One Liner -->
                <div class="one-liner">
                    {c.one_liner}
                </div>

                <!-- IS-52 Content Package & Operator Actions -->
                <div class="content-package">
                    <div class="cp-header">
                        <span>📋 운영자 콘텐츠 패키지</span>
                        <span style="font-weight:400; color:#94a3b8; font-size:11px;">(Ready to Speak)</span>
                    </div>
                    
                    <!-- Text Card -->
                    <div class="cp-row">
                        <button class="copy-btn" onclick="copyToClipboard(`{text_card}`)">
                            <span>📄 텍스트 카드</span>
                        </button>
                        <span class="cp-desc">한 줄 요약 텍스트</span>
                    </div>

                    <!-- Long Form -->
                    <div class="cp-row">
                        <button class="copy-btn copy-btn-primary" onclick="copyToClipboard(`{long_form}`)">
                            <span>📝 롱폼 스크립트</span>
                        </button>
                        <span class="cp-desc">전체 논리 구조 포함 ({len(long_form)}자)</span>
                    </div>

                    <!-- Shorts -->
                    <div class="cp-row">
                        <button class="copy-btn copy-btn-shorts" onclick="copyToClipboard(`{shorts_text}`)">
                            <span>🎬 숏츠 대본</span>
                        </button>
                        <span class="cp-desc">15초/30초 숏폼용</span>
                    </div>
                </div>

                <div style="font-size: 0.8em; margin-top: 25px; color:#ef4444; font-weight:600;">
                    ⛔ KILL_SWITCH: <span style="font-weight:400; color:#334155;">{c.kill_switch}</span>
                </div>

                {narrative_html}

                <div style="font-size: 0.7em; margin-top: 15px; color: #94a3b8; text-align:right; border-top:1px solid #f1f5f9; padding-top:10px;">
                    Signature Verify: {c.signature or '-'}
                </div>
            </div>
            """)
        return "\n".join(items)

    def _render_watchlist(self, cards: List[DecisionCard]) -> str:
        if not cards: return "<div style='color:var(--text-sub)'>관심 목록이 비어있습니다.</div>"
        rows = []
        for c in cards:
            rows.append(f"""
            <tr>
                <td><b>{c.title}</b></td>
                <td>{c.actor}</td>
                <td>{c.trigger_type}</td>
                <td style="color: var(--blue)">PRE_TRIGGER</td>
            </tr>
            """)
        return f"""
        <table class="watchlist-table">
            <thead>
                <tr>
                    <th>Title</th>
                    <th>Actor</th>
                    <th>Type</th>
                    <th>Status</th>
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
                <div style="font-size: 0.75em; color: var(--purple); font-weight: bold; margin-bottom:5px;">[HOIN ARTIFACT]</div>
                <div style="font-weight: bold; font-size: 1.1em; margin-bottom:8px;">{i.title}</div>
                <div style="font-size: 0.9em; color: var(--text-sub); margin-bottom:12px;">{i.summary}</div>
                <ul style="font-size:0.85em; padding-left:18px; margin-bottom:12px; color:#374151;">
                    {bullets}
                </ul>
                <div style="font-size: 0.75em; color: var(--text-sub); border-top: 1px solid var(--border); padding-top:8px;">
                    SOURCE: <code>{i.source_file}</code>
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
            
            html_rows.append(f"""
            <tr class="link-row" id="row-{idx}" data-status="{c.status}" data-has-ev="{has_ev}" data-has-proof="{has_proof}">
                <td><span class="badge-status {status_class}">{r.link_status}</span></td>
                <td><b>{c.title}</b><br><small>{c.topic_id}</small></td>
                <td>{c.status}</td>
                <td>{", ".join([t.get('symbol', '') for t in c.tickers])}</td>
                <td>
                    <button class="expand-btn" onclick="toggleRow('{idx}')">
                        {len(r.linked_evidence)} Evidence ▾
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
                    <th width="120">LINK</th>
                    <th>ISSUE TITLE</th>
                    <th width="120">STATUS</th>
                    <th width="150">TICKERS</th>
                    <th width="120">HOIN EVIDENCE</th>
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
            items.append(f"<div style='margin-bottom:15px; font-weight:bold; color:var(--green); border-bottom:1px solid var(--border); padding-bottom:5px;'>🌐 SOURCE DIVERSITY (IS-32)</div>")
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
        items.append(f"<div style='margin-bottom:15px; font-weight:bold; color:var(--blue); border-bottom:1px solid var(--border); padding-bottom:5px;'>🗣️ TRIGGER QUOTE PROOF (IS-31)</div>")
        if not c.trigger_quote:
            items.append(f"<div style='color:var(--text-sub); margin-bottom:20px;'>검증된 인용구 증거가 없습니다.</div>")
        else:
            q = c.trigger_quote
            q_status_class = "status-matched" if q.verification_status == "PASS" else "status-no-ev"
            items.append(f"""
            <div class="evidence-item" style="border-left: 4px solid var(--blue); background:#EFF6FF; margin-bottom:20px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <span style="background:#DBEAFE; color:#1E40AF; padding:2px 6px; border-radius:4px; font-size:0.75em; font-weight:bold;">{q.fact_type}</span>
                    <span class="badge-status {q_status_class}">{q.verification_status}: {q.reason_code}</span>
                </div>
                <div style="font-size:1.1em; font-weight:bold; line-height:1.4; color:#1E3A8A; margin:10px 0;">"{q.excerpt}"</div>
                <div style="font-size:0.75em; color:var(--text-sub);">
                    SOURCE: <b>{q.source_kind}</b> ({q.source_date}) | <a href="{q.source_ref}" target="_blank" style="color:var(--blue); text-decoration:none;">{q.source_ref}</a>
                </div>
            </div>
            """)

        # 1. Hoin Evidence Section
        items.append(f"<div style='margin-bottom:15px; font-weight:bold; color:var(--purple); border-bottom:1px solid var(--border); padding-bottom:5px;'>🧬 HOIN EVIDENCE</div>")
        if not row.linked_evidence:
            items.append(f"<div style='color:var(--text-sub); margin-bottom:20px;'>이 카드에 매칭된 호인 증거가 없습니다 ({c.topic_id}).</div>")
        else:
            items.append(f"<div style='margin-bottom:15px; font-weight:bold; color:var(--emerald); font-size:0.85em;'>MATCH REASON: {row.match_reason}</div>")
            for ev in row.linked_evidence:
                bullets = "".join([f"<li>{b}</li>" for b in ev.bullets])
                items.append(f"""
                <div class="evidence-item" style="margin-bottom:10px;">
                    <div style="font-weight:bold; font-size:0.95em;">{ev.title}</div>
                    <div style="font-size:0.85em; color:var(--text-sub); margin:5px 0;">{ev.summary}</div>
                    <ul style="font-size:0.8em; margin:8px 0; padding-left:20px;">{bullets}</ul>
                    <div style="font-size:0.7em; color:var(--blue);">REF: {ev.source_file}</div>
                </div>
                """)

        # 2. Proof Pack Section (IS-30)
        items.append(f"<div style='margin-top:20px; margin-bottom:15px; font-weight:bold; color:var(--amber); border-bottom:1px solid var(--border); padding-bottom:5px;'>🛡️ TICKER PROOF PACKS (IS-30)</div>")
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
                            SOURCE: <b>{f.source_kind}</b> ({f.source_date}) | REF: <code>{f.source_ref}</code>
                        </div>
                    </li>
                    """)
                
                p_status_class = "status-matched" if p.proof_status == "PROOF_OK" else "status-no-ev"
                items.append(f"""
                <div class="evidence-item" style="border-left: 4px solid var(--amber); background:#FFFBEB;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <div style="font-weight:bold; font-size:1em;">{p.ticker}: {p.company_name}</div>
                        <span class="badge-status {p_status_class}">{p.proof_status}</span>
                    </div>
                    <div style="font-size:0.85em; color:#4B5563; margin-bottom:10px; font-style:italic;">"{p.why_irreplaceable_now}"</div>
                    <ul style="margin:0; padding-left:15px; color:#374151;">{''.join(f_items)}</ul>
                </div>
                """)
        
        return "".join(items)
