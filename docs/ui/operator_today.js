async function renderToday() {
  const content = document.getElementById("content");
  content.innerHTML = '<div class="loading">데이터 로딩 중...</div>';

  try {
    const res = await fetch("../data/ops/today_operator_brief.json");
    if (!res.ok) throw new Error("오늘 브리핑 데이터가 없습니다.");
    const data = await res.json();

    const ui = data.ui_today;
    const engine = data.ui_engine_status;

    if (!ui || !engine) {
        throw new Error("UI 계약 데이터(ui_*)가 JSON에 포함되어 있지 않습니다. 파이프라인을 확인하세요.");
    }

    content.innerHTML = `
      <h2>📌 오늘 포착 주제</h2>

      <div class="card">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
          <h3>${ui.title}</h3>
          <div style="display:flex; gap:8px;">
            <span class="badge badge-amber">테마 성격: ${ui.theme_type}</span>
            <span class="badge badge-blue">진행 단계: ${ui.evolution_stage}</span>
          </div>
        </div>

        <p style="margin-top:16px; color: var(--text-secondary); line-height:1.6;">
          <b>왜 지금인가:</b> ${ui.why_now}
        </p>

        <div class="stats-grid" style="margin-top:24px;">
          <div class="stat-item">
            <div class="stat-label">강도</div>
            <div class="stat-value" style="color: var(--accent-amber)">${ui.intensity_label}</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">행동 지침</div>
            <div class="stat-value" style="color: var(--accent-emerald)">${ui.action}</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">신뢰도</div>
            <div class="stat-value">${ui.confidence_pct}%</div>
          </div>
        </div>

        <hr style="border: none; border-top: 1px solid var(--card-border); margin: 24px 0;"/>

        <h4 style="margin-bottom:12px;">핵심 수혜 종목 (Top 3)</h4>
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap:12px;">
          ${ui.top_stocks.map(s => `
            <div style="background: rgba(255,255,255,0.02); padding:12px; border-radius:8px; border:1px solid var(--card-border);">
              <div style="font-weight:700; color: var(--accent-blue);">${s.ticker}</div>
              <div style="font-size:12px; color: var(--text-secondary);">${s.industry}</div>
              <div style="font-size:11px; margin-top:8px; opacity:0.8;">${s.directness}</div>
            </div>
          `).join("")}
        </div>
      </div>

      <div class="card">
        <h3>엔진 상태</h3>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
          <div>
            <p><b>운영 상태:</b> <span style="color: var(--accent-emerald)">${engine.status}</span></p>
            <p><b>표본 수:</b> ${engine.sample_size}</p>
          </div>
          <div>
            <p><b>정합성:</b> ${engine.alignment_pct}%</p>
            <p><b>적중률:</b> ${engine.hit_ratio_pct}%</p>
          </div>
        </div>
        ${engine.warning ? `<p style="color: var(--accent-amber); margin-top: 12px; font-size: 13px; background: rgba(255,193,7,0.05); padding: 8px; border-radius: 4px;">⚠️ ${engine.warning}</p>` : ""}
      </div>

      <div class="card">
        <h3>결정 상세</h3>
        <p style="font-size: 14px; color: var(--text-secondary); line-height: 1.6;">
          <b>마켓 컨텍스트:</b> ${ui.market_context}
        </p>
      </div>
    `;
  } catch (err) {
    content.innerHTML = `<div class="card" style="border-color: var(--accent-rose)"><h3>⚠️ 오류 발생</h3><p>${err.message}</p></div>`;
  }
}
