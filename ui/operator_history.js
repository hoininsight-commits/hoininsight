
/**
 * Operator History View v2.2
 * Features: Group by Date, Filters (Type/Int/Speak), Detail Panel, Anti-Undefined
 */

const UI_SAFE = {
    get: (val, fallback = "-") => (val === undefined || val === null || val === "" || val === "undefined") ? fallback : val,
    num: (val, fallback = 0) => {
        const n = parseFloat(val);
        return isNaN(n) ? fallback : n;
    }
};

export async function initHistoryView(container) {
    container.innerHTML = '<div class="p-8 text-slate-500 text-xs animate-pulse uppercase tracking-widest font-black">Reconstructing Historical Records...</div>';

    try {
        const manifestResp = await fetch('data/decision/manifest.json?v=' + Date.now());
        if (!manifestResp.ok) throw new Error("Manifest Missing");
        const manifest = await manifestResp.json();

        const allDecisions = [];
        const fetchTasks = (manifest.files || []).map(async (file) => {
            try {
                const res = await fetch(`data/decision/${file}?v=${Date.now()}`);
                if (!res.ok) return;
                const data = await res.json();
                const items = Array.isArray(data) ? data : [data];
                items.forEach(item => allDecisions.push({ ...item, _file: file }));
            } catch (e) { console.warn(`Skip ${file}`, e); }
        });

        await Promise.all(fetchTasks);

        // State for filtering
        const state = {
            data: allDecisions,
            filters: { type: 'All', intensity: 0, speakability: 'All' }
        };

        renderHistoryFrame(container, state);

    } catch (e) {
        container.innerHTML = `<div class="p-8 text-red-500 font-mono text-xs bg-red-500/5 border border-red-500/20 rounded">Failed: ${e.message}</div>`;
    }
}

function renderHistoryFrame(container, state) {
    container.innerHTML = `
        <div class="space-y-6 fade-in">
            <div class="flex justify-between items-end">
                <h1 class="text-3xl font-black text-white tracking-tighter uppercase">선정 히스토리</h1>
                <div class="flex gap-2">
                    <select id="filter-type" class="bg-slate-900 border border-slate-800 text-slate-400 text-[10px] font-black px-2 py-1 rounded outline-none appearance-none">
                        <option value="All">All Types</option>
                        <option value="Schedule">Schedule</option>
                        <option value="State">State</option>
                        <option value="Hybrid">Hybrid</option>
                    </select>
                    <select id="filter-int" class="bg-slate-900 border border-slate-800 text-slate-400 text-[10px] font-black px-2 py-1 rounded outline-none appearance-none">
                        <option value="0">Int >= 0</option>
                        <option value="50">Int >= 50</option>
                        <option value="80">Int >= 80</option>
                    </select>
                    <select id="filter-speak" class="bg-slate-900 border border-slate-800 text-slate-400 text-[10px] font-black px-2 py-1 rounded outline-none appearance-none">
                        <option value="All">All Speak</option>
                        <option value="OK">OK Only</option>
                        <option value="HOLD">HOLD Only</option>
                    </select>
                </div>
            </div>

            <div id="history-list-container" class="space-y-8"></div>
        </div>
    `;

    // Handlers
    const update = () => {
        state.filters.type = document.getElementById('filter-type').value;
        state.filters.intensity = parseInt(document.getElementById('filter-int').value);
        state.filters.speakability = document.getElementById('filter-speak').value;
        renderHistoryList(document.getElementById('history-list-container'), state);
    };

    document.getElementById('filter-type').onchange = update;
    document.getElementById('filter-int').onchange = update;
    document.getElementById('filter-speak').onchange = update;

    update();
}

