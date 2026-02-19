
export async function initSystemView(container) {
    container.innerHTML = '<h2>⚙️ 시스템 상태 (Loading...)</h2>';

    try {
        const [auditRes, unitsRes, testRes] = await Promise.all([
            fetch('data/ops/usage_audit.json').then(r => r.ok ? r.json() : null),
            fetch('data/decision/interpretation_units.json').then(r => r.ok ? r.json() : []),
            fetch('data/ops/system_health.json').then(r => r.ok ? r.json() : null)
        ]);

        const todayStr = new Date().toISOString().split('T')[0]; // simple UTC date or use local if needed
        // count today's anomalies
        const todayDecisions = unitsRes.filter(item => (item.date || "").startsWith(todayStr));
        const anomalyCount = todayDecisions.length;
        const whyNowDist = todayDecisions.reduce((acc, item) => {
            acc[item.why_now_type] = (acc[item.why_now_type] || 0) + 1;
            return acc;
        }, {});

        renderSystem(container, auditRes, testRes, anomalyCount, whyNowDist);

    } catch (e) {
        console.error(e);
        container.innerHTML = `<div class="error-card">Failed to load system status: ${e.message}</div>`;
    }
}

function renderSystem(container, audit, test, anomalyCount, whyNowDist) {
    const lastScan = audit ? audit.scan_timestamp : "Unknown";
    const testStatus = test ? (test.exit_code === 0 ? "PASSED" : "FAILED") : "Unknown";
    const testColor = testStatus === "PASSED" ? "#4ade80" : "#ef4444";

    let html = `
        <div class="system-grid">
            <!-- Collection Status -->
            <div class="status-card">
                <h3>📊 데이터 수집 상태</h3>
                <div class="stat-row">
                    <span>Latest Collection:</span>
                    <strong class="mono">${lastScan}</strong>
                </div>
                <div class="stat-row">
                    <span>Pipeline Status:</span>
                    <strong style="color: ${testColor}">${testStatus}</strong>
                </div>
                <div class="stat-row">
                    <span>Files Audited:</span>
                    <strong>${audit ? Object.keys(audit.code_references || {}).length : 0}</strong>
                </div>
            </div>

            <!-- Anomalies -->
            <div class="status-card">
                <h3>🚨 이상징후 감지 (Today)</h3>
                <div class="big-number">${anomalyCount}</div>
                <div class="dist-list">
                    ${Object.entries(whyNowDist).map(([k, v]) => `
                        <div class="dist-item">
                            <span>${k}</span>
                            <span>${v}</span>
                        </div>
                    `).join('')}
                </div>
            </div>

            <!-- Logs -->
            <div class="status-card full-width">
                <h3>📜 최근 에러 로그</h3>
                <div class="log-console">
                    ${test && test.recent_failures ? test.recent_failures.map(f => `
                        <div class="log-entry error">
                            <span class="bad">[FAIL]</span> ${f.nodeid} - ${f.message ? f.message.substring(0, 100) : "No msg"}...
                        </div>
                    `).join('') : '<div class="log-entry info">No recent failures logged.</div>'}
                    <div class="log-entry success">[SYSTEM] Dashboard loaded successfully.</div>
                </div>
            </div>
        </div>
    `;

    container.innerHTML = html;
}
