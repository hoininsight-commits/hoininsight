
export async function initTodayView(container) {
    container.innerHTML = '<div class="p-8 text-blue-400 animate-pulse">📡 Initializing Today View Logic...</div>';

    const debugState = {
        computedToday: new Date().toLocaleDateString('en-CA'),
        timezoneOffset: new Date().getTimezoneOffset(),
        manifestFiles: [],
        loadResults: [],
        errors: []
    };

    try {
        // 1. Load Manifest
        const manifestResp = await fetch('data/decision/manifest.json?v=' + Date.now());
        if (!manifestResp.ok) throw new Error('Manifest not found. Run publish_ui_assets.py');

        const manifest = await manifestResp.json();
        debugState.manifestFiles = manifest.files || [];

        // 2. Fetch all files in parallel
        const fetchPromises = debugState.manifestFiles.map(async (filename) => {
            try {
                const res = await fetch(`data/decision/${filename}?v=${Date.now()}`);
                if (!res.ok) return { filename, error: `HTTP ${res.status}` };
                const data = await res.json();
                return { filename, data };
            } catch (e) {
                return { filename, error: e.message };
            }
        });

        const rawResults = await Promise.all(fetchPromises);

        // 3. Process and Filter
        const diagnosticData = [];
        const matches = [];

        rawResults.forEach(res => {
            if (res.error) {
                diagnosticData.push({ filename: res.filename, match: false, reason: 'parse error', detail: res.error });
                return;
            }

            const items = Array.isArray(res.data) ? res.data : [res.data];

            items.forEach((item, idx) => {
                const date = item.date || '';
                const selectedAt = item.selected_at || '';

                let isMatch = false;
                let reason = 'date mismatch';

                if (date === debugState.computedToday) {
                    isMatch = true;
                } else if (selectedAt.startsWith(debugState.computedToday)) {
                    isMatch = true;
                }

                if (!date && !selectedAt) reason = 'missing date fields';

                if (isMatch) {
                    matches.push(item);
                }

                diagnosticData.push({
                    filename: res.filename + (items.length > 1 ? `[${idx}]` : ''),
                    date: date,
                    selected_at: selectedAt,
                    match: isMatch,
                    reason: isMatch ? 'OK' : reason
                });
            });
        });

        debugState.loadResults = diagnosticData;
        matches.sort((a, b) => new Date(b.selected_at) - new Date(a.selected_at));

        renderView(container, matches, debugState);

    } catch (e) {
        console.error('Today View Error:', e);
        debugState.errors.push(e.message);
        renderView(container, [], debugState);
    }
}

