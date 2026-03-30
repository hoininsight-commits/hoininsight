async function renderToday() {
  const content = document.getElementById("content");
  content.innerHTML = '<div class="loading">데이터 로딩 중...</div>';

  try {
    const stats_res = await fetch("../data/ops/post_structural_validation.json");
    const stats = stats_res.ok ? await stats_res.json() : null;
    const res = await fetch("../data/ops/today_operator_brief.json");
    if (!res.ok) throw new Error("오늘의 브리핑 데이터가 없습니다.");
    const data = await res.json();
    
    const theme = data.display_title || data.core_theme || "미확인 테마";
    const narrative = data.narrative || {};
    const decision = data.investment_decision || { action: { value: "WATCH" }, confidence: { value: { final_confidence: 0 } } };
    const impact = data.impact_chain || [];
    const radar = data.market_radar || {};

    content.innerHTML = `
      <h2>📌 오늘 포착 주제</h2>
      
      <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
          <h3>${theme}</h3>
          <span class="badge badge-blue">${radar.evolution_stage || "N/A"}</span>
        </div>
        
        <p style="margin-top: 16px; color: var(--text-secondary); line-height: 1.6;">
          <b>왜 지금인가:</b> ${narrative.explanation || "내용 없음"}
        </p>
        
        <div class="stats-grid" style="margin-top: 24px;">
          <div class="stat-item">
            <div class="stat-label">강도 (Intensity)</div>
            <div class="stat-value" style="color: var(--accent-amber)">${radar.momentum_score || "0.0"}</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">행동 지침 (Action)</div>
            <div class="stat-value" style="color: var(--accent-emerald)">${decision.action.value}</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">신뢰도 (Confidence)</div>
            <div class="stat-value">${((decision.confidence.value.final_confidence || 0) * 100).toFixed(0)}%</div>
          </div>
        </div>
        
        <hr/>
        
        <h4 style="margin-bottom: 12px; font-size: 16px; font-weight: 600;">핵심 수혜 종목 (Top 3)</h4>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px;">
          ${impact.slice(0, 3).map(s => `
            <div style="background: rgba(255,255,255,0.02); padding: 12px; border-radius: 8px; border: 1px solid var(--card-border);">
              <div style="font-weight: 700; color: var(--accent-blue);">${s.ticker}</div>
              <div style="font-size: 12px; color: var(--text-secondary);">${s.industry_link || "N/A"}</div>
              <div style="font-size: 11px; margin-top: 8px; opacity: 0.8;">${s.directness || "indirect"}</div>
            </div>
          `).join("")}
        </div>
      </div>

      <div class="card">
        <h3>결정 상세 (Decision Meta)</h3>
        <p style="font-size: 14px; color: var(--text-secondary);">
          <b>마켓 컨텍스트:</b> ${data.market_context || "분석 대기 중"}
        </p>
      </div>
    `;
  } catch (err) {
    content.innerHTML = `<div class="card" style="border-color: var(--accent-rose)"><h3>⚠️ 오류 발생</h3><p>${err.message}</p></div>`;
  }
}
