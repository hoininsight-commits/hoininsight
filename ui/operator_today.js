
/**
 * Operator Today View v2.3
 * Features: Contract Normalization, Priority Sorting, HERO Meta Header, Anti-Undefined
 */

import { UI_SAFE, normalizeDecision, assertNoUndefined } from './utils.js?v=2.3';

export async function initTodayView(container) {
    container.innerHTML = `
        <div id="debug-error-banner" class="hidden fixed top-0 left-0 w-full bg-red-600 text-white font-black text-[10px] p-2 z-[100] text-center shadow-xl animate-bounce"></div>
        <div class="p-8 flex flex-col items-center justify-center space-y-4">
            <div class="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
            <div class="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em]">Normalizing Decision Stream v2.3...</div>
        </div>
    `;

    const today = new Date().toLocaleDateString('en-CA');
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
                    const norm = normalizeDecision(item);

                    let isToday = false;
                    if (norm.date === today) isToday = true;
                    else if (norm.selected_at.startsWith(today)) isToday = true;

                    if (isToday) {
                        allDecisions.push(norm);
                        debug.matches++;
                    } else {
                        debug.mismatchReasons.push({ file, date: norm.date, selected: norm.selected_at });
                    }
                });
            } catch (e) {
                console.warn(`Failed to parse ${file}`, e);
            }
        });

        await Promise.all(fetchTasks);

        // PHASE 4: TODAY LIST SORTING (OPERATOR PRIORITY)
        // 1) speakability rank: OK(3) > HOLD(2) > "-"(1)
        // 2) intensity desc
        // 3) selected_at desc
        const getSpeakRank = (s) => (s === 'OK' ? 3 : (s === 'HOLD' ? 2 : 1));

        allDecisions.sort((a, b) => {
            // Incomplete items at bottom regardless of intensity
            if (a.incomplete !== b.incomplete) return a.incomplete ? 1 : -1;

            const sA = getSpeakRank(a.speakability);
            const sB = getSpeakRank(b.speakability);
            if (sA !== sB) return sB - sA;

            if (b.intensity !== a.intensity) return b.intensity - a.intensity;

            return new Date(b.selected_at || 0) - new Date(a.selected_at || 0);
        });

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
        <div id="debug-error-banner" class="hidden fixed top-0 left-0 w-full bg-red-600 text-white font-black text-[10px] p-2 z-[100] text-center shadow-xl animate-bounce"></div>
        <div class="space-y-8 fade-in">
            <!-- Header & Debug Toggle -->
            <div class="flex justify-between items-end">
                <div>
                    <h1 class="text-3xl font-black text-white tracking-tighter uppercase blur-[0.3px]">🔥 오늘의 TOP 선정</h1>
                    <p class="text-slate-500 text-xs mt-1 font-medium font-mono">OPERATOR_REF: ${debug.today} / MATCHES: ${debug.matches}</p>
                </div>
                <button id="hotfix-debug-trigger" class="text-[10px] font-black text-slate-600 hover:text-slate-400 border border-slate-800 px-2 py-1 rounded transition-colors uppercase">
                    Debug Mode
                </button>
            </div>

            <!-- Debug Panel -->
            <div id="hotfix-debug-panel" class="hidden bg-slate-900/50 border border-slate-800 rounded p-4 font-mono text-[10px] text-slate-500">
                <div class="grid grid-cols-3 gap-4 mb-2">
                    <div>Today: ${debug.today}</div>
                    <div>Files: ${debug.totalFiles}</div>
                    <div>Matches: ${debug.matches}</div>
                </div>
                <div class="max-h-24 overflow-y-auto border-t border-slate-800 mt-2 pt-2">
                    ${debug.mismatchReasons.slice(0, 5).map(r => `<div>[MISMATCH] ${UI_SAFE.safeStr(r.date)} / ${UI_SAFE.safeStr(r.selected)}</div>`).join('')}
                </div>
            </div>

            ${hasItems ? `
                <!-- v2.3 HERO CARD UPGRADE -->
                <div class="bg-gradient-to-br from-blue-600/20 to-transparent border border-blue-500/30 rounded-2xl p-8 shadow-2xl relative overflow-hidden">
                    <div class="absolute -right-4 -top-4 text-8xl opacity-10 font-black italic select-none">TOP</div>
                    
                    <!-- Meta Info First (PHASE 3) -->
                    <div class="flex flex-wrap gap-2 mb-8 items-center">
                         <div class="bg-blue-600 text-white text-[10px] font-black px-3 py-1.5 rounded shadow-lg uppercase tracking-widest mr-2">
                            TIME: ${UI_SAFE.safeISOTime(hero.selected_at)}
                        </div>
                        <div class="flex gap-1.5 px-3 py-1.5 bg-slate-900/80 rounded-full border border-slate-700/50">
                            <span class="text-blue-400 text-[9px] font-black uppercase tracking-tighter">WHY_NOW: ${hero.display_badge}</span>
                            <span class="text-slate-600 text-[9px]">|</span>
                            <span class="${hero.intensity >= 80 ? 'text-red-400' : 'text-slate-400'} text-[9px] font-black uppercase">INTENSITY: ${hero.intensity}%</span>
                            <span class="text-slate-600 text-[9px]">|</span>
                            <span class="${hero.speakability === 'OK' ? 'text-green-400' : 'text-yellow-400'} text-[9px] font-black uppercase">${hero.speakability}</span>
                        </div>
                    </div>

                    <h2 class="text-4xl font-black text-white mb-6 leading-[1.1] tracking-tight">
                        ${hero.title}
                    </h2>
                    
                    <p class="text-slate-300 text-lg leading-relaxed max-w-4xl font-medium mb-8">
                        ${hero.why_now_summary}
                    </p>

                    ${hero.incomplete ? `
                        <div class="text-[9px] font-bold text-red-500/60 flex items-center gap-2 mb-6">
                            <span>⚠ 데이터 일부 누락(렌더 정상, 원본 확인 필요)</span>
                            <span class="bg-red-500/10 px-1 py-0.5 rounded">MISSING: ${hero.missingFields.join(',')}</span>
                        </div>
                    ` : ''}

                    <div class="pt-6 border-t border-blue-500/10 flex items-center justify-between">
                         <div class="flex gap-1">
                            ${hero.related_assets.map(a => `
                                <span class="bg-slate-800/80 text-blue-400 text-[8px] font-black px-2 py-1 rounded border border-blue-500/10 uppercase tracking-tighter">
                                    ${a}
                                </span>
                            `).join('')}
                        </div>
                        <div class="text-[9px] font-black text-slate-600 uppercase tracking-tighter">OPERATOR_INSIGHT_v2.3</div>
                    </div>
                </div>

                <!-- LIST SECTION -->
                <div class="space-y-4">
                    <h3 class="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em] flex items-center gap-2">
                        <span>결정론적 우선순위 리스트</span>
                        <span class="w-1.5 h-1.5 bg-blue-500 rounded-full"></span>
                    </h3>
                    
                    <div class="grid gap-3">
                        ${list.map((item, idx) => renderCompactCard(item, idx)).join('')}
                    </div>
                </div>
            ` : renderFallback(debug, error)}
        </div>
    `;

    // Anti-Undefined Assertions
    assertNoUndefined(container.innerHTML);

    // Handlers
    document.getElementById('hotfix-debug-trigger').onclick = () => {
        document.getElementById('hotfix-debug-panel').classList.toggle('hidden');
    };

    // Expand logic
    container.querySelectorAll('.expand-trigger').forEach(btn => {
        btn.onclick = (e) => {
            const target = container.querySelector(`#detail-${btn.dataset.idx}`);
            target.classList.toggle('hidden');
            const icon = btn.querySelector('.icon');
            if (icon) icon.innerText = target.classList.contains('hidden') ? '▼' : '▲';
        };
    });
}