function renderHistoryList(container, state) {
    const filtered = state.data.filter(item => {
        const tMatch = state.filters.type === 'All' || UI_SAFE.get(item.why_now_type) === state.filters.type;
        const iMatch = UI_SAFE.num(item.intensity) >= state.filters.intensity;
        const sMatch = state.filters.speakability === 'All' || UI_SAFE.get(item.speakability) === state.filters.speakability;
        return tMatch && iMatch && sMatch;
    });

    // Grouping
    const grouped = filtered.reduce((acc, item) => {
        const date = UI_SAFE.get(item.date) || UI_SAFE.get(item.selected_at).split('T')[0] || "Unknown";
        if (!acc[date]) acc[date] = [];
        acc[date].push(item);
        return acc;
    }, {});

    const sortedDates = Object.keys(grouped).sort((a, b) => new Date(b) - new Date(a));

    if (sortedDates.length === 0) {
        container.innerHTML = `<div class="p-20 border border-dashed border-slate-800 rounded-2xl text-center text-slate-600 font-bold uppercase tracking-widest text-xs">No records found for the selected filters.</div>`;
        return;
    }

    container.innerHTML = sortedDates.map(date => `
        <div class="space-y-3">
            <h2 class="text-[10px] font-black text-slate-500 uppercase tracking-[0.4em] flex items-center gap-4">
                <span>${date}</span>
                <div class="h-[1px] bg-slate-800 flex-1"></div>
            </h2>
            <div class="space-y-1">
                ${grouped[date].sort((a, b) => new Date(UI_SAFE.get(b.selected_at, 0)) - new Date(UI_SAFE.get(a.selected_at, 0))).map((item, idx) => `
                    <div class="bg-slate-900/40 border border-slate-800/50 hover:bg-slate-800/60 transition-colors group">
                        <div class="p-3 flex items-center gap-4 text-xs cursor-pointer expand-trigger" data-id="${date}-${idx}">
                            <span class="text-slate-600 font-bold w-12">${UI_SAFE.get(item.selected_at).split('T')[1]?.substring(0, 5) || "--:--"}</span>
                            <span class="text-slate-300 font-bold flex-1 truncate">${UI_SAFE.get(item.title)}</span>
                            <div class="flex gap-2">
                                <span class="bg-slate-900 border border-slate-800 text-slate-500 text-[8px] font-black px-1.5 py-0.5 rounded uppercase">${UI_SAFE.get(item.why_now_type)}</span>
                                <span class="bg-slate-900 border border-slate-800 text-slate-500 text-[8px] font-black px-1.5 py-0.5 rounded uppercase">INT ${UI_SAFE.num(item.intensity)}%</span>
                                <span class="bg-slate-900 border border-slate-800 text-slate-500 text-[8px] font-black px-1.5 py-0.5 rounded uppercase">${UI_SAFE.get(item.speakability)}</span>
                            </div>
                            <div class="icon text-[8px] text-slate-700 group-hover:text-slate-500 ml-2">▼</div>
                        </div>

                        <div id="detail-${date}-${idx}" class="hidden p-4 pt-0 border-t border-slate-800/30 bg-black/10 text-[11px] text-slate-400 space-y-3 fade-in">
                            <div class="pt-4 grid grid-cols-2 gap-8">
                                <div class="space-y-2">
                                    <div class="text-[9px] font-black text-blue-500 uppercase tracking-widest">Why Now Summary</div>
                                    <p class="leading-relaxed font-medium">${UI_SAFE.get(item.why_now_summary)}</p>
                                </div>
                                <div class="space-y-2">
                                    <div class="text-[9px] font-black text-green-500 uppercase tracking-widest">Anomaly Points</div>
                                    <ul class="space-y-1 list-disc pl-4 italic">
                                        ${(item.anomaly_points || ["-"]).map(pt => `<li>${UI_SAFE.get(pt)}</li>`).join('')}
                                    </ul>
                                </div>
                            </div>
                            <div class="pt-2 flex justify-between items-center border-t border-slate-800/30">
                                <div class="flex gap-1">
                                    ${(item.related_assets || ["-"]).map(a => `<span class="bg-slate-800/50 px-2 py-0.5 rounded text-[9px] text-slate-500 border border-slate-800/50">${a}</span>`).join('')}
                                </div>
                                <div class="text-[9px] text-slate-700 font-mono">Source: ${UI_SAFE.get(item._file)}</div>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `).join('');

    // Expand logic
    container.querySelectorAll('.expand-trigger').forEach(btn => {
        btn.onclick = () => {
            const target = container.querySelector(`#detail-${btn.dataset.id}`);
            target.classList.toggle('hidden');
            btn.querySelector('.icon').innerText = target.classList.contains('hidden') ? '▼' : '▲';
        };
    });
}
