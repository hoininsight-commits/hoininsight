
/**
 * Operator Today View v2.2
 * Features: HERO + LIST, Robust ISO Matching, Anti-Undefined Policy, Minimized Diagnostics
 */

const UI_SAFE = {
    get: (val, fallback = "-") => (val === undefined || val === null || val === "" || val === "undefined") ? fallback : val,
    num: (val, fallback = 0) => {
        const n = parseFloat(val);
        return isNaN(n) ? fallback : n;
    }
};

export async function initTodayView(container) {
    container.innerHTML = `
        <div class="p-8 flex flex-col items-center justify-center space-y-4">
            <div class="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
            <div class="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em]">Synchronizing Decision Stream...</div>
        </div>
    `;

    const today = new Date().toLocaleDateString('en-CA'); // YYYY-MM-DD
    const debug = { today, matches: 0, totalFiles: 0, mismatchReasons: [] };

    try {
        const manifestResp = await fetch('data/decision/manifest.json?v=' + Date.now());
        if (!manifestResp.ok) throw new Error("Manifest Missing");
        const manifest = await manifestResp.json();
        debug.totalFiles = (manifest.files || []).length;

        const allDecisions = [];
        const fetchTasks = (manifest.files || []).map(async (file) => {
            try {
                const res = await fetch(`data/decision/${file}?v=${Date.now()}`);
                if (!res.ok) return;
                const data = await res.json();
                const items = Array.isArray(data) ? data : [data];

                items.forEach(item => {
                    const dDate = UI_SAFE.get(item.date, "");
                    const dSelected = UI_SAFE.get(item.selected_at, "");

                    let isToday = false;
                    if (dDate === today) isToday = true;
                    else if (dSelected.startsWith(today)) isToday = true;

                    if (isToday) {
                        allDecisions.push(item);
                        debug.matches++;
                    } else {
                        debug.mismatchReasons.push({ file, date: dDate, selected: dSelected });
                    }
                });
            } catch (e) {
                console.warn(`Failed to parse ${file}`, e);
            }
        });

        await Promise.all(fetchTasks);

        // Sort by selected_at desc
        allDecisions.sort((a, b) => new Date(UI_SAFE.get(b.selected_at, 0)) - new Date(UI_SAFE.get(a.selected_at, 0)));

        renderTodayUI(container, allDecisions, debug);

    } catch (e) {
        console.error(e);
        renderTodayUI(container, [], debug, e.message);
    }
}

function renderTodayUI(container, items, debug, error = null) {
    const hasItems = items.length > 0;
    const hero = hasItems ? items[0] : null;
    const list = hasItems ? items.slice(1) : [];

    container.innerHTML = `
        <div class="space-y-8 fade-in">
            <!-- Header & Debug Toggle -->
            <div class="flex justify-between items-end">
                <div>
                    <h1 class="text-3xl font-black text-white tracking-tighter">오늘의 TOP 선정</h1>
                    <p class="text-slate-500 text-xs mt-1 font-medium">운영 기준일: ${debug.today} (KST)</p>
                </div>
                <button id="hotfix-debug-trigger" class="text-[10px] font-black text-slate-600 hover:text-slate-400 border border-slate-800 px-2 py-1 rounded transition-colors uppercase">
                    Debug Mode
                </button>
            </div>

            <!-- Debug Panel (Hidden) -->
            <div id="hotfix-debug-panel" class="hidden bg-slate-900/50 border border-slate-800 rounded p-4 font-mono text-[10px] text-slate-500">
                <div class="grid grid-cols-3 gap-4 mb-2">
                    <div>Today: ${debug.today}</div>
                    <div>Files: ${debug.totalFiles}</div>
                    <div>Matches: ${debug.matches}</div>
                </div>
                <div class="max-h-24 overflow-y-auto border-t border-slate-800 mt-2 pt-2">
                    ${debug.mismatchReasons.slice(0, 10).map(r => `<div>[MISMATCH] ${r.file} (${r.date || 'no-date'})</div>`).join('')}
                </div>
            </div>

            ${hasItems ? `
                <!-- HERO CARD -->
                <div class="bg-gradient-to-br from-blue-600/20 to-transparent border border-blue-500/30 rounded-2xl p-8 shadow-2xl relative overflow-hidden">
                    <div class="absolute -right-4 -top-4 text-8xl opacity-10 font-black italic select-none">TOP</div>
                    
                    <div class="flex flex-wrap gap-2 mb-6">
                        <span class="bg-blue-600 text-white text-[10px] font-black px-2 py-1 rounded shadow-lg uppercase tracking-wider">
                            ${UI_SAFE.get(hero.selected_at).split('T')[1]?.substring(0, 5) || "00:00"}
                        </span>
                        <span class="bg-slate-800 text-blue-400 text-[10px] font-black px-2 py-1 rounded border border-blue-500/20 uppercase">
                            ${UI_SAFE.get(hero.why_now_type)}
                        </span>
                        <span class="${hero.intensity >= 70 ? 'bg-red-500/20 text-red-400 border-red-500/30' : 'bg-slate-800 text-slate-400 border-slate-700/50'} text-[10px] font-black px-2 py-1 rounded border uppercase">
                            INT ${UI_SAFE.num(hero.intensity)}%
                        </span>
                        <span class="bg-slate-800 text-green-400 text-[10px] font-black px-2 py-1 rounded border border-green-500/20 uppercase">
                            ${UI_SAFE.get(hero.speakability, "OK")}
                        </span>
                    </div>

                    <h2 class="text-4xl font-black text-white mb-4 leading-[1.1] tracking-tight">
                        ${UI_SAFE.get(hero.title)}
                    </h2>
                    
                    <p class="text-slate-300 text-lg leading-relaxed max-w-3xl font-medium">
                        ${UI_SAFE.get(hero.why_now_summary)}
                    </p>

                    <div class="mt-8 pt-6 border-t border-blue-500/10 flex items-center gap-6">
                        <div class="text-[10px] font-black text-slate-500 uppercase tracking-widest">Selected For You Today</div>
                        <div class="flex -space-x-2">
                            ${(hero.related_assets || []).slice(0, 3).map(asset => `
                                <div class="w-6 h-6 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-[8px] font-bold text-blue-400 uppercase ring-2 ring-slate-900">
                                    ${asset.substring(0, 2)}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>

                <!-- LIST SECTION -->
                <div class="space-y-4">
                    <h3 class="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em] flex items-center gap-2">
                        <span>오늘 선정 리스트</span>
                        <span class="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></span>
                    </h3>
                    
                    <div class="grid gap-3">
                        ${list.length > 0 ? list.map((item, idx) => renderCompactCard(item, idx)).join('') : `
                            <div class="p-8 border border-dashed border-slate-800 rounded-xl text-center text-slate-600 text-xs font-bold uppercase italic">
                                Additional signals are being processed...
                            </div>
                        `}
                    </div>
                </div>
            ` : renderFallback(debug, error)}
        </div>
    `;

    // Handlers
    document.getElementById('hotfix-debug-trigger').onclick = () => {
        document.getElementById('hotfix-debug-panel').classList.toggle('hidden');
    };

    // Expand logic
    container.querySelectorAll('.expand-trigger').forEach(btn => {
        btn.onclick = (e) => {
            const target = container.querySelector(`#detail-${btn.dataset.idx}`);
            target.classList.toggle('hidden');
            btn.querySelector('.icon').innerText = target.classList.contains('hidden') ? '▼' : '▲';
        };
    });
}

