
/**
 * Operator History View v2.3
 * Features: Normalization, Incomplete Data Filter (Default On), Same Badges as Today
 */

import { UI_SAFE, normalizeDecision, assertNoUndefined } from './utils.js?v=2.3';

export async function initHistoryView(container) {
    container.innerHTML = `
        <div id="debug-error-banner" class="hidden fixed top-0 left-0 w-full bg-red-600 text-white font-black text-[10px] p-2 z-[100] text-center shadow-xl animate-bounce"></div>
        <div class="p-8 text-slate-500 text-xs animate-pulse uppercase tracking-widest font-black">Syncing Historical Normalization v2.3...</div>
    `;

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
                items.forEach(item => {
                    const norm = normalizeDecision(item);
                    allDecisions.push({ ...norm, _file: file });
                });
            } catch (e) { console.warn(`Skip ${file}`, e); }
        });

        await Promise.all(fetchTasks);

        // State for filtering
        const state = {
            data: allDecisions,
            filters: { type: 'All', intensity: 0, speakability: 'All', hideIncomplete: true }
        };

        renderHistoryFrame(container, state);

    } catch (e) {
        container.innerHTML = `<div class="p-8 text-red-500 font-mono text-xs bg-red-500/5 border border-red-500/20 rounded">History Initialization Failed: ${UI_SAFE.safeStr(e.message)}</div>`;
    }
}

function renderHistoryFrame(container, state) {
    container.innerHTML = `
        <div id="debug-error-banner" class="hidden fixed top-0 left-0 w-full bg-red-600 text-white font-black text-[10px] p-2 z-[100] text-center shadow-xl animate-bounce"></div>
        <div class="space-y-6 fade-in">
            <div class="flex justify-between items-end">
                <h1 class="text-3xl font-black text-white tracking-tighter uppercase">선정 히스토리 v2.3</h1>
                <div class="flex flex-wrap gap-2 items-center">
                    <!-- Incomplete Filter Toggle -->
                    <label class="flex items-center gap-2 bg-slate-900 border border-slate-800 px-3 py-1 rounded cursor-pointer mr-2">
                        <input type="checkbox" id="filter-incomplete" class="w-2.5 h-2.5 bg-slate-800 border-slate-700 rounded accent-blue-500" ${state.filters.hideIncomplete ? 'checked' : ''}>
                        <span class="text-slate-500 text-[9px] font-black uppercase">불완전 데이터 숨기기</span>
                    </label>

                    <select id="filter-type" class="bg-slate-900 border border-slate-800 text-slate-400 text-[10px] font-black px-2 py-1 rounded outline-none appearance-none">
                        <option value="All">All Types</option>
                        <option value="Schedule">Schedule</option>
                        <option value="State">State</option>
                        <option value="Hybrid">Hybrid</option>
                    </select>
                    <select id="filter-int" class="bg-slate-900 border border-slate-800 text-slate-400 text-[10px] font-black px-2 py-1 rounded outline-none appearance-none">
                        <option value="0">Int >= 0</option>
                        <option value="80">Int >= 80</option>
                    </select>
                </div>
            </div>

            <div id="history-list-container" class="space-y-8"></div>
        </div>
    `;

    const update = () => {
        state.filters.type = document.getElementById('filter-type').value;
        state.filters.intensity = parseInt(document.getElementById('filter-int').value);
        state.filters.hideIncomplete = document.getElementById('filter-incomplete').checked;
        renderHistoryList(document.getElementById('history-list-container'), state);
        assertNoUndefined(container.innerHTML);
    };

    document.getElementById('filter-type').onchange = update;
    document.getElementById('filter-int').onchange = update;
    document.getElementById('filter-incomplete').onchange = update;

    update();
}

