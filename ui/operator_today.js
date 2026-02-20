
/**
 * Operator Today View v2.6 — DECISION MODE UPGRADE
 * Features: Structured No-Signal Panel, Strongest HOLD/Incomplete Highlighting
 */

import { UI_SAFE, normalizeDecision, assertNoUndefined } from './utils.js?v=2.3';

let CACHED_MANIFEST = null;

export async function initTodayView(container) {
    container.innerHTML = `
        <div id="debug-error-banner" class="hidden fixed top-0 left-0 w-full bg-red-600 text-white font-black text-[10px] p-2 z-[100] text-center shadow-xl animate-bounce"></div>
        <div class="p-8 flex flex-col items-center justify-center space-y-4">
            <div class="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
            <div class="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em]">Loading Decision Console v2.6...</div>
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

        // UNIFIED SORTING RULE (v2.6)
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
    const completeItems = items.filter(i => !i.incomplete);
    const incompleteItems = items.filter(i => i.incomplete);
    const okItems = completeItems.filter(i => i.speakability === 'OK');
    const holdItems = completeItems.filter(i => i.speakability === 'HOLD');

    // HERO selection (OK preferred)
    const hero = okItems.length > 0 ? okItems[0] : (holdItems.length > 0 ? holdItems[0] : null);
    const hasHero = hero !== null;

    // Summary Stats
    const totalCount = items.length;
    const okCount = okItems.length;
    const holdCount = holdItems.length;
    const incCount = incompleteItems.length;
    const avgInt = totalCount > 0 ? Math.round(items.reduce((s, i) => s + i.intensity, 0) / totalCount) : 0;
    const maxInt = totalCount > 0 ? Math.max(...items.map(i => i.intensity)) : 0;

    // Build Summary Strip
    const summaryStripHtml = `
        <div id="summary-strip" class="bg-slate-800/40 border border-slate-700/30 rounded-lg px-4 h-[44px] flex items-center justify-between mb-4">
            <div class="flex items-center gap-4">
                <span class="text-[10px] font-black text-slate-300 uppercase italic">운영 요약</span>
                <div class="h-3 w-[1px] bg-slate-700"></div>
                <span class="text-[11px] font-bold text-white">오늘 ${totalCount}건</span>
                <span class="text-[11px] text-green-500 font-bold">OK ${okCount}</span>
                <span class="text-[11px] text-yellow-500 font-bold">HOLD ${holdCount}</span>
                <span class="text-[11px] text-slate-500 font-bold italic">불완전 ${incCount}</span>
            </div>
            <div class="flex items-center gap-4 text-[11px]">
                <span class="text-slate-500">평균 <strong class="text-slate-300">${avgInt}%</strong></span>
                <span class="text-slate-500">최고 <strong class="text-red-400">${maxInt}%</strong></span>
            </div>
        </div>
    `;

    // Build Decision Console Panel (No Signal Mode)
    let heroAreaHtml = '';
    if (hasHero) {
        heroAreaHtml = renderHeroCard(hero);
    } else if (totalCount > 0) {
        // Structured No-Signal Panel (v2.6)
        const strongestHold = holdItems.length > 0 ? holdItems[0] : null;
        const strongestInc = incompleteItems.length > 0 ? incompleteItems[0] : null;

        heroAreaHtml = `
            <div class="bg-slate-900/80 border border-slate-800 rounded-xl p-8 space-y-8 animate-in fade-in slide-in-from-top-4">
                <!-- SECTION A: Status Summary -->
                <div class="flex items-start justify-between">
                    <div class="space-y-2">
                        <div class="text-[10px] font-black text-red-500 uppercase tracking-widest">⚠ Decision Alert</div>
                        <h2 class="text-2xl font-black text-white italic tracking-tighter uppercase">오늘은 완전한 신호가 아직 없습니다.</h2>
                        <div class="flex gap-4 pt-2">
                            <div class="text-[11px] text-slate-500">완전 신호: <span class="text-slate-300">0</span></div>
                            <div class="text-[11px] text-slate-500">HOLD 신호: <span class="text-yellow-500">${holdCount}</span></div>
                            <div class="text-[11px] text-slate-500">불완전 신호: <span class="text-red-400/50">${incCount}</span></div>
                            <div class="text-[11px] text-slate-500">데이터 수집 상태: <span class="text-green-500">정상</span></div>
                        </div>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4 border-t border-slate-800/50">
                    <!-- SECTION B: STRONGEST HOLD -->
                    <div class="space-y-3">
                        <div class="text-[9px] font-black text-slate-600 uppercase tracking-widest flex items-center gap-2">
                            <span>Strongest HOLD</span>
                            <div class="h-[1px] bg-slate-800 flex-1"></div>
                        </div>
                        ${strongestHold ? `
                            <div class="bg-black/20 border border-yellow-900/20 p-4 rounded-lg space-y-2 group hover:border-yellow-900/40 transition-colors">
                                <div class="flex justify-between items-start">
                                    <h4 class="text-xs font-bold text-slate-300 truncate w-4/5">${strongestHold.title}</h4>
                                    <span class="text-yellow-500 font-black text-[10px]">${strongestHold.intensity}%</span>
                                </div>
                                <div class="flex gap-2 items-center text-[9px] text-slate-500 font-bold uppercase">
                                    <span>${UI_SAFE.safeISOTime(strongestHold.selected_at)}</span>
                                    <span>•</span>
                                    <span class="text-blue-500">${strongestHold.display_badge}</span>
                                </div>
                            </div>
                        ` : '<div class="text-[10px] text-slate-700 italic border border-dashed border-slate-800/50 rounded-lg p-4 text-center">HOLD 대상 없음</div>'}
                    </div>

                    <!-- SECTION C: STRONGEST INCOMPLETE -->
                    <div class="space-y-3">
                        <div class="text-[9px] font-black text-slate-600 uppercase tracking-widest flex items-center gap-2">
                            <span>Strongest Incomplete</span>
                            <div class="h-[1px] bg-slate-800 flex-1"></div>
                        </div>
                        ${strongestInc ? `
                            <div class="bg-black/20 border border-red-900/10 p-4 rounded-lg space-y-2 opacity-70 group hover:opacity-100 transition-opacity">
                                <div class="flex justify-between items-start">
                                    <h4 class="text-xs font-bold text-slate-500 truncate w-4/5 italic">${strongestInc.title}</h4>
                                    <span class="text-slate-600 font-black text-[10px]">${strongestInc.intensity}%</span>
                                </div>
                                <div class="flex gap-2 items-center text-[9px] text-slate-600 font-bold uppercase">
                                    <span class="bg-slate-800 px-1.5 rounded-sm">보완 필요</span>
                                    <span>•</span>
                                    <span>${UI_SAFE.safeISOTime(strongestInc.selected_at)}</span>
                                </div>
                            </div>
                        ` : '<div class="text-[10px] text-slate-700 italic border border-dashed border-slate-800/50 rounded-lg p-4 text-center">불완전 신호 없음</div>'}
                    </div>
                </div>
            </div>
        `;
    } else {
        heroAreaHtml = `
            <div class="p-20 border border-dashed border-slate-800 bg-slate-900/10 rounded-xl text-center space-y-4">
                <div class="text-5xl grayscale opacity-20">🌫</div>
                <h2 class="text-lg font-black text-slate-600 uppercase tracking-[0.4em]">오늘 수집된 신호가 없습니다.</h2>
                <p class="text-[10px] font-medium text-slate-700 uppercase tracking-widest">Waiting for next engine cycle...</p>
            </div>
        `;
    }

    container.innerHTML = `
        <div id="debug-error-banner" class="hidden fixed top-0 left-0 w-full bg-red-600 text-white font-black text-[10px] p-2 z-[100] text-center shadow-xl animate-bounce"></div>
        <div class="space-y-4 fade-in max-w-6xl mx-auto">
            <div class="flex justify-between items-end mb-2">
                <h1 class="text-2xl font-black text-white tracking-tighter uppercase blur-[0.2px]">🔥 오늘의 선정</h1>
                <button id="hotfix-debug-trigger" class="text-[9px] font-black text-slate-700 hover:text-slate-500 border border-slate-800/50 px-2 py-0.5 rounded transition-colors uppercase">
                    Debug
                </button>
            </div>

            ${summaryStripHtml}
            ${heroAreaHtml}

            <!-- LIST SECTIONS (Only if complete list exists beyond hero) -->
            ${completeItems.filter(i => i.interpretation_id !== hero?.interpretation_id).length > 0 ? `
                <div class="space-y-1.5 mt-8">
                    <h3 class="text-[9px] font-black text-slate-600 uppercase tracking-[0.4em] px-1 mb-2 flex items-center gap-2">
                        <span>검증 완료 신호</span>
                        <div class="h-[1px] bg-slate-800 flex-1"></div>
                    </h3>
                    <div class="grid gap-1.5">
                        ${items.filter(i => !i.incomplete && i.interpretation_id !== hero?.interpretation_id).map((item, idx) => renderCompactCard(item, `c-${idx}`)).join('')}
                    </div>
                </div>
            ` : ''}

            ${incompleteItems.length > 0 ? `
                <div class="space-y-1.5 mt-10">
                    <h3 class="text-[9px] font-black text-slate-700 uppercase tracking-[0.4em] px-1 mb-2 flex items-center gap-2">
                        <span class="text-red-900/60">보완 필요 신호</span>
                        <div class="h-[1px] bg-red-950/20 flex-1"></div>
                    </h3>
                    <div class="grid gap-1.5">
                        ${incompleteItems.map((item, idx) => renderCompactCard(item, `i-${idx}`)).join('')}
                    </div>
                </div>
            ` : ''}
        </div>
    `;

    assertNoUndefined(container.innerHTML);
    bindEvents(container);
}

function renderHeroCard(hero) {
    return `
        <div class="bg-slate-1000/90 border border-slate-800 rounded-xl shadow-2xl relative overflow-hidden flex animate-in slide-in-from-top-4 duration-500">
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
                <h2 class="text-3xl font-black text-white mb-3 leading-tight tracking-tight uppercase">${hero.title}</h2>
                <p class="text-slate-400 text-base leading-snug max-w-4xl font-medium mb-6">${hero.why_now_summary}</p>
                <div class="pt-4 border-t border-slate-800/50 flex items-center justify-between">
                    <div class="flex gap-1">
                        ${hero.related_assets.map(a => `
                            <span class="text-[8px] font-black px-1.5 py-0.5 rounded border border-slate-800 text-slate-600 uppercase">${a}</span>
                        `).join('')}
                    </div>
                    <span class="text-[8px] font-black text-slate-700 uppercase tracking-tighter">OPERATOR_v2.6_STABLE</span>
                </div>
            </div>
        </div>
    `;
}

function renderCompactCard(item, idx) {
    const time = UI_SAFE.safeISOTime(item.selected_at);
    const opacityClass = item.incomplete ? 'opacity-75 grayscale-[0.3]' : '';
    const hoverBorder = item.incomplete ? 'hover:border-red-900/30' : 'hover:border-slate-500';
    const accentBorder = item.incomplete ? 'border-red-950/10' : 'border-slate-800/60';

    return `
        <div class="bg-slate-900/30 border ${accentBorder} ${hoverBorder} rounded-lg transition-all group ${opacityClass}">
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
            <div id="detail-${idx}" class="hidden px-4 pb-3 border-t border-slate-800/20 bg-black/5 text-[10.5px] text-slate-500 space-y-3">
                <div class="pt-3 grid grid-cols-2 gap-6">
                    <div class="space-y-1">
                        <div class="text-[8px] font-black text-blue-600 uppercase mb-1">Impact Summary</div>
                        <p class="leading-relaxed font-medium">${item.why_now_summary}</p>
                    </div>
                    <div class="space-y-1">
                        <div class="text-[8px] font-black text-green-600 uppercase mb-1">Risk Signals</div>
                        <ul class="space-y-1 italic list-none">
                            ${item.anomaly_points.map(pt => `<li class="flex gap-2"><span>•</span> ${UI_SAFE.safeStr(pt)}</li>`).join('')}
                        </ul>
                    </div>
                </div>
                ${item.incomplete ? `<div class="pt-2 border-t border-slate-800/10 text-[9px] font-bold text-red-900/40 italic uppercase">Required Data Missing: ${item.missingFields?.join(', ')}</div>` : ''}
            </div>
        </div>
    `;
}

function bindEvents(container) {
    const debugTrigger = document.getElementById('hotfix-debug-trigger');
    if (debugTrigger) {
        debugTrigger.onclick = () => {
            const panel = document.getElementById('hotfix-debug-panel');
            if (panel) panel.classList.toggle('hidden');
        };
    }

    container.querySelectorAll('.expand-trigger').forEach(btn => {
        btn.onclick = () => {
            const idx = btn.dataset.idx;
            const target = container.querySelector(`#detail-${idx}`);
            target.classList.toggle('hidden');
            const icon = btn.querySelector('.icon');
            if (icon) icon.innerText = target.classList.contains('hidden') ? '▼' : '▲';
        };
    });
}
