async function renderRadar() {
  const content = document.getElementById("content");
  content.innerHTML = '<div class="loading">레이더망 가동 중...</div>';

  try {
    const res = await fetch("../data/ops/validation_tracking.json");
    if (!res.ok) throw new Error("분석 데이터가 없습니다.");
    const data = await res.json();

    const recent = data.slice(-5).reverse();
    const stats_res = await fetch("../data/ops/post_structural_validation.json");
    const stats = stats_res.ok ? await stats_res.json() : null;

    let html = `<h2>📡 현재 이슈 흐름</h2>`;

    if (stats) {
        html += `
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-label">평균 정합성 (Alignment)</div>
            <div class="stat-value" style="color: var(--accent-blue)">${(stats.after.avg_alignment * 100).toFixed(0)}%</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">평균 적중률 (Hit Ratio)</div>
            <div class="stat-value" style="color: var(--accent-emerald)">${(stats.after.avg_hit_ratio * 100).toFixed(0)}%</div>
          </div>
          <div class="stat-item">
             <div class="stat-label">분석 샘플 수</div>
             <div class="stat-value">${stats.after.count}</div>
          </div>
        </div>`;
    }

    html += `<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px;">`;

    recent.forEach(d => {
      html += `
        <div class="card" style="margin-bottom: 0;">
          <h4 style="font-size: 16px; margin-bottom: 8px;">${d.core_theme}</h4>
          <div style="font-size: 12px; color: var(--text-secondary);">${d.date} • ${d.action} • ${d.failure_type}</div>
        </div>
      `;
    });

    html += `</div>`;
    content.innerHTML = html;
  } catch (err) {
    content.innerHTML = `<div class="card" style="border-color: var(--accent-rose)"><h3>⚠️ 오류 발생</h3><p>${err.message}</p></div>`;
  }
}
