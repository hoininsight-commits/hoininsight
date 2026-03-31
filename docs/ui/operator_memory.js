/**
 * Operator Memory View v1.0 — NARRATIVE PATTERN VISUALIZER
 * Features: Frequent Topics, Recurring Intervals, Emerging Patterns
 */

export async function initMemoryView(container) {
    container.innerHTML = `
        <div class="p-8 text-slate-500 text-xs animate-pulse uppercase tracking-widest font-black text-center">
            Retrieving Narrative Memory...
        </div>
    `;

    try {
        const resp = await fetch('data/memory/narrative_patterns.json?v=' + Date.now());
        if (!resp.ok) throw new Error("Memory Data Missing");
        const data = await resp.json();
        renderMemoryUI(container, data);
    } catch (e) {
        console.error(e);
        container.innerHTML = `
            <div class="p-8 bg-slate-900/40 border border-slate-800 rounded-2xl text-center">
                <div class="text-3xl mb-4">🧠</div>
                <div class="text-xs font-black text-slate-500 uppercase tracking-widest mb-2">Memory Engine Status: Offline</div>
                <div class="text-[10px] text-slate-600 font-mono italic">No historical patterns detected yet. Core engine must complete at least 2 runs.</div>
            </div>
        `;
    }
}

function renderMemoryUI(container, data) {
    const { frequent_topics = [], recurring_patterns = [], emerging_topics = [], last_updated, total_records } = data;

    container.innerHTML = `
        <div class="space-y-8 fade-in max-w-6xl mx-auto">
            <div class="flex items-center justify-between">
                <h1 class="text-3xl font-black text-white tracking-tighter uppercase">NARRATIVE MEMORY v1.0</h1>
                <div class="text-right">
                    <div class="text-[10px] font-black text-blue-500 uppercase tracking-widest">Index Version: Stable</div>
                    <div class="text-[8px] text-slate-500 font-mono italic">Last Sync: ${last_updated ? last_updated.split('T')[0] : 'N/A'}</div>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <!-- STATS -->
                <div class="bg-blue-600/10 border border-blue-500/20 p-4 rounded-xl text-center">
                    <div class="text-[9px] text-blue-400 font-black uppercase mb-1">Stored Topics</div>
                    <div class="text-2xl font-black text-white">${total_records || 0}</div>
                </div>
                <div class="bg-amber-600/10 border border-amber-500/20 p-4 rounded-xl text-center">
                    <div class="text-[9px] text-amber-400 font-black uppercase mb-1">Active Patterns</div>
                    <div class="text-2xl font-black text-white">${recurring_patterns.length}</div>
                </div>
                <div class="bg-green-600/10 border border-green-500/20 p-4 rounded-xl text-center">
                    <div class="text-[9px] text-green-400 font-black uppercase mb-1">Emerging Trends</div>
                    <div class="text-2xl font-black text-white">${emerging_topics.length}</div>
                </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <!-- RECURRING PATTERNS -->
                <div class="bg-slate-900/40 border border-slate-800 rounded-2xl p-6 space-y-6">
                    <div class="flex items-center gap-2 text-[10px] font-black text-blue-500 uppercase tracking-widest">
                        <span class="w-1.5 h-1.5 bg-blue-500 rounded-full"></span>
                        분석된 주제 주기성 (Recurrence)
                    </div>
                    
                    <div class="space-y-3">
                        ${recurring_patterns.length > 0 ? recurring_patterns.map(p => `
                            <div class="bg-black/20 border border-slate-800/50 p-4 rounded-xl hover:border-slate-700 transition-colors">
                                <div class="flex justify-between items-start mb-2">
                                    <div class="text-xs font-black text-white uppercase">${p.title}</div>
                                    <div class="bg-blue-500/20 text-blue-400 text-[8px] px-1.5 py-0.5 rounded font-black">${p.count} Hits</div>
                                </div>
                                <div class="flex justify-between items-center text-[10px]">
                                    <div class="text-slate-500 uppercase tracking-tighter font-bold">Avg Interval</div>
                                    <div class="text-blue-400 font-black">${p.avg_interval_days} Days</div>
                                </div>
                                <div class="mt-2 text-[8px] text-slate-600 font-mono uppercase">Last Seen: ${p.last_seen}</div>
                            </div>
                        `).join('') : '<div class="text-center py-8 text-[10px] text-slate-600 italic">No patterns detected yet.</div>'}
                    </div>
                </div>

                <!-- TOP FREQUENCY & EMERGING -->
                <div class="space-y-8">
                    <!-- EMERGING -->
                    <div class="bg-slate-900/40 border border-slate-800 rounded-2xl p-6 space-y-4">
                        <div class="text-[10px] font-black text-green-500 uppercase tracking-widest">
                            최근 급상승 주제 (Emerging Trend)
                        </div>
                        <div class="space-y-2">
                            ${emerging_topics.map(t => `
                                <div class="flex items-center justify-between group">
                                    <span class="text-[11px] font-black text-slate-400 group-hover:text-white transition-colors">${t.title}</span>
                                    <div class="h-1 flex-1 mx-4 bg-slate-800 rounded-full overflow-hidden">
                                        <div class="h-full bg-green-500/40" style="width: ${Math.min(t.count * 20, 100)}%"></div>
                                    </div>
                                    <span class="text-[10px] font-mono text-green-500">${t.count}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>

                    <!-- MOST FREQUENT -->
                    <div class="bg-slate-900/40 border border-slate-800 rounded-2xl p-6 space-y-4">
                        <div class="text-[10px] font-black text-amber-500 uppercase tracking-widest">
                            역대 최다 등장 주제 (Historical Winners)
                        </div>
                        <div class="grid grid-cols-1 gap-2">
                             ${frequent_topics.map(t => `
                                <div class="flex justify-between p-2 bg-black/10 rounded border border-slate-800/30">
                                    <span class="text-[10px] font-bold text-slate-500">${t.title}</span>
                                    <span class="text-[10px] font-black text-amber-500">${t.count}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}
