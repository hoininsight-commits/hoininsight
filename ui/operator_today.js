
/**
 * Operator Today View v2.5 — HERO STABILIZATION MODE
 * Features: HERO must be Complete+OK/HOLD, Segregated Incomplete List, Opacity Downgrade
 */

import { UI_SAFE, normalizeDecision, assertNoUndefined } from './utils.js?v=2.3';

let CACHED_MANIFEST = null;

export async function initTodayView(container) {
    container.innerHTML = `
        <div id="debug-error-banner" class="hidden fixed top-0 left-0 w-full bg-red-600 text-white font-black text-[10px] p-2 z-[100] text-center shadow-xl animate-bounce"></div>
        <div class="p-8 flex flex-col items-center justify-center space-y-4">
            <div class="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
            <div class="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em]">Stabilizing HERO v2.5...</div>
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

        // PHASE 2: GLOBAL RE-SORT (v2.5)
        // Groups:
        // 1) Complete + OK (Rank 4)
        // 2) Complete + HOLD (Rank 3)
        // 3) Complete + "-" (Rank 2)
        // 4) Incomplete (Rank 1)
        const getGlobalRank = (item) => {
            if (item.incomplete) return 1;
            if (item.speakability === 'OK') return 4;
            if (item.speakability === 'HOLD') return 3;
            return 2;
        };

        allDecisions.sort((a, b) => {
            const rA = getGlobalRank(a);
            const rB = getGlobalRank(b);
            if (rA !== rB) return rB - rA;

            // Within group: intensity desc, selected_at desc
            if (b.intensity !== a.intensity) return b.intensity - a.intensity;
            return new Date(b.selected_at || 0) - new Date(a.selected_at || 0);
        });

        renderTodayUI(container, allDecisions, debug);

    } catch (e) {
        console.error(e);
        renderTodayUI(container, [], debug, e.message);
    }
}

const GET_COLORS = {
    speak: (s) => {
        if (s === 'OK') return 'bg-green-500/10 text-green-500 border-green-500/20';
        if (s === 'HOLD') return 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20';
        return 'bg-slate-800 text-slate-500 border-slate-700';
    },
    why: (t, incomplete = false) => {
        if (incomplete) return 'bg-slate-800 text-slate-500 border-slate-700';
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
    // PHASE 1: HERO SELECTION (Complete Only)
    const completeItems = items.filter(i => !i.incomplete);
    const incompleteItems = items.filter(i => i.incomplete);

    const hasHero = completeItems.length > 0;
    const hero = hasHero ? completeItems[0] : null;
    const completeList = hasHero ? completeItems.slice(1) : completeItems;

    // PHASE 4: SUMMARY STRIP CONSISTENCY
    let summaryStripHtml = '';
    if (items.length > 0) {
        const okCount = items.filter(i => i.speakability === 'OK').length;
        const holdCount = items.filter(i => i.speakability === 'HOLD').length;
        const incompleteCount = incompleteItems.length;
        const completeCount = completeItems.length;
        const avgInt = Math.round(items.reduce((s, i) => s + i.intensity, 0) / items.length);
        const maxInt = Math.max(...items.map(i => i.intensity));

        summaryStripHtml = `
            <div id="summary-strip" class="bg-slate-800/40 border border-slate-700/30 rounded-lg px-4 h-[44px] flex items-center justify-between mb-4">
                <div class="flex items-center gap-4">
                    <span class="text-[10px] font-black text-slate-300 uppercase italic">운영 요약</span>
                    <div class="h-3 w-[1px] bg-slate-700"></div>
                    <span class="text-[11px] font-bold text-white">오늘 ${items.length}건</span>
                    <span class="text-[11px] text-green-500 font-bold">OK ${items.filter(i => !i.incomplete && i.speakability === 'OK').length}</span>
                    <span class="text-[11px] text-yellow-500 font-bold">HOLD ${items.filter(i => !i.incomplete && i.speakability === 'HOLD').length}</span>
                    <span class="text-[11px] text-slate-500 font-bold italic">불완전 ${incompleteCount}</span>
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

            <!-- HERO SECTION -->
            ${hasHero ? `
                <div class="bg-slate-1000/90 border border-slate-800 rounded-xl shadow-2xl relative overflow-hidden flex">
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

                        <div class="pt-4 border-t border-slate-800/50 flex items-center justify-between">
                            <div class="flex gap-1">
                                ${hero.related_assets.map(a => `
                                    <span class="text-[8px] font-black px-1.5 py-0.5 rounded border border-slate-800 text-slate-600 uppercase">
                                        ${a}
                                    </span>
                                `).join('')}
                            </div>
                            <span class="text-[8px] font-black text-slate-700 uppercase tracking-tighter">OPERATOR_v2.5_STABLE</span>
                        </div>
                    </div>
                </div>
            ` : `
                <div class="p-12 border border-dashed border-red-900/40 bg-red-950/5 rounded-xl text-center space-y-4">
                    <div class="text-4xl grayscale opacity-30">⚠</div>
                    <div class="space-y-1">
                        <h2 class="text-lg font-black text-red-500 uppercase tracking-widest">오늘은 완전한 신호가 없습니다.</h2>
                        <p class="text-slate-600 text-[10px] font-mono">모든 신호가 보완 필요 상태이거나 선정된 신호가 없습니다.</p>
                    </div>
                </div>
            `}

            <!-- COMPLETED LIST SECTION -->
            ${completeList.length > 0 ? `
                <div class="space-y-1.5 mt-8">
                    <h3 class="text-[9px] font-black text-slate-600 uppercase tracking-[0.4em] px-1 mb-2 flex items-center gap-2">
                        <span>검증 완료 신호</span>
                        <div class="h-[1px] bg-slate-800 flex-1"></div>
                    </h3>
                    <div class="grid gap-1.5">
                        ${completeList.map((item, idx) => renderCompactCard(item, `complete-${idx}`)).join('')}
                    </div>
                </div>
            ` : ''}

            <!-- INCOMPLETE LIST SECTION (PHASE 3) -->
            ${incompleteItems.length > 0 ? `
                <div class="space-y-1.5 mt-10">
                    <h3 class="text-[9px] font-black text-slate-700 uppercase tracking-[0.4em] px-1 mb-2 flex items-center gap-2">
                        <span class="text-red-900/60">보완 필요 신호</span>
                        <div class="h-[1px] bg-red-950/20 flex-1"></div>
                    </h3>
                    <div class="grid gap-1.5">
                        ${incompleteItems.map((item, idx) => renderCompactCard(item, `incomplete-${idx}`)).join('')}
                    </div>
                </div>
            ` : ''}
        </div>
    `;

    // Anti-Undefined Assertions
    assertNoUndefined(container.innerHTML);

    // Handlers
    document.getElementById('hotfix-debug-trigger').onclick = () => {
        const panel = document.getElementById('hotfix-debug-panel');
        if (panel) panel.classList.toggle('hidden');
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
    // PHASE 3: Visual Downgrade
    const opacityClass = item.incomplete ? 'opacity-75 grayscale-[0.3]' : '';
    const accentBorder = item.incomplete ? 'border-red-900/10' : 'border-slate-800/60';

    return `
        <div class="bg-slate-900/30 border ${accentBorder} hover:border-slate-600 rounded-lg transition-all group ${opacityClass}">
            <div class="px-3 py-2 flex items-center justify-between cursor-pointer expand-trigger" data-idx="${idx}">
                <div class="flex items-center gap-3">
                    <span class="text-[9px] font-black text-slate-600 w-8">${time}</span>
                    <h4 class="text-[13px] font-bold ${item.incomplete ? 'text-slate-500 italic' : 'text-slate-200'} truncate max-w-[300px] lg:max-w-md">
                        ${item.title}
                    </h4>
                    <div class="flex gap-1.5 ml-2">
                        <span class="${GET_COLORS.why(item.display_badge, item.incomplete)} text-[8px] font-black px-1.5 rounded border-0 uppercase">
                            ${item.incomplete ? '● 불완전' : item.display_badge}
                        </span>
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
                ${item.incomplete ? `
                    <div class="pt-2 border-t border-slate-800/10 text-[9px] font-bold text-red-900/50">
                        ⚠ 필수 데이터 누락 필드: ${item.missingFields?.join(', ')}
                    </div>
                ` : ''}
            </div>
        </div>
    `;
}
