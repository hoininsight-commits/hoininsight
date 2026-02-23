
/**
 * Operator History View v2.7 — DECISION CARD SCHEMA ADAPTER
 * Features: Tabbed Interface (Complete vs Incomplete), Daily Trend Intelligence,
 *           Decision Card schema support via extractDecisions
 */

import { UI_SAFE, normalizeDecision, assertNoUndefined, extractDecisions } from './utils.js?v=2.4';

export async function initHistoryView(container) {
    container.innerHTML = `
        <div id="debug-error-banner" class="hidden fixed top-0 left-0 w-full bg-red-600 text-white font-black text-[10px] p-2 z-[100] text-center shadow-xl animate-bounce"></div>
        <div class="p-8 text-slate-500 text-xs animate-pulse uppercase tracking-widest font-black text-center">
            Consolidating History Intelligence v2.6...
        </div>
    `;

    try {
        const manifestResp = await fetch('data/decision/manifest.json?v=' + Date.now());
        if (!manifestResp.ok) throw new Error("Manifest Missing");
        const manifest = await manifestResp.json();

        const allDecisions = [];
        // v2.5 manifest uses files_flat (string[]); old format uses files[] as strings
        const fileList = manifest.files_flat
            || (manifest.files || []).map(f => typeof f === 'string' ? f : f.path);
        const fetchTasks = fileList.map(async (file) => {
            try {
                const res = await fetch(`data/decision/${file}?v=${Date.now()}`);
                if (!res.ok) return;
                const data = await res.json();

                // ADAPTER: handles Decision Card / array / legacy / non-decision (skip empty)
                const rawItems = extractDecisions(data);
                if (rawItems.length === 0) return;

                rawItems.forEach(item => {
                    const norm = item._source === 'decision_card'
                        ? { ...item }              // already converted by adapter
                        : normalizeDecision(item); // legacy item
                    allDecisions.push({ ...norm, _file: file });
                });
            } catch (e) { console.warn(`Skip ${file}`, e); }
        });

        await Promise.all(fetchTasks);

        const state = {
            data: allDecisions,
            activeTab: 'complete', // 'complete' or 'incomplete' (v2.6)
            filters: { type: 'All', intensity: 0 }
        };

        renderHistoryFrame(container, state);

    } catch (e) {
        container.innerHTML = `<div class="p-8 text-red-500 font-mono text-xs bg-red-500/5 border border-red-500/20 rounded">History Initialization Failed: ${UI_SAFE.safeStr(e.message)}</div>`;
    }
}