function renderView(container, matches, debugState) {
    container.innerHTML = `
        <div class="space-y-6 fade-in">
            <div class="flex justify-between items-center">
                <h1 class="text-2xl font-bold text-white">📅 오늘 선정 분석</h1>
                <button id="toggle-debug" class="text-xs px-3 py-1 bg-slate-800 hover:bg-slate-700 text-slate-400 rounded transition-colors">
                    디버그 보기
                </button>
            </div>

            <div id="debug-panel" class="hidden bg-slate-900 border border-slate-700 rounded-lg p-4 font-mono text-[10px] text-slate-300 overflow-x-auto">
                <div class="grid grid-cols-2 gap-4 mb-4 border-b border-slate-800 pb-2">
                    <div>Computed Today: <span class="text-blue-400">${debugState.computedToday}</span></div>
                    <div>TZ Offset: <span class="text-blue-400">${debugState.timezoneOffset}</span></div>
                    <div>Manifest Count: <span class="text-blue-400">${debugState.manifestFiles.length}</span></div>
                    <div>Errors: <span class="text-red-400">${debugState.errors.length}</span></div>
                </div>
                <table class="w-full text-left">
                    <thead>
                        <tr class="text-slate-500 border-b border-slate-800">
                            <th class="py-1">File/Item</th>
                            <th class="py-1">Date</th>
                            <th class="py-1">Selected At</th>
                            <th class="py-1">Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${debugState.loadResults.slice(0, 15).map(res => `
                            <tr class="border-b border-slate-800/50">
                                <td class="py-1 truncate max-w-[120px]">${res.filename}</td>
                                <td class="py-1">${res.date || '-'}</td>
                                <td class="py-1">${res.selected_at || '-'}</td>
                                <td class="py-1 ${res.match ? 'text-green-500' : 'text-slate-500'}">
                                    ${res.match ? 'MATCH' : res.reason}
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
                ${debugState.loadResults.length > 15 ? `<div class="mt-1 text-slate-500">... and ${debugState.loadResults.length - 15} more</div>` : ''}
            </div>

            ${matches.length > 0 ? renderMatches(matches) : renderFallback(debugState)}
        </div>
    `;

    document.getElementById('toggle-debug').onclick = () => {
        const panel = document.getElementById('debug-panel');
        panel.classList.toggle('hidden');
    };
}

function renderMatches(items) {
    const topItem = items[0];
    return `
        <div class="space-y-6">
            <!-- TOP CARD -->
            <div class="bg-blue-600/10 border border-blue-500/30 rounded-xl p-6 shadow-2xl relative overflow-hidden group">
                <div class="absolute top-0 right-0 p-4 opacity-50 text-4xl">🔥</div>
                <div class="flex items-center gap-2 mb-4">
                    <span class="bg-blue-500 text-white text-[10px] font-black px-2 py-0.5 rounded">TOP SIGNAL</span>
                    <span class="text-blue-400 text-xs font-bold uppercase tracking-widest">${topItem.why_now_type}</span>
                </div>
                <h2 class="text-3xl font-black text-white mb-4 leading-tight">${topItem.title}</h2>
                <p class="text-slate-300 text-lg mb-6 leading-relaxed">${topItem.why_now_summary}</p>
                <div class="flex items-center gap-4 pt-4 border-t border-blue-500/20 text-xs font-bold text-slate-400">
                    <div class="flex items-center gap-1"><span class="text-blue-400">⚡ Intensity:</span> ${topItem.intensity}%</div>
                    <div class="flex items-center gap-1"><span class="text-blue-400">🕒 Time:</span> ${topItem.selected_at.split('T')[1].substring(0, 5)}</div>
                </div>
            </div>

            <!-- LIST -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                ${items.map(item => `
                    <div class="bg-slate-800/40 border border-slate-700/50 rounded-lg p-4 hover:bg-slate-800 transition-all cursor-pointer">
                        <div class="flex justify-between items-start mb-2">
                            <span class="text-[10px] font-bold text-slate-500">${item.selected_at.split('T')[1].substring(0, 5)}</span>
                            <span class="text-[10px] font-bold text-blue-400">${item.why_now_type}</span>
                        </div>
                        <h3 class="text-sm font-bold text-white mb-2 line-clamp-2">${item.title}</h3>
                        <div class="text-[10px] text-slate-400 line-clamp-1 italic">"${item.content_hook}"</div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

function renderFallback(debugState) {
    const latestFile = debugState.loadResults[0] || null;
    return `
        <div class="bg-slate-800/20 border-2 border-dashed border-slate-700 rounded-2xl p-12 text-center space-y-4">
            <div class="text-6xl mb-4">🔇</div>
            <h2 class="text-2xl font-black text-white tracking-tight">🔥 오늘은 선정된 주제가 없습니다.</h2>
            <div class="text-slate-400 max-w-sm mx-auto text-sm leading-relaxed">
                현재 시스템이 실시간 신호를 분석 중이나, ${debugState.computedToday} 날짜와 일치하는 결정 사항이 발견되지 않았습니다.
            </div>
            
            <div class="pt-8 grid grid-cols-2 max-w-xs mx-auto gap-2">
                <div class="bg-slate-900/50 p-3 rounded-lg border border-slate-800">
                    <div class="text-[10px] text-slate-500 uppercase font-black mb-1">Total Files</div>
                    <div class="text-xl font-bold text-white">${debugState.manifestFiles.length}</div>
                </div>
                <div class="bg-slate-900/50 p-3 rounded-lg border border-slate-800">
                    <div class="text-[10px] text-slate-500 uppercase font-black mb-1">Today Matches</div>
                    <div class="text-xl font-bold text-red-500">0</div>
                </div>
            </div>

            ${latestFile ? `
                <div class="mt-6 text-[11px] text-slate-500">
                    가장 최근 발견된 데이터: <span class="text-slate-300 font-bold">${latestFile.selected_at || latestFile.date || 'N/A'}</span>
                </div>
            ` : ''}
        </div>
    `;
}