function renderHistoryList(container, state) {
    const filtered = state.data.filter(item => {
        if (state.filters.hideIncomplete && item.incomplete) return false;
        const tMatch = state.filters.type === 'All' || item.why_now_type === state.filters.type;
        const iMatch = item.intensity >= state.filters.intensity;
        return tMatch && iMatch;
    });

    // Grouping
    const grouped = filtered.reduce((acc, item) => {
        const date = item.date;
        if (!acc[date]) acc[date] = [];
        acc[date].push(item);
        return acc;
    }, {});

    const sortedDates = Object.keys(grouped).sort((a, b) => new Date(b) - new Date(a));

    if (sortedDates.length === 0) {
        container.innerHTML = `<div class="p-20 border border-dashed border-slate-800 rounded-2xl text-center text-slate-700 font-bold uppercase tracking-widest text-[9px]">NO NORM_RECORDS MATCHING CURRENT FILTERS</div>`;
        return;
    }

    container.innerHTML = sortedDates.map(date => `
        <div class="space-y-3">
            <h2 class="text-[10px] font-black text-slate-500 uppercase tracking-[0.4em] flex items-center gap-4">
                <span>${date}</span>
                <div class="h-[1px] bg-slate-800/50 flex-1"></div>
            </h2>
            <div class="space-y-1">
                ${grouped[date].sort((a, b) => new Date(b.selected_at || 0) - new Date(a.selected_at || 0)).map((item, idx) => `
                    <div class="bg-slate-900/40 border border-slate-800/40 hover:bg-slate-800/40 transition-colors group">
                        <div class="p-3 flex items-center gap-4 text-xs cursor-pointer expand-trigger" data-id="${date}-${idx}">
                            <span class="text-slate-600 font-bold w-12 text-[10px]">${UI_SAFE.safeISOTime(item.selected_at)}</span>
                            <span class="${item.incomplete ? 'text-slate-500' : 'text-slate-300'} font-bold flex-1 truncate text-xs">${item.title}</span>
                            <div class="flex gap-2">
                                <span class="bg-slate-900/50 border border-slate-800 text-blue-500 text-[8px] font-black px-1.5 py-0.5 rounded uppercase">${item.display_badge}</span>
                                <span class="bg-slate-900/50 border border-slate-800 text-slate-500 text-[8px] font-black px-1.5 py-0.5 rounded uppercase">INT ${item.intensity}%</span>
                                <span class="bg-slate-900/50 border border-slate-800 ${item.speakability === 'OK' ? 'text-green-600' : 'text-yellow-600'} text-[8px] font-black px-1.5 py-0.5 rounded uppercase">${item.speakability}</span>
                            </div>
                            <div class="icon text-[8px] text-slate-700 group-hover:text-slate-500 ml-2">▼</div>
                        </div>

                        <div id="detail-${date}-${idx}" class="hidden p-4 pt-0 border-t border-slate-800/20 bg-black/10 text-[11px] text-slate-400 space-y-3 fade-in">
                            <div class="pt-4 grid grid-cols-2 gap-8">
                                <div class="space-y-2">
                                    <div class="text-[9px] font-black text-blue-500 uppercase tracking-widest">Why Now Summary</div>
                                    <p class="leading-relaxed font-medium">${item.why_now_summary}</p>
                                </div>
                                <div class="space-y-2">
                                    <div class="text-[9px] font-black text-green-500 uppercase tracking-widest">Evidence Context</div>
                                    <ul class="space-y-1 list-disc pl-4 italic opacity-80">
                                        ${item.anomaly_points.map(pt => `<li>${UI_SAFE.safeStr(pt)}</li>`).join('')}
                                    </ul>
                                </div>
                            </div>
                            <div class="pt-2 flex justify-between items-center border-t border-slate-800/20">
                                <div class="flex gap-1">
                                    ${item.related_assets.map(a => `<span class="bg-slate-800/40 px-2 py-0.5 rounded text-[8px] text-slate-600 border border-slate-800/40">${a}</span>`).join('')}
                                </div>
                                <div class="text-[8px] text-slate-700 font-mono uppercase">SOURCE_NODE: ${item._file} ${item.incomplete ? '| INCOMPLETE' : ''}</div>
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
            const icon = btn.querySelector('.icon');
            if (icon) icon.innerText = target.classList.contains('hidden') ? '▼' : '▲';
        };
    });
}
