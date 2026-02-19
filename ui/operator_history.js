
export async function initHistoryView(container) {
    container.innerHTML = '<h2>📚 선정 히스토리 (Loading...)</h2>';

    try {
        const response = await fetch('data/decision/interpretation_units.json');
        if (!response.ok) throw new Error('Failed to load history');
        const data = await response.json();

        // Group by Date
        const grouped = data.reduce((acc, item) => {
            const d = item.date || item.as_of_date || "Unknown";
            if (!acc[d]) acc[d] = [];
            acc[d].push(item);
            return acc;
        }, {});

        // Sort Dates Descending
        const sortedDates = Object.keys(grouped).sort((a, b) => new Date(b) - new Date(a));

        renderHistory(container, grouped, sortedDates);

    } catch (e) {
        console.error(e);
        container.innerHTML = `<div class="error-card">Failed to load history: ${e.message}</div>`;
    }
}

function renderHistory(container, grouped, dates) {
    let html = '<div class="history-container">';

    dates.forEach(date => {
        html += `
            <div class="history-group">
                <div class="group-date">${date}</div>
                <table class="history-table">
                    <thead>
                        <tr>
                            <th>Time</th>
                            <th>Title</th>
                            <th>Why Now</th>
                            <th>Intensity</th>
                            <th>Speakability</th>
                        </tr>
                    </thead>
                    <tbody>
        `;

        // Sort items within date by time desc
        const items = grouped[date].sort((a, b) => new Date(b.selected_at) - new Date(a.selected_at));

        items.forEach(item => {
            const time = item.selected_at ? item.selected_at.split('T')[1].substring(0, 5) : "--:--";
            html += `
                <tr onclick="this.classList.toggle('active')">
                    <td>${time}</td>
                    <td>${item.title}</td>
                    <td><span class="badge">${item.why_now_type}</span></td>
                    <td>${item.intensity}</td>
                    <td>${item.speakability}</td>
                </tr>
                <tr class="history-detail-row">
                    <td colspan="5">
                        <div class="history-detail-content">
                            <p><strong>Summary:</strong> ${item.why_now_summary}</p>
                            <p><strong>Hook:</strong> ${item.content_hook}</p>
                        </div>
                    </td>
                </tr>
            `;
        });

        html += `
                    </tbody>
                </table>
            </div>
        `;
    });

    html += '</div>';
    container.innerHTML = html;
}
