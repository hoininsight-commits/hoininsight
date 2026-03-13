/**
 * [STEP-20] Portfolio Relevance Board
 * Fetches data/ops/portfolio_relevance.json and renders
 * CORE / TACTICAL / WATCHLIST pick cards in the dashboard.
 */
(function () {
  "use strict";

  const BASE = "https://hoininsight-commits.github.io/hoininsight";
  const PR_URL = `${BASE}/data/ops/portfolio_relevance.json`;
  const CACHE_BUST = () => `${PR_URL}?v=${Date.now()}`;

  // ─── Direction badge ──────────────────────────────────────────────────────
  function directionBadge(dir) {
    const map = {
      POSITIVE: { cls: "dir-positive", label: "▲ POSITIVE" },
      NEGATIVE: { cls: "dir-negative", label: "▼ NEGATIVE" },
      MIXED:    { cls: "dir-mixed",    label: "◆ MIXED" },
    };
    const { cls, label } = map[dir] || { cls: "dir-neutral", label: "— N/A" };
    return `<span class="dir-badge ${cls}">${label}</span>`;
  }

  // ─── Score bar ────────────────────────────────────────────────────────────
  function scoreBar(score) {
    const pct = Math.min(score, 100);
    const color = score >= 80 ? "#22c55e" : score >= 65 ? "#f59e0b" : "#94a3b8";
    return `
      <div class="score-bar-wrap">
        <div class="score-bar-bg">
          <div class="score-bar-fill" style="width:${pct}%;background:${color}"></div>
        </div>
        <span class="score-label">${score}pt</span>
      </div>`;
  }

  // ─── Single stock card ────────────────────────────────────────────────────
  function stockCard(pick) {
    return `
      <div class="portfolio-card basket-${pick.basket.toLowerCase()}">
        <div class="pc-header">
          <span class="pc-name">${pick.name}</span>
          <span class="pc-ticker">${pick.ticker}</span>
          ${directionBadge(pick.impact_direction)}
        </div>
        <div class="pc-sector">${pick.sector} · ${pick.theme}</div>
        ${scoreBar(pick.portfolio_relevance_score)}
        <div class="pc-reason">${pick.reason || ""}</div>
        <div class="pc-action">${pick.action_note || ""}</div>
        <div class="pc-risk">⚠ ${pick.risk || ""}</div>
      </div>`;
  }

  // ─── Render basket grid ───────────────────────────────────────────────────
  function renderGrid(containerId, picks) {
    const el = document.getElementById(containerId);
    if (!el) return;
    if (!picks || picks.length === 0) {
      el.innerHTML = `<p class="empty-basket">이 바스켓에 해당하는 종목이 없습니다.</p>`;
      return;
    }
    el.innerHTML = picks.map(stockCard).join("");
  }

  // ─── Theme banner ─────────────────────────────────────────────────────────
  function renderThemeBanner(theme) {
    const el = document.getElementById("portfolio-theme-banner");
    if (!el || !theme) return;
    el.innerHTML = `
      <div class="pt-banner">
        <div class="pt-focus">📌 ${theme.portfolio_focus || theme.theme || "—"}</div>
        <div class="pt-summary">${theme.summary || ""}</div>
      </div>`;
  }

  // ─── Tab switcher ─────────────────────────────────────────────────────────
  window.switchBasketTab = function (tab) {
    ["core", "tactical", "watchlist"].forEach(t => {
      const grid = document.getElementById(`portfolio-${t}`);
      const btn  = document.querySelector(`.tab-${t}`);
      if (grid) grid.className = `portfolio-grid ${t === tab ? "active-basket" : "hidden-basket"}`;
      if (btn)  btn.classList.toggle("active", t === tab);
    });
  };

  // ─── Main fetch & render ──────────────────────────────────────────────────
  function init() {
    const section = document.getElementById("portfolio-basket");
    if (!section) return;

    fetch(CACHE_BUST())
      .then(r => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then(data => {
        renderThemeBanner(data.top_portfolio_theme);
        renderGrid("portfolio-core",      data.core_picks      || []);
        renderGrid("portfolio-tactical",  data.tactical_picks  || []);
        renderGrid("portfolio-watchlist", data.watchlist_picks || []);
        section.style.display = "block";
      })
      .catch(err => {
        console.warn("[PortfolioBoard] Failed to load:", err);
        const banner = document.getElementById("portfolio-theme-banner");
        if (banner) banner.innerHTML = `<p class="empty-basket">포트폴리오 데이터를 불러올 수 없습니다 (${err.message})</p>`;
      });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
