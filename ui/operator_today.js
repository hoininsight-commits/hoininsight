
/**
 * Operator Today View v2.4 — OPERATOR COMPRESSION MODE
 * Features: Summary Strip, HERO Accent Bar, List Compression, Badge Standardization
 */

import { UI_SAFE, normalizeDecision, assertNoUndefined } from './utils.js?v=2.3';

let CACHED_MANIFEST = null;

export async function initTodayView(container) {
    container.innerHTML = `
        <div id="debug-error-banner" class="hidden fixed top-0 left-0 w-full bg-red-600 text-white font-black text-[10px] p-2 z-[100] text-center shadow-xl animate-bounce"></div>
        <div class="p-8 flex flex-col items-center justify-center space-y-4">
            <div class="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
            <div class="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em]">Compressing Dashboard v2.4...</div>
        </div>
    `;

    const today = new Date().toLocaleDateString('en-CA');
    const debug = { today, matches: 0, totalFiles: 0, mismatchReasons: [] };

    try {
        if (!CACHED_MANIFEST) {
            const manifestResp = await fetch('data/decision/manifest.json?v=' + Date.now());
            if (!manifestResp.ok) throw new Error("Manifest Missing");
            CACHED_MANIFEST = await manifestResp.json();
        }

        debug.totalFiles = (CACHED_MANIFEST.files || []).length;

        const allDecisions = [];
        const fetchTasks = (CACHED_MANIFEST.files || []).map(async (file) => {
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

        // v2.3/v2.4 STABLE SORT
        const getSpeakRank = (s) => (s === 'OK' ? 3 : (s === 'HOLD' ? 2 : 1));
        allDecisions.sort((a, b) => {
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

/**
 * PHASE 4: COLOR & BADGE STANDARDIZATION
 */
const GET_COLORS = {
    speak: (s) => {
        if (s === 'OK') return 'bg-green-500/10 text-green-500 border-green-500/20';
        if (s === 'HOLD') return 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20';
        return 'bg-slate-800 text-slate-500 border-slate-700';
    },
    why: (t) => {
        if (t === 'Schedule') return 'bg-blue-500/10 text-blue-400 border-blue-500/20';
        if (t === 'State') return 'bg-purple-500/10 text-purple-400 border-purple-500/20';
        if (t === 'Hybrid') return 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20';
        return 'bg-slate-800 text-slate-500 border-slate-700';
    },
    intensity: (i) => {
        if (i >= 70) return 'text-red-500 font-black';
        if (i >= 40) return 'text-orange-400 font-bold';
        return 'text-blue-400';
    },
    accent: (i) => {
        if (i >= 70) return 'bg-red-500';
        if (i >= 40) return 'bg-orange-500';
        return 'bg-blue-500';
    }
};

function renderTodayUI(container, items, debug, error = null) {
    const hasItems = items.length > 0;
    const hero = hasItems ? items[0] : null;
    const list = hasItems ? items.slice(1) : [];

    // PHASE 1: SUMMARY STRIP
    let summaryStripHtml = '';
    if (hasItems) {
        const okCount = items.filter(i => i.speakability === 'OK').length;
        const holdCount = items.filter(i => i.speakability === 'HOLD').length;
        const avgInt = Math.round(items.reduce((s, i) => s + i.intensity, 0) / items.length);
        const maxInt = Math.max(...items.map(i => i.intensity));

        summaryStripHtml = `
            <div id="summary-strip" class="bg-slate-800/40 border border-slate-700/30 rounded-lg px-4 h-[44px] flex items-center justify-between mb-4">
                <div class="flex items-center gap-4">
                    <span class="text-[10px] font-black text-slate-300 uppercase italic">운영 요약</span>
                    <div class="h-3 w-[1px] bg-slate-700"></div>
                    <span class="text-[11px] font-bold text-white">오늘 ${items.length}건</span>
                    <span class="text-[11px] text-green-500 font-bold">OK ${okCount}</span>
                    <span class="text-[11px] text-yellow-500 font-bold">HOLD ${holdCount}</span>
                </div>
                <div class="flex items-center gap-4 text-[11px]">
                    <span class="text-slate-500">평균 <strong class="text-slate-300">${avgInt}%</strong></span>
                    <span class="text-slate-500">최고 <strong class="text-red-400">${maxInt}%</strong></span>
                </div>
            </div>
        `;
    } else {
        summaryStripHtml = `
            <div class="bg-slate-800/20 border border-slate-800/50 rounded-lg px-4 h-[44px] flex items-center justify-center mb-4 italic text-[10px] text-slate-600 uppercase tracking-widest">
                오늘 선정 없음
            </div>
        `;
    }

    container.innerHTML = `
        <div id="debug-error-banner" class="hidden fixed top-0 left-0 w-full bg-red-600 text-white font-black text-[10px] p-2 z-[100] text-center shadow-xl animate-bounce"></div>
        <div class="space-y-4 fade-in max-w-6xl mx-auto">
            <!-- Header -->
            <div class="flex justify-between items-end mb-2">
                <h1 class="text-2xl font-black text-white tracking-tighter uppercase blur-[0.2px]">🔥 오늘의 선정</h1>
                <button id="hotfix-debug-trigger" class="text-[9px] font-black text-slate-700 hover:text-slate-500 border border-slate-800/50 px-2 py-0.5 rounded transition-colors uppercase">
                    Debug
                </button>
            </div>

            ${summaryStripHtml}

            <!-- Debug Panel -->
            <div id="hotfix-debug-panel" class="hidden bg-slate-900/80 border border-slate-800 rounded p-3 font-mono text-[9px] text-slate-500 mb-4">
                <div class="grid grid-cols-3 gap-4">
                    <div>Ref: ${debug.today}</div>
                    <div>Docs: ${debug.totalFiles}</div>
                    <div>Hit: ${debug.matches}</div>
                </div>
            </div>

            ${hasItems ? `
                <!-- PHASE 2: HERO CARD VISUAL UPGRADE -->
                <div class="bg-slate-900/80 border border-slate-800 rounded-xl shadow-2xl relative overflow-hidden flex">
                    <div class="w-1.5 ${GET_COLORS.accent(hero.intensity)} flex-shrink-0"></div>
                    
                    <div class="p-6 flex-1 relative">
                        <div class="flex flex-wrap gap-2 mb-4 items-center">
                            <span class="bg-blue-600 text-white text-[9px] font-black px-2 py-0.5 rounded shadow tracking-widest mr-2">
                                ${UI_SAFE.safeISOTime(hero.selected_at)}
                            </span>
                            <span class="${GET_COLORS.why(hero.display_badge)} text-[9px] font-black px-2 py-0.5 rounded border uppercase">
                                WHY: ${hero.display_badge}
                            </span>
                            <span class="${GET_COLORS.speak(hero.speakability)} text-[9px] font-black px-2 py-0.5 rounded border uppercase">
                                ${hero.speakability}
                            </span>
                            <span class="bg-slate-800/50 border border-slate-700 text-[9px] font-black px-2 py-0.5 rounded uppercase ${GET_COLORS.intensity(hero.intensity)}">
                                INT: ${hero.intensity}%
                            </span>
                        </div>

                        <h2 class="text-3xl font-black text-white mb-3 leading-tight tracking-tight">
                            ${hero.title}
                        </h2>
                        
                        <p class="text-slate-400 text-base leading-snug max-w-4xl font-medium mb-6">
                            ${hero.why_now_summary}
                        </p>

                        ${hero.incomplete ? `<div class="text-[9px] font-bold text-red-500/50 mb-4 italic">⚠ 데이터 누락됨</div>` : ''}

                        <div class="pt-4 border-t border-slate-800/50 flex items-center justify-between">
                            <div class="flex gap-1">
                                ${hero.related_assets.map(a => `
                                    <span class="text-[8px] font-black px-1.5 py-0.5 rounded border border-slate-800 text-slate-600 uppercase">
                                        ${a}
                                    </span>
                                `).join('')}
                            </div>
                            <span class="text-[8px] font-black text-slate-700 uppercase tracking-tighter">OPERATOR_v2.4_ALPHA</span>
                        </div>
                    </div>
                </div>

                <!-- PHASE 3: LIST CARD COMPRESSION -->
                <div class="space-y-1.5">
                    <h3 class="text-[9px] font-black text-slate-600 uppercase tracking-[0.4em] px-1 mb-2">
                        추가 항목 (${list.length})
                    </h3>
                    
                    <div class="grid gap-1.5">
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

    container.querySelectorAll('.expand-trigger').forEach(btn => {
        btn.onclick = (e) => {
            const idx = btn.dataset.idx;
            const target = container.querySelector(`#detail-${idx}`);
            target.classList.toggle('hidden');
            const icon = btn.querySelector('.icon');
            if (icon) icon.innerText = target.classList.contains('hidden') ? '▼' : '▲';
        };
    });
}

function renderCompactCard(item, idx) {
    const time = UI_SAFE.safeISOTime(item.selected_at);
    return `
        <div class="bg-slate-900/30 border ${item.incomplete ? 'border-red-900/10' : 'border-slate-800/60'} hover:border-slate-600 rounded-lg transition-all group">
            <div class="px-3 py-2 flex items-center justify-between cursor-pointer expand-trigger" data-idx="${idx}">
                <div class="flex items-center gap-3">
                    <span class="text-[9px] font-black text-slate-600 w-8">${time}</span>
                    <h4 class="text-[13px] font-bold ${item.incomplete ? 'text-slate-500' : 'text-slate-200'} truncate max-w-[300px] lg:max-w-md">
                        ${item.title}
                    </h4>
                    <div class="flex gap-1.5 ml-2">
                        <span class="${GET_COLORS.why(item.display_badge)} text-[8px] font-black px-1.5 rounded border-0 uppercase">${item.display_badge}</span>
                        <span class="${GET_COLORS.speak(item.speakability)} text-[8px] font-black px-1.5 rounded border-0 uppercase">${item.speakability}</span>
                        <span class="${GET_COLORS.intensity(item.intensity)} text-[8px] font-black px-1.5 rounded-0 uppercase tracking-tighter">${item.intensity}%</span>
                    </div>
                </div>
                <div class="icon text-[9px] text-slate-800 group-hover:text-slate-600">▼</div>
            </div>

            <div id="detail-${idx}" class="hidden px-4 pb-3 border-t border-slate-800/20 bg-black/5 text-[10.5px] text-slate-500 space-y-3 fade-in">
                <div class="pt-3 grid grid-cols-2 gap-6">
                    <div>
                        <div class="text-[8px] font-black text-blue-600 uppercase mb-1">Impact Summary</div>
                        <p class="leading-relaxed">${item.why_now_summary}</p>
                    </div>
                    <div>
                        <div class="text-[8px] font-black text-green-600 uppercase mb-1">Risk Signals</div>
                        <ul class="space-y-1 italic list-none">
                            ${item.anomaly_points.map(pt => `<li class="flex gap-2"><span>•</span> ${UI_SAFE.safeStr(pt)}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function renderFallback(debug, error) {
    return `
        <div class="p-16 border border-dashed border-slate-800 rounded-2xl text-center space-y-4">
            <div class="text-4xl opacity-20">📭</div>
            <div class="space-y-1">
                <h2 class="text-xl font-black text-white tracking-widest uppercase">오늘 선정 없음</h2>
                <p class="text-slate-600 text-[10px] font-mono">${debug.today} | SCAN: ${new Date().toLocaleTimeString('ko-KR')}</p>
            </div>
            <div class="text-[10px] font-mono text-center text-slate-800">${error || "NO_MATCH"}</div>
        </div>
    `;
}
