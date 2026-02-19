
export async function initTodayView(container) {
    container.innerHTML = '<h2>🔥 오늘 선정 (Loading...)</h2>';

    try {
        const response = await fetch('data/decision/interpretation_units.json');
        if (!response.ok) throw new Error('Failed to load decisions');
        const data = await response.json();

        // Filter Today (YYYY-MM-DD)
        // Use local time for Korea (implied context) or system time
        // Simple approach: Match exact string if possible, or use latest date as fallback for demo?
        // Prompt says: "Filter by today's date (YYYY-MM-DD)"
        // We will try exact match first.

        const today = new Date();
        const yyyy = today.getFullYear();
        const mm = String(today.getMonth() + 1).padStart(2, '0');
        const dd = String(today.getDate()).padStart(2, '0');
        const todayStr = `${yyyy}-${mm}-${dd}`;

        // For testing purposes, if today has no data, we might want to see something?
        // But prompt says "If no selections: Show clear card".

        const todaysSelections = data.filter(item => item.date === todayStr);

        // Sort by selected_at desc
        todaysSelections.sort((a, b) => new Date(b.selected_at) - new Date(a.selected_at));

        render(container, todaysSelections, todayStr);

    } catch (e) {
        console.error(e);
        container.innerHTML = `<div class="error-card">Failed to load data: ${e.message}</div>`;
    }
}

function render(container, items, dateStr) {
    if (items.length === 0) {
        container.innerHTML = `
            <div class="empty-state-card">
                <h1>🔥 오늘은 선정된 주제가 없습니다.</h1>
                <p>(${dateStr} 기준 엔진 판단 결과)</p>
                <p class="sub-text">시스템이 모니터링 중입니다.</p>
            </div>
        `;
        return;
    }

    const topItem = items[0];
    const restItems = items.slice(0); // All items in list below, or exclude top? Prompt says "Render all today's selections...". implies list includes top? Usually "Top" is highlighted, list is comprehensive. Let's include all in list or separate. 
    // "Render: [Top Selection] ... [Today Selection List]"
    // Usually implies Top is highlighted, then List follows. The list *could* duplicate the top item or exclude it.
    // "Render all today's selections in descending order." -> implied duplication or comprehensive list.
    // Let's render Top separate, then List of *all*.

    let html = `
        <div class="today-container">
            <!-- TOP CARD -->
            <section class="top-section">
                <div class="section-header">🔥 오늘의 TOP 선정</div>
                <div class="top-card" onclick="toggleDetail('${topItem.interpretation_id}')">
                    <div class="top-header">
                        <span class="badge intensity-badge">Intensity ${topItem.intensity}%</span>
                        <span class="badge why-badge">${topItem.why_now_type}</span>
                    </div>
                    <h1 class="top-title">${topItem.title}</h1>
                    <div class="top-summary">${topItem.why_now_summary}</div>
                    <div class="top-footer">
                        <span>Speakability: ${topItem.speakability}</span>
                        <span>${topItem.selected_at.split('T')[1].substring(0, 5)}</span>
                    </div>
                </div>
            </section>

            <!-- LIST -->
            <section class="list-section">
                <div class="section-header">📋 오늘 선정 리스트 (${items.length})</div>
                <div class="card-list">
                    ${items.map(item => renderListItem(item)).join('')}
                </div>
            </section>
        </div>
    `;

    container.innerHTML = html;
}

function renderListItem(item) {
    // anomaly points max 3
    const anomalies = (item.anomaly_points || []).slice(0, 3).map(p => `<span class="tag">${p}</span>`).join('');

    return `
        <div class="list-card" id="card-${item.interpretation_id}">
            <div class="card-main" onclick="this.parentElement.classList.toggle('expanded')">
                <div class="card-time">${item.selected_at.split('T')[1].substring(0, 5)}</div>
                <div class="card-content">
                    <div class="card-row">
                        <span class="card-type">${item.why_now_type}</span>
                        <span class="card-intensity">⚡ ${item.intensity}</span>
                    </div>
                    <div class="card-title">${item.title}</div>
                    <div class="card-tags">${anomalies}</div>
                </div>
                <div class="card-action">▼</div>
            </div>
            <div class="card-detail">
                <div class="detail-row"><strong>Why Now:</strong> ${item.why_now_summary}</div>
                <div class="detail-row"><strong>Hook:</strong> ${item.content_hook}</div>
                <div class="detail-row"><strong>Assets:</strong> ${item.related_assets.length} refs</div>
            </div>
        </div>
    `;
}
