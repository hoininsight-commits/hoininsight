from .models import DashboardSummary, DecisionCard, RejectLog, HoinEvidenceItem, UnifiedLinkRow
from typing import List

class DashboardRenderer:
    """
    (IS-27) Renders a static HTML page for IssueSignal Dashboard.
    """
    def render(self, summary: DashboardSummary) -> str:
        html = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IssueSignal & Hoin Unified Dashboard</title>
    <style>
        :root {{
            --bg: #F3F4F6;
            --card-bg: #FFFFFF;
            --text-main: #1F2937;
            --text-sub: #6B7280;
            --emerald: #10B981;
            --blue: #3B82F6;
            --amber: #F59E0B;
            --purple: #8B5CF6;
            --red: #EF4444;
            --border: #E5E7EB;
        }}
        body {{ font-family: -apple-system, system-ui, sans-serif; background: var(--bg); color: var(--text-main); margin: 0; padding: 0; }}
        
        .nav-tabs {{ background: #FFF; border-bottom: 1px solid var(--border); display: flex; gap: 20px; padding: 0 40px; position: sticky; top: 0; z-index: 100; }}
        .tab-btn {{ padding: 15px 5px; border: none; background: none; font-weight: bold; font-size: 0.9em; cursor: pointer; color: var(--text-sub); border-bottom: 3px solid transparent; transition: 0.2s; }}
        .tab-btn.active {{ color: var(--blue); border-bottom-color: var(--blue); }}
        
        .container {{ padding: 30px 40px; display: none; }}
        .container.active {{ display: block; }}
        
        .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }}
        .status-badge {{ padding: 4px 12px; border-radius: 999px; font-weight: bold; font-size: 0.8em; }}
        .status-success {{ background: #D1FAE5; color: #065F46; }}
        
        /* Dashboard Cards */
        .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; margin-bottom: 30px; }}
        .summary-card {{ background: var(--card-bg); padding: 15px; border-radius: 8px; border: 1px solid var(--border); }}
        .summary-card .count {{ font-size: 1.5em; font-weight: bold; margin-top: 5px; }}
        
        .section-title {{ font-size: 1.25em; font-weight: bold; margin: 30px 0 15px 0; }}
        .insight-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 20px; }}
        
        .card-base {{ background: var(--card-bg); border-radius: 12px; border: 1px solid var(--border); box-shadow: 0 1px 3px rgba(0,0,0,0.1); padding: 20px; }}
        .is-card {{ border-left: 6px solid var(--emerald); }}
        .hoin-card {{ border-left: 6px solid var(--purple); }}
        
        /* Unified Link View Table */
        .unified-table {{ width: 100%; border-collapse: collapse; background: #FFF; border-radius: 12px; overflow: hidden; border: 1px solid var(--border); }}
        .unified-table th {{ background: #F9FAFB; padding: 15px; text-align: left; font-size: 0.85em; color: var(--text-sub); border-bottom: 1px solid var(--border); }}
        .unified-table td {{ padding: 15px; border-bottom: 1px solid var(--border); font-size: 0.9em; }}
        .expanded-row {{ background: #F9FAFB; display: none; }}
        
        .evidence-drawer {{ padding: 20px; border-top: 1px solid var(--border); }}
        .evidence-item {{ background: #FFF; border: 1px solid var(--border); border-radius: 8px; padding: 12px; margin-bottom: 10px; }}
        
        /* Interactive */
        .expand-btn {{ cursor: pointer; color: var(--blue); font-weight: bold; border: none; background: none; }}
        .filter-bar {{ display: flex; gap: 10px; margin-bottom: 20px; background: #FFF; padding: 15px; border-radius: 8px; border: 1px solid var(--border); }}
        
        .badge-status {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 0.75em; }}
        .status-trust {{ background: #D1FAE5; color: #065F46; }}
        .status-no-ev {{ background: #F3F4F6; color: #6B7280; border: 1px solid var(--border); }}
        .status-matched {{ background: #E0E7FF; color: #3730A3; }}
    </style>
</head>
<body>
    <div style="background: #FFF; padding: 20px 40px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border);">
        <h1 style="margin:0; font-size: 1.4em;">🛰️ HOIN Unified Ops View</h1>
        <div style="display: flex; gap: 20px; align-items: center;">
            <div style="font-size: 0.9em; color: var(--text-sub);">Data: {summary.date}</div>
            <div class="status-badge status-success">ENGINE: {summary.engine_status}</div>
        </div>
    </div>

    <div class="nav-tabs">
        <button class="tab-btn active" onclick="switchTab('issuesignal', this)">IssueSignal</button>
        <button class="tab-btn" onclick="switchTab('hoinevidence', this)">Hoin Evidence</button>
        <button class="tab-btn" onclick="switchTab('linkview', this)">Link View (IS ↔ Hoin)</button>
    </div>

    <!-- Tab 1: IssueSignal -->
    <div id="issuesignal" class="container active">
        {self._render_no_topic_alert(summary)}
        <div class="summary-grid">
            {self._render_counters(summary.counts)}
        </div>
        <div class="section-title">✨ 오늘의 확정 인텔리전스 (TRUST_LOCKED)</div>
        <div class="insight-grid">
            {self._render_top_cards(summary.top_cards)}
        </div>
        <div class="section-title">🔭 사전 트리거 감시망 (WATCHLIST)</div>
        {self._render_watchlist(summary.watchlist)}
        <div class="section-title">🚫 개선 필요 및 반려 로그 (REJECT)</div>
        <div style="background:#FFF; padding:15px; border:1px solid var(--border); border-radius:8px;">
            {self._render_reject_logs(summary.reject_logs)}
        </div>
    </div>

    <!-- Tab 2: Hoin Evidence -->
    <div id="hoinevidence" class="container">
        <div class="section-title">🧬 LATEST HOIN ARTIFACTS</div>
        <div class="insight-grid">
            {self._render_hoin_evidence(summary.hoin_evidence)}
        </div>
        {f"<div class='empty-state' style='padding:40px; text-align:center; color:var(--text-sub);'>No Hoin artifacts detected for {summary.date}</div>" if not summary.hoin_evidence else ""}
    </div>

    <!-- Tab 3: Link View -->
    <div id="linkview" class="container">
        <div class="filter-bar">
            <b>Filters:</b>
            <select id="statusFilter" onchange="filterLinkView()">
                <option value="ALL">All Status</option>
                <option value="TRUST_LOCKED">TRUST_LOCKED</option>
                <option value="HOLD">HOLD</option>
                <option value="REJECT">REJECT</option>
            </select>
            <label><input type="checkbox" id="evOnly" onchange="filterLinkView()"> Linked Evidence Only</label>
            <label><input type="checkbox" id="proofOnly" onchange="filterLinkView()"> Proof Only</label>
        </div>
        {self._render_link_view(summary.link_view)}
    </div>

    <script>
        function switchTab(tabId, btn) {{
            document.querySelectorAll('.container').forEach(c => c.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            btn.classList.add('active');
        }}

        function toggleRow(id) {{
            const row = document.getElementById('drawer-' + id);
            row.style.display = (row.style.display === 'table-row') ? 'none' : 'table-row';
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
                    document.getElementById('drawer-' + id).style.display = 'none';
                }}
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
            "TRUST_LOCKED": "확정(LOCKED)",
            "REJECT": "반려(REJECT)",
            "PRE_TRIGGER": "감시(WATCH)",
            "HOLD": "보류(HOLD)",
            "SILENT_DROP": "침묵(SILENT)"
        }
        colors = {
            "TRUST_LOCKED": "#10B981",
            "REJECT": "#EF4444",
            "PRE_TRIGGER": "#3B82F6",
            "HOLD": "#F59E0B",
            "SILENT_DROP": "#6B7280"
        }
        for status, count in counts.items():
            if status not in status_map: continue
            color = colors.get(status, "#6B7280")
            items.append(f"""
            <div class="summary-card" style="border-top: 3px solid {color}">
                <div style="font-size: 0.8em; color: var(--text-sub);">{status_map[status]}</div>
                <div class="count">{count}</div>
            </div>
            """)
        return "\n".join(items)

    def _render_top_cards(self, cards: List[DecisionCard]) -> str:
        if not cards: return "<div style='color:var(--text-sub)'>No high-trust insights available today.</div>"
        items = []
        for c in cards:
            items.append(f"""
            <div class="decision-card">
                <div class="title">{c.title}</div>
                <div class="metas">
                    <span class="meta-item">WHO: {c.actor}</span>
                    <span class="meta-item">TYPE: {c.trigger_type}</span>
                    <span class="meta-item">ITEM: {c.must_item}</span>
                </div>
                <div style="font-size: 0.95em; line-height: 1.5; margin-bottom: 15px;">
                    {c.one_liner}
                </div>
                <div style="font-size: 0.85em; border-top: 1px solid var(--border); padding-top: 10px;">
                    <span style="color: var(--red); font-weight: bold;">KILL_SWITCH:</span> {c.kill_switch}
                </div>
                <div style="font-size: 0.7em; margin-top: 10px; color: var(--text-sub);">SIG: {c.signature or '-'}</div>
            </div>
            """)
        return "\n".join(items)

    def _render_watchlist(self, cards: List[DecisionCard]) -> str:
        if not cards: return "<div style='color:var(--text-sub)'>Watchlist empty.</div>"
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
            items.append(f"<div style='color:var(--text-sub); margin-bottom:20px;'>No validated quote proof attached.</div>")
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
            items.append(f"<div style='color:var(--text-sub); margin-bottom:20px;'>NO_HOIN_EVIDENCE matched for this card ({c.topic_id}).</div>")
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
            items.append(f"<div style='color:var(--text-sub)'>No atomic proof packs generated.</div>")
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