function renderHistoryFrame(container, state) {
    container.innerHTML = `
        <div id="debug-error-banner" class="hidden fixed top-0 left-0 w-full bg-red-600 text-white font-black text-[10px] p-2 z-[100] text-center shadow-xl animate-bounce"></div>
        <div class="space-y-6 fade-in max-w-6xl mx-auto">
            <!-- Header & Tabs (v2.6) -->
            <div class="flex flex-col md:flex-row justify-between items-center md:items-end gap-6 mb-4">
                <div class="space-y-4">
                    <h1 class="text-3xl font-black text-white tracking-tighter uppercase blur-[0.1px]">선정 히스토리 v2.6</h1>
                    <div class="flex bg-slate-900/50 p-1 rounded-lg border border-slate-800 w-fit">
                        <button id="tab-complete" class="px-6 py-1.5 text-[10px] font-black uppercase rounded transition-all ${state.activeTab === 'complete' ? 'bg-blue-600 text-white shadow-lg' : 'text-slate-500 hover:text-slate-300'}">완전 신호</button>
                        <button id="tab-incomplete" class="px-6 py-1.5 text-[10px] font-black uppercase rounded transition-all ${state.activeTab === 'incomplete' ? 'bg-red-900/40 text-red-400 shadow-lg' : 'text-slate-600 hover:text-slate-400'}">보완 필요 신호</button>
                    </div>
                </div>

                <div class="flex flex-wrap gap-2 items-center">
                    <select id="filter-type" class="bg-slate-900 border border-slate-800 text-slate-400 text-[10px] font-black px-3 py-1.5 rounded outline-none appearance-none hover:border-slate-600 transition-colors">
                        <option value="All">All Types</option>
                        <option value="Schedule">Schedule</option>
                        <option value="State">State</option>
                        <option value="Hybrid">Hybrid</option>
                    </select>
                    <select id="filter-int" class="bg-slate-900 border border-slate-800 text-slate-400 text-[10px] font-black px-3 py-1.5 rounded outline-none appearance-none hover:border-slate-600 transition-colors">
                        <option value="0">Int >= 0%</option>
                        <option value="50">Int >= 50%</option>
                        <option value="80">Int >= 80%</option>
                    </select>
                </div>
            </div>

            <div id="history-list-container" class="space-y-10"></div>
        </div>
    `;

    const update = () => {
        state.filters.type = document.getElementById('filter-type').value;
        state.filters.intensity = parseInt(document.getElementById('filter-int').value);
        renderHistoryList(document.getElementById('history-list-container'), state);
        assertNoUndefined(container.innerHTML);
    };

    document.getElementById('tab-complete').onclick = () => { state.activeTab = 'complete'; renderHistoryFrame(container, state); };
    document.getElementById('tab-incomplete').onclick = () => { state.activeTab = 'incomplete'; renderHistoryFrame(container, state); };

    document.getElementById('filter-type').onchange = update;
    document.getElementById('filter-int').onchange = update;

    update();
}

/**
 * PHASE 2-5 Intelligence Calculations (v2.7)
 */
function calculateIntelligence(data) {
    const today = new Date();
    const sevenDaysAgo = new Date(today);
    sevenDaysAgo.setDate(today.getDate() - 7);

    // Filter last 7 calendar days
    const recentItems = data.filter(item => {
        const d = new Date(item.date);
        return d >= sevenDaysAgo && d <= today;
    });

    if (recentItems.length === 0) return null;

    const totalCount = recentItems.length;
    const completeItems = recentItems.filter(i => !i.incomplete);
    const avgInt = Math.round(recentItems.reduce((s, i) => s + i.intensity, 0) / totalCount);
    const maxInt = Math.max(...recentItems.map(i => i.intensity));
    const compRatio = Math.round((completeItems.length / totalCount) * 100);

    const topSignal = [...completeItems].sort((a, b) => b.intensity - a.intensity)[0] || null;

    // Daily averages for Sparkline
    const dailyMap = recentItems.reduce((acc, item) => {
        if (!acc[item.date]) acc[item.date] = [];
        acc[item.date].push(item.intensity);
        return acc;
    }, {});

    const dates = Object.keys(dailyMap).sort();
    const sparkPoints = dates.map(d => {
        const vals = dailyMap[d];
        return Math.round(vals.reduce((s, v) => s + v, 0) / vals.length);
    });

    return { avgInt, maxInt, compRatio, totalCount, topSignal, sparkPoints };
}

function renderSparkline(points) {
    if (!points || points.length < 2) return '';
    const width = 120;
    const height = 30;
    const padding = 2;
    const max = 100;

    const step = (width - padding * 2) / (points.length - 1);
    const coords = points.map((p, i) => {
        const x = padding + i * step;
        const y = height - (p / max * height);
        return `${x},${y}`;
    }).join(' ');

    return `
        <svg width="${width}" height="${height}" class="overflow-visible">
            <polyline points="${coords}" fill="none" stroke="#3b82f6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
            ${points.map((p, i) => `
                <circle cx="${padding + i * step}" cy="${height - (p / max * height)}" r="3" fill="#3b82f6" class="hover:r-4 hover:fill-blue-400 cursor-help transition-all">
                    <title>Avg Intensity: ${p}%</title>
                </circle>
            `).join('')}
        </svg>
    `;
}

