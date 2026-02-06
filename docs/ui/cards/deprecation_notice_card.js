/**
 * REF-010: Legacy Deprecation Notice Card
 * Surfaces active technical debt warnings to the operator.
 */
class DeprecationNoticeCard {
    constructor(containerId) {
        this.containerId = containerId;
        this.ledgerPath = "data/ops/deprecation_ledger.json";
    }

    async render() {
        const container = document.getElementById(this.containerId);
        if (!container) return;

        try {
            const response = await fetch(this.ledgerPath);
            if (!response.ok) return;

            const data = await response.json();
            if (data.status === "OK") return;

            const card = document.createElement("div");
            card.className = "card deprecation-warning";
            card.style.borderLeft = data.status === "FAIL" ? "5px solid #ff4444" : "5px solid #ffbb33";
            card.style.background = "#fff9f0";
            card.style.padding = "15px";
            card.style.marginBottom = "20px";
            card.style.borderRadius = "8px";

            const titleColor = data.status === "FAIL" ? "#cc0000" : "#856404";

            let html = `
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="margin: 0; color: ${titleColor};">⚠️ 시스템 정체성 유지 알림 (${data.status})</h3>
                    <span style="font-size: 0.8em; color: #666;">${data.date}</span>
                </div>
                <p style="margin: 10px 0; font-size: 0.9em; line-height: 1.4;">
                    현재 프로젝트 구조에서 <b>${data.summary.total_hits}건</b>의 레거시 패턴이 감지되었습니다. 
                    (중요도 HIGH: ${data.summary.high}건)
                </p>
                <div style="font-size: 0.85em; background: #fff; padding: 10px; border-radius: 4px; border: 1px solid #eee;">
            `;

            const topHits = data.legacy_hits.slice(0, 3);
            topHits.forEach(hit => {
                html += `
                    <div style="margin-bottom: 8px; border-bottom: 1px dashed #eee; padding-bottom: 5px;">
                        <div style="font-weight: bold; color: #333;">${hit.legacy_key}</div>
                        <div style="color: #666; font-size: 0.9em;">📍 ${hit.path}</div>
                        <div style="color: #0066cc; margin-top: 3px;">💡 권장: ${hit.replacement}</div>
                    </div>
                `;
            });

            if (data.summary.total_hits > 3) {
                html += `<div style="text-align: center; color: #999; font-size: 0.8em;">...외 ${data.summary.total_hits - 3}건 더 있음</div>`;
            }

            html += `</div>`;
            card.innerHTML = html;
            container.prepend(card);

        } catch (e) {
            console.warn("[REF-010] Failed to render deprecation card:", e);
        }
    }
}

// Auto-init if on dashboard
window.addEventListener('DOMContentLoaded', () => {
    // Assuming container id 'alerts-container' exists
    const card = new DeprecationNoticeCard('alerts-container');
    card.render();
});
