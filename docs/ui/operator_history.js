async function renderHistory() {
  const content = document.getElementById("content");
  content.innerHTML = '<div class="loading">과거 데이터 분석 중...</div>';

  try {
    const res = await fetch("../data/ops/validation_tracking.json");
    if (!res.ok) throw new Error("과거 검증 데이터가 없습니다.");
    const data = await res.json();

    let html = `<h2>📊 과거 포착 리스트</h2>
                <div style="display: flex; flex-direction: column; gap: 16px;">`;

    // Reverse to show latest first
    data.slice().reverse().forEach(d => {
      const isSuccess = d.failure_type === "SUCCESS";
      const statusColor = isSuccess ? "var(--accent-emerald)" : "var(--accent-rose)";
      const statusLabel = isSuccess ? "✅ 성공" : "❌ 보정 필요";

      html += `
        <div class="card" style="margin-bottom: 0;">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="font-weight: 700;">${d.date}</div>
            <div style="color: ${statusColor}; font-weight: 600; font-size: 14px;">${statusLabel}</div>
          </div>
          
          <h4 style="margin: 12px 0; font-size: 18px;">${d.core_theme}</h4>
          
          <div style="display: flex; gap: 24px; font-size: 13px; color: var(--text-secondary);">
            <div><b>지시:</b> ${d.action}</div>
            <div><b>신뢰도:</b> ${(d.confidence * 100).toFixed(0)}%</div>
            <div><b>정합성:</b> ${(d.outcome_alignment * 100).toFixed(0)}%</div>
          </div>
          
          ${!isSuccess ? `<p style="margin-top: 12px; font-size: 12px; color: var(--accent-amber);">원인: ${d.failure_type}</p>` : ""}
        </div>
      `;
    });

    html += `</div>`;
    content.innerHTML = html;
  } catch (err) {
    content.innerHTML = `<div class="card" style="border-color: var(--accent-rose)"><h3>⚠️ 오류 발생</h3><p>${err.message}</p></div>`;
  }
}