function renderHistoryList(container, state) {
    const isCompView = state.activeTab === 'complete';

    // Global Sorting & Filtering (v2.6 Unified)
    const filtered = state.data.filter(item => {
        // Use data_incomplete (set by adapter) OR the legacy `incomplete` flag
        const isIncomplete = item.data_incomplete || item.incomplete || false;
        if (isCompView && isIncomplete) return false;
        if (!isCompView && !isIncomplete) return false;

        const typeMatch = state.filters.type === 'All' || item.why_now_type === state.filters.type;
        const intMatch = item.intensity >= state.filters.intensity;
        return typeMatch && intMatch;
    });

    const getRank = (item) => {
        if (item.incomplete) return 1;
        if (item.speakability === 'OK') return 4;
        if (item.speakability === 'HOLD') return 3;
        return 2;
    };

    // Grouping
    const grouped = filtered.reduce((acc, item) => {
        const date = item.date;
        if (!acc[date]) acc[date] = [];
        acc[date].push(item);
        return acc;
    }, {});

    const sortedDates = Object.keys(grouped).sort((a, b) => new Date(b) - new Date(a));

    const intel = calculateIntelligence(state.data);
    const intelHtml = (intel && isCompView) ? `
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <div class="bg-blue-900/10 border border-blue-900/20 p-5 rounded-2xl flex items-center justify-between group hover:border-blue-500/30 transition-all">
                <div class="space-y-1">
                    <div class="text-[9px] font-black text-blue-500 uppercase tracking-widest">최근 7일 요약</div>
                    <div class="flex items-baseline gap-2">
                        <span class="text-2xl font-black text-white italic">${intel.avgInt}%</span>
                        <span class="text-[10px] text-slate-500 font-bold uppercase">Average Int</span>
                    </div>
                    <div class="text-[10px] text-slate-400 font-medium">최고 ${intel.maxInt}% | 완전율 ${intel.compRatio}% | 총 ${intel.totalCount}건</div>
                </div>
                <div class="opacity-80 group-hover:opacity-100 transition-opacity">
                    ${renderSparkline(intel.sparkPoints)}
                </div>
            </div>

            ${intel.topSignal ? `
                <div class="md:col-span-2 bg-slate-900/40 border border-slate-800 p-5 rounded-2xl flex flex-col justify-center relative overflow-hidden group hover:border-slate-600 transition-all">
                    <div class="absolute -right-4 -top-4 text-6xl opacity-5 grayscale group-hover:grayscale-0 transition-all">🏆</div>
                    <div class="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-1">최근 7일 최고 강도 신호</div>
                    <div class="flex items-center gap-3">
                        <span class="bg-red-500/10 text-red-500 text-[10px] font-black px-2 py-0.5 rounded border border-red-500/20">${intel.topSignal.intensity}%</span>
                        <h4 class="text-sm font-bold text-slate-200 truncate">${intel.topSignal.title}</h4>
                        <span class="text-[10px] text-slate-500 font-mono ml-auto">${intel.topSignal.date}</span>
                    </div>
                    <p class="text-[10px] text-slate-400 mt-2 truncate max-w-2xl">${intel.topSignal.why_now_summary}</p>
                </div>
            ` : ''}
        </div>
    ` : '';

    const infoHtml = !isCompView ? `
        <div class="bg-blue-900/10 border border-blue-500/20 p-4 rounded-xl mb-6 flex items-start gap-3 animate-in fade-in slide-in-from-top-2">
            <span class="text-blue-500 text-sm">ℹ️</span>
            <p class="text-[10.5px] text-slate-400 leading-relaxed font-medium">
                보완 필요 신호는 자동 선정 조건을 충족하지 못한 기록입니다.<br/>
                엔진 선정 대상(HERO/Main)에는 포함되지 않으며, 데이터 보완 후 재검토가 권장됩니다.
            </p>
        </div>
    ` : '';

    if (sortedDates.length === 0) {
        container.innerHTML = intelHtml + infoHtml + `
            <div class="p-20 border border-dashed border-slate-800 rounded-2xl text-center space-y-2">
                <div class="text-3xl grayscale opacity-10">📂</div>
                <div class="text-slate-700 font-black uppercase tracking-[0.2em] text-[10px]">No records found for ${state.activeTab}</div>
            </div>`;
        return;
    }

    container.innerHTML = intelHtml + infoHtml + sortedDates.map((date, idx) => {
        const dayItems = grouped[date];

        // Daily Delta (v2.7)
        let deltaHtml = '';
        if (idx < sortedDates.length - 1) {
            const nextDate = sortedDates[idx + 1];
            const nextDayItems = grouped[nextDate];
            if (nextDayItems) {
                const curAvg = Math.round(dayItems.reduce((s, i) => s + i.intensity, 0) / dayItems.length);
                const prevAvg = Math.round(nextDayItems.reduce((s, i) => s + i.intensity, 0) / nextDayItems.length);
                const delta = curAvg - prevAvg;
                if (delta > 0) deltaHtml = `<span class="text-green-500 ml-2">↑ +${delta}%</span>`;
                else if (delta < 0) deltaHtml = `<span class="text-red-500 ml-2">↓ ${delta}%</span>`;
            }
        }

        // PHASE 3: DAILY TREND SUMMARY (v2.6)
        const d_ok = dayItems.filter(i => !i.incomplete && i.speakability === 'OK').length;
        const d_hold = dayItems.filter(i => !i.incomplete && i.speakability === 'HOLD').length;
        const d_inc = dayItems.filter(i => i.incomplete).length;
        const d_avg = Math.round(dayItems.reduce((s, i) => s + i.intensity, 0) / dayItems.length);
        const d_max = Math.max(...dayItems.map(i => i.intensity));

        const trendHtml = isCompView ? `
            <div class="flex items-center gap-3 bg-slate-900/30 px-3 py-1 rounded-full border border-slate-800/50">
                <span class="text-[9px] text-slate-500 font-bold">완전 <strong class="text-slate-300 font-black">${dayItems.length}</strong></span>
                <span class="text-[9px] text-slate-500 font-bold">평균 <strong class="text-slate-300 font-black">${d_avg}%</strong>${deltaHtml}</span>
                <span class="text-[9px] text-slate-500 font-bold">최고 <strong class="text-red-500 font-black">${d_max}%</strong></span>
            </div>
        ` : `
            <div class="flex items-center gap-3 bg-red-950/10 px-3 py-1 rounded-full border border-red-900/10">
                <span class="text-[9px] text-red-900/60 font-black italic">보완 필요 ${dayItems.length}건</span>
            </div>
        `;

        return `
            <div class="space-y-4">
                <div class="flex justify-between items-center transition-opacity hover:opacity-100 opacity-90 px-1">
                    <h2 class="text-[11px] font-black text-slate-400 uppercase tracking-[0.5em] flex items-center gap-4 flex-1">
                        <span>${date}</span>
                        <div class="h-[1px] bg-slate-800/80 flex-1"></div>
                    </h2>
                    <div class="ml-6">${trendHtml}</div>
                </div>
                
                <div class="grid gap-1.5">
                    ${dayItems.sort((a, b) => {
            const rA = getRank(a);
            const rB = getRank(b);
            if (rA !== rB) return rB - rA;
            if (b.intensity !== a.intensity) return b.intensity - a.intensity;
            return new Date(b.selected_at || 0) - new Date(a.selected_at || 0);
        }).map((item, idx) => renderHistoryCardSnippet(item, `${date}-${idx}`)).join('')}
                </div>
            </div>
        `;
    }).join('');

    bindHistoryEvents(container);
}

