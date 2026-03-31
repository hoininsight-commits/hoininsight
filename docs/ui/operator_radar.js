async function renderRadar() {
  const content = document.getElementById("content");
  content.innerHTML = '<div class="loading">레이더망 가동 중...</div>';

  try {
    const res = await fetch("../data/ops/today_operator_brief.json");
    if (!res.ok) throw new Error("분석 데이터가 없습니다.");
    const data = await res.json();

    const radar = data.ui_radar;
    const engine = data.ui_engine_status;

    if (!radar || !engine) {
        throw new Error("UI 레이더 계약 데이터(ui_radar)가 JSON에 없습니다.");
    }

    let html = `<h2>📡 현재 이슈 흐름</h2>
      <div class="stats-grid">
        <div class="stat-item">
          <div class="stat-label">평균 정합성</div>
          <div class="stat-value" style="color: var(--accent-blue)">${radar.avg_alignment_pct}%</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">평균 적중률</div>
          <div class="stat-value" style="color: var(--accent-emerald)">${radar.avg_hit_ratio_pct}%</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">분석 표본 수</div>
          <div class="stat-value">${radar.sample_size}</div>
        </div>
      </div>

      <div class="card" style="border-left: 4px solid var(--accent-emerald);">
        <h3>엔진 운영 상태: <span style="color: var(--accent-emerald)">${engine.status}</span></h3>
        ${engine.warning ? `<p style="color: var(--accent-amber); margin-top: 8px; font-size: 14px;">⚠️ ${engine.warning}</p>` : "<p style="color: var(--text-secondary); font-size: 14px;">현재 시스템이 안정적으로 운영되고 있습니다.</p>"}
      </div>

      <div style="display:grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap:16px;">`;

    radar.recent_topics.forEach(d => {
      const isSuccess = d.status === "SUCCESS";
      const statusColor = isSuccess ? "var(--accent-emerald)" : "var(--accent-rose)";
      
      html += `
        <div class="card" style="margin-bottom:0;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
             <span style="font-size: 11px; color: var(--text-secondary);">${d.date}</span>
             <span style="font-size: 11px; color: ${statusColor}; font-weight: 500;">${isSuccess ? "SUCCESS" : d.status}</span>
          </div>
          <h4 style="font-size:16px; margin-bottom:8px; line-height: 1.4;">${d.title}</h4>
          <div style="font-size:12px; color: var(--text-secondary);"><b>지침:</b> ${d.action}</div>
        </div>
      `;
    });

    html += `</div>`;
    content.innerHTML = html;
  } catch (err) {
    content.innerHTML = `<div class="card" style="border-color: var(--accent-rose)"><h3>⚠️ 오류 발생</h3><p>${err.message}</p></div>`;
  }
}
