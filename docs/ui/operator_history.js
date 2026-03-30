async function renderHistory() {
  const content = document.getElementById("content");
  content.innerHTML = '<div class="loading">과거 데이터 분석 중...</div>';

  try {
    const res = await fetch("../data/ops/today_operator_brief.json");
    if (!res.ok) throw new Error("과거 데이터가 없습니다.");
    const data = await res.json();

    const history = data.ui_history || [];

    let html = `<h2>📊 과거 포착 리스트</h2>
                <div style="display:flex; flex-direction:column; gap:16px;">`;

    if (history.length === 0) {
        html += `<div class="card">표시할 과거 데이터가 아직 없습니다.</div>`;
    }

    history.forEach(d => {
      const isSuccess = d.result_status === "SUCCESS";
      const statusColor = isSuccess ? "var(--accent-emerald)" : "var(--accent-rose)";

      html += `
        <div class="card" style="margin-bottom:0;">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <div style="font-weight:700;">${d.date}</div>
            <div style="color:${statusColor}; font-weight:600; font-size:14px;">${d.result_label}</div>
          </div>

          <h4 style="margin:12px 0; font-size:18px;">${d.title}</h4>

          <div style="display:flex; gap:24px; font-size:13px; color: var(--text-secondary);">
            <div><b>지시:</b> <span style="color: var(--text-primary);">${d.action}</span></div>
            <div><b>신뢰도:</b> <span style="color: var(--text-primary);">${d.confidence_pct}%</span></div>
            <div><b>정합성:</b> <span style="color: var(--accent-blue);">${d.alignment_pct}%</span></div>
          </div>
        </div>
      `;
    });

    html += `</div>`;
    content.innerHTML = html;
  } catch (err) {
    content.innerHTML = `<div class="card" style="border-color: var(--accent-rose)"><h3>⚠️ 오류 발생</h3><p>${err.message}</p></div>`;
  }
}