function renderCompactCard(item, idx) {
    const time = UI_SAFE.safeISOTime(item.selected_at);
    return `
        <div class="bg-slate-900/40 border ${item.incomplete ? 'border-red-900/20' : 'border-slate-800'} hover:border-slate-700 rounded-xl transition-all">
            <div class="p-4 flex items-center justify-between cursor-pointer expand-trigger" data-idx="${idx}">
                <div class="flex items-center gap-4">
                    <span class="text-[10px] font-black text-slate-600 w-10">${time}</span>
                    <div class="flex flex-col">
                        <h4 class="text-sm font-bold ${item.incomplete ? 'text-slate-400' : 'text-white'} leading-tight">
                            ${item.title}
                        </h4>
                        <div class="flex gap-2 mt-1">
                            <span class="text-[8px] font-black text-blue-500 uppercase tracking-tighter">${item.display_badge}</span>
                            <span class="text-[8px] font-black text-slate-600 uppercase tracking-tighter">INT ${item.intensity}%</span>
                            <span class="text-[8px] font-black ${item.speakability === 'OK' ? 'text-green-600' : 'text-yellow-600'} uppercase tracking-tighter">${item.speakability}</span>
                        </div>
                    </div>
                </div>
                <div class="icon text-[10px] text-slate-700">▼</div>
            </div>

            <div id="detail-${idx}" class="hidden p-4 pt-0 border-t border-slate-800/30 text-[11px] text-slate-400 space-y-4 fade-in">
                <div class="pt-4 grid grid-cols-2 gap-8">
                    <div class="space-y-2">
                        <div class="text-[9px] font-black text-blue-500 uppercase tracking-widest">Why Now Analysis</div>
                        <p class="leading-relaxed font-medium">${UI_SAFE.safeStr(item.why_now_summary)}</p>
                    </div>
                    <div class="space-y-2">
                        <div class="text-[9px] font-black text-green-500 uppercase tracking-widest">Evidence Points</div>
                        <ul class="space-y-1 list-disc pl-4 italic opacity-80">
                            ${item.anomaly_points.map(pt => `<li>${UI_SAFE.safeStr(pt)}</li>`).join('')}
                        </ul>
                    </div>
                </div>
                <div class="flex justify-between items-center py-2 border-t border-slate-800/30">
                    <div class="flex gap-1">
                        ${item.related_assets.map(a => `<span class="bg-slate-800/50 px-2 py-0.5 rounded text-[8px] text-slate-500 border border-slate-800/50">${a}</span>`).join('')}
                    </div>
                    ${item.incomplete ? `<span class="text-[8px] font-black text-red-500 uppercase">⚠ INCOMPLETE</span>` : ''}
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
                <h2 class="text-2xl font-black text-white tracking-tighter uppercase">🔥 오늘은 선정된 주제가 없습니다.</h2>
                <p class="text-slate-500 text-xs font-mono">NODE_DATE: ${debug.today} / SCAN_TIME: ${new Date().toLocaleTimeString('ko-KR')}</p>
            </div>
            
            <div class="flex justify-center gap-4 max-w-sm mx-auto">
                <div class="bg-black/40 p-4 rounded-xl border border-slate-800 flex-1">
                    <div class="text-[9px] font-black text-slate-600 uppercase mb-1">Scanned Files</div>
                    <div class="text-2xl font-bold text-white">${debug.totalFiles}</div>
                </div>
                <div class="bg-black/40 p-4 rounded-xl border border-slate-800 flex-1">
                    <div class="text-[9px] font-black text-slate-600 uppercase mb-1">Today Signals</div>
                    <div class="text-2xl font-bold text-red-600">-</div>
                </div>
            </div>

            <div class="text-[10px] font-mono text-slate-700 bg-slate-900 p-2 rounded inline-block border border-slate-800">
                REASON_CODE: ${error ? UI_SAFE.safeStr(error) : "ZERO_MATCH_THRESHOLD"}
            </div>
        </div>
    `;
}
