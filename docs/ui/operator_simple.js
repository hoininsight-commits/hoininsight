/**
 * STEP-L: Operator Cognitive Layer v1.0
 * Simplified rendering logic for human-centric operation.
 */

async function initOperatorView() {
    const statusBadge = document.getElementById("global-status-badge");
    try {
        const response = await fetch('../data/ui/ui_operator_view.json?v=' + Date.now());
        if (!response.ok) throw new Error("Contract not found");
        const data = await response.json();

        renderOperator(data);
        if (statusBadge) {
            statusBadge.innerText = "운영 준비 완료";
            statusBadge.className = "badge status-ready";
        }
    } catch (error) {
        console.error("[STEP-L] Failed to load operator view:", error);
        if (statusBadge) {
            statusBadge.innerText = "데이터 오류";
            statusBadge.className = "badge status-error";
        }
    }
}

function renderOperator(data) {
    // 1. 오늘의 주제 & Why Now
    document.getElementById("topic-title").innerText = data.today_topic;
    document.getElementById("why-now-text").innerText = data.why_now;

    // 2. 즉시 행동 (Action Metrics)
    const actionEl = document.getElementById("action-val");
    actionEl.innerText = data.action;
    actionEl.className = "metric-val action-" + data.action.toLowerCase();
    
    document.getElementById("timing-val").innerText = data.timing;
    document.getElementById("confidence-val").innerText = Math.round(data.confidence * 100) + "%";
    document.getElementById("risk-val").innerText = data.risk;
    document.getElementById("allocation-val").innerText = Math.round(data.allocation * 100) + "%";

    // 3. 종목 Top 3
    const stockContainer = document.getElementById("stocks-list");
    stockContainer.innerHTML = "";
    data.top_stocks.forEach((stock, index) => {
        const div = document.createElement("div");
        div.className = "stock-card";
        div.innerHTML = `
            <div class="stock-rank">${index + 1}</div>
            <div class="stock-info">
                <div class="stock-name">${stock.name}</div>
                <div class="stock-reason">${stock.reason}</div>
            </div>
        `;
        stockContainer.appendChild(div);
    });

    // 4. 과거 이력 (좌측)
    const historyContainer = document.getElementById("history-list");
    historyContainer.innerHTML = "";
    data.history.forEach(item => {
        const li = document.createElement("li");
        li.innerHTML = `<span class="date">${item.date}</span> <span class="topic">${item.topic}</span> <span class="res">${item.result}</span>`;
        historyContainer.appendChild(li);
    });

    // 5. 활성 주제 (우측)
    const activeContainer = document.getElementById("active-topics-list");
    activeContainer.innerHTML = "";
    data.active_topics.forEach(topic => {
        const div = document.createElement("div");
        div.className = "active-topic-item";
        div.innerText = topic;
        activeContainer.appendChild(div);
    });
    
    // Update last update time
    document.getElementById("last-sync").innerText = "마지막 갱신: " + (data.last_updated || "N/A");
}

document.addEventListener("DOMContentLoaded", initOperatorView);