function renderHistoryCardSnippet(item, id) {
    // PHASE 4: Visual Refinement (v2.6)
    const isInc = item.incomplete;
    const opacity = isInc ? 'opacity-80 grayscale-[0.2]' : '';
    const border = isInc ? 'border-l-[3px] border-slate-700/50 border-slate-800' : 'border-l-[3px] border-blue-600/60 border-slate-800/60';
    const accent = isInc ? '' : (item.intensity >= 70 ? 'bg-red-500/10' : (item.intensity >= 40 ? 'bg-orange-500/5' : 'bg-blue-500/5'));

    return `
        <div class="bg-slate-900/40 border-slate-800 hover:border-slate-500 transition-all group ${border} ${accent} ${opacity}">
            <div class="p-3 flex items-center gap-4 text-xs cursor-pointer expand-trigger" data-id="${id}">
                <span class="text-slate-600 font-black w-10 text-[9.5px] uppercase">${UI_SAFE.safeISOTime(item.selected_at)}</span>
                <span class="${isInc ? 'text-slate-500 italic' : 'text-slate-200 font-bold'} flex-1 truncate text-[12.5px] tracking-tight">
                    ${item.title}
                </span>
                <div class="flex gap-2 items-center">
                    <span class="text-[8.5px] font-black px-1.5 py-0.5 rounded border border-slate-800 text-slate-600 uppercase ${isInc ? 'hidden' : ''}">${item.display_badge}</span>
                    <span class="text-[8.5px] font-black text-slate-500 uppercase">INT ${item.intensity}%</span>
                    <span class="text-[8.5px] font-black px-1.5 py-0.5 rounded border border-slate-800 ${item.speakability === 'OK' ? 'text-green-600' : 'text-yellow-600'} uppercase">${item.speakability}</span>
                    ${isInc ? '<span class="text-[8px] font-black bg-red-900/20 text-red-900/60 px-1 rounded">● 불완전</span>' : ''}
                </div>
                <div class="icon text-[9px] text-slate-800 group-hover:text-slate-600 ml-2">▼</div>
            </div>

            <div id="detail-${id}" class="hidden p-5 pt-0 border-t border-slate-800/10 bg-black/10 text-[11px] text-slate-400 space-y-4 fade-in">
                <div class="pt-4 grid grid-cols-2 gap-10">
                    <div class="space-y-2">
                        <div class="text-[8.5px] font-black text-blue-500 uppercase tracking-widest">Decision Narrative</div>
                        <p class="leading-relaxed font-medium text-slate-300 italic">"${item.why_now_summary}"</p>
                    </div>
                    <div class="space-y-2">
                        <div class="text-[8.5px] font-black text-green-600 uppercase tracking-widest">Validated Signals</div>
                        <ul class="space-y-1.5 list-none pl-1 text-[10.5px]">
                            ${item.anomaly_points.map(pt => `<li class="flex gap-2 text-slate-500 italic"><span>•</span> ${UI_SAFE.safeStr(pt)}</li>`).join('')}
                        </ul>
                    </div>
                </div>
                <div class="pt-3 flex justify-between items-center border-t border-slate-800/10">
                    <div class="flex gap-1.5">
                        ${item.related_assets.map(a => `<span class="bg-slate-800/40 px-2.5 py-0.5 rounded text-[8px] text-slate-600 border border-slate-800/30 uppercase font-black">${a}</span>`).join('')}
                    </div>
                    <div class="text-[8.5px] text-slate-700 font-mono uppercase tracking-tighter">NODE_ID: ${item._file}</div>
                </div>
            </div>
        </div>
    `;
}

function bindHistoryEvents(container) {
    container.querySelectorAll('.expand-trigger').forEach(btn => {
        btn.onclick = () => {
            const target = container.querySelector(`#detail-${btn.dataset.id}`);
            target.classList.toggle('hidden');
            const icon = btn.querySelector('.icon');
            if (icon) icon.innerText = target.classList.contains('hidden') ? '▼' : '▲';
        };
    });
}