function renderCompactCard(item, idx) {
    const time = UI_SAFE.get(item.selected_at).split('T')[1]?.substring(0, 5) || "--:--";
    return `
        <div class="bg-slate-800/30 border border-slate-800 hover:border-slate-700 rounded-xl transition-all">
            <div class="p-4 flex items-center justify-between cursor-pointer expand-trigger" data-idx="${idx}">
                <div class="flex items-center gap-4">
                    <span class="text-[10px] font-black text-slate-500">${time}</span>
                    <h4 class="text-sm font-bold text-white">${UI_SAFE.get(item.title)}</h4>
                    <div class="flex gap-1">
                        <span class="text-[8px] font-black px-1.5 py-0.5 rounded border border-slate-700 text-slate-500 uppercase">${UI_SAFE.get(item.why_now_type)}</span>
                        <span class="text-[8px] font-black px-1.5 py-0.5 rounded border border-slate-700 text-slate-500 uppercase">INT ${UI_SAFE.num(item.intensity)}%</span>
                    </div>
                </div>
                <div class="icon text-[10px] text-slate-600 transition-transform">▼</div>
            </div>

            <!-- Expandable Details -->
            <div id="detail-${idx}" class="hidden p-4 pt-0 border-t border-slate-800/50 bg-slate-900/20 rounded-b-xl fade-in">
                <div class="space-y-4 pt-4">
                    <div>
                        <div class="text-[9px] font-black text-blue-500 uppercase tracking-widest mb-1">Anomaly Points</div>
                        <ul class="text-[11px] text-slate-400 space-y-1 pl-1">
                            ${(item.anomaly_points || ["-"]).slice(0, 3).map(pt => `<li class="flex items-start gap-2"><span>•</span> ${UI_SAFE.get(pt)}</li>`).join('')}
                        </ul>
                    </div>

                    <div class="flex justify-between items-end">
                        <div>
                            <div class="text-[9px] font-black text-blue-500 uppercase tracking-widest mb-1">Related Assets</div>
                            <div class="flex flex-wrap gap-1">
                                ${(item.related_assets || ["-"]).map(a => `<span class="px-1.5 py-0.5 bg-slate-800 text-[9px] text-slate-400 rounded">${a}</span>`).join('')}
                            </div>
                        </div>
                        <div class="italic text-[10px] text-slate-600 font-medium">
                            "${UI_SAFE.get(item.content_hook).substring(0, 50)}..."
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function renderFallback(debug, error) {
    return `
        <div class="p-20 border-2 border-dashed border-slate-800 rounded-3xl text-center space-y-6">
            <div class="text-7xl opacity-20 grayscale">📭</div>
            <div class="space-y-2">
                <h2 class="text-2xl font-black text-white tracking-tighter">🔥 오늘은 선정된 주제가 없습니다.</h2>
                <p class="text-slate-500 text-xs font-medium">날짜: ${debug.today} | 현재 시각: ${new Date().toLocaleTimeString('ko-KR')}</p>
            </div>
            
            <div class="flex justify-center gap-4 max-w-sm mx-auto">
                <div class="bg-slate-900/50 p-4 rounded-xl border border-slate-800 flex-1">
                    <div class="text-[9px] font-black text-slate-500 uppercase mb-1">Total Assets</div>
                    <div class="text-2xl font-bold text-white">${debug.totalFiles}</div>
                </div>
                <div class="bg-slate-900/50 p-4 rounded-xl border border-slate-800 flex-1">
                    <div class="text-[9px] font-black text-slate-500 uppercase mb-1">Today Matches</div>
                    <div class="text-2xl font-bold text-red-500">0</div>
                </div>
            </div>

            <div class="text-[10px] font-mono text-slate-600 bg-slate-900 p-2 rounded inline-block">
                Reason: ${error || "No dynamic signals matched the current date filter."}
            </div>
        </div>
    `;
}
