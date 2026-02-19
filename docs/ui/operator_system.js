
/**
 * Operator System Status View v2.2
 * Features: 3 Health Blocks, Real-time Anomaly Stats, Error Logs, Anti-Undefined
 */

const UI_SAFE = {
    get: (val, fallback = "-") => (val === undefined || val === null || val === "" || val === "undefined") ? fallback : val,
    num: (val, fallback = 0) => {
        const n = parseFloat(val);
        return isNaN(n) ? fallback : n;
    }
};

export async function initSystemView(container) {
    container.innerHTML = '<div class="p-8 text-slate-500 text-xs animate-pulse uppercase tracking-widest font-black">Diagnosing System Vitals...</div>';

    const today = new Date().toLocaleDateString('en-CA');

    try {
        const [audit, health, manifestResp] = await Promise.all([
            fetch('data/ops/usage_audit.json').then(r => r.ok ? r.json() : null),
            fetch('data/ops/system_health.json').then(r => r.ok ? r.json() : null),
            fetch('data/decision/manifest.json').then(r => r.ok ? r.json() : { files: [] })
        ]);

        const decisions = [];
        if (manifestResp.files.length > 0) {
            const fetchTasks = manifestResp.files.slice(0, 10).map(async (f) => {
                const r = await fetch(`data/decision/${f}`);
                if (r.ok) {
                    const d = await r.json();
                    (Array.isArray(d) ? d : [d]).forEach(item => decisions.push(item));
                }
            });
            await Promise.all(fetchTasks);
        }

        renderSystemUI(container, { audit, health, decisions, today });

    } catch (e) {
        container.innerHTML = `<div class="p-8 text-red-500 font-mono text-xs bg-red-500/5 border border-red-500/20 rounded">Diagnosis Failed: ${e.message}</div>`;
    }
}

function renderSystemUI(container, data) {
    const { audit, health, decisions, today } = data;

    // Calculate Anomaly Stats (Today)
    const todayItems = decisions.filter(d => UI_SAFE.get(d.date) === today || UI_SAFE.get(d.selected_at).startsWith(today));
    const avgIntensity = todayItems.length > 0 ? todayItems.reduce((s, i) => s + UI_SAFE.num(i.intensity), 0) / todayItems.length : 0;
    const dist = todayItems.reduce((acc, i) => {
        const t = UI_SAFE.get(i.why_now_type);
        acc[t] = (acc[t] || 0) + 1;
        return acc;
    }, {});

    container.innerHTML = `
        <div class="space-y-8 fade-in">
            <h1 class="text-3xl font-black text-white tracking-tighter uppercase">시스템 상태</h1>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <!-- BLOCK A: 데이터 수집 상태 -->
                <div class="bg-slate-900/40 border border-slate-800 rounded-2xl p-6 space-y-4">
                    <div class="flex items-center gap-2 text-[10px] font-black text-blue-500 uppercase tracking-widest">
                        <span class="w-1.5 h-1.5 bg-blue-500 rounded-full"></span>
                        데이터 수집 상태
                    </div>
                    
                    <div class="space-y-3">
                        <div class="flex justify-between items-center bg-black/20 p-3 rounded-lg border border-slate-800/50">
                            <span class="text-xs text-slate-500 font-bold uppercase">Last Collection</span>
                            <span class="text-xs text-slate-300 font-mono">${UI_SAFE.get(audit?.scan_timestamp, "데이터 없음")}</span>
                        </div>
                        <div class="flex justify-between items-center bg-black/20 p-3 rounded-lg border border-slate-800/50">
                            <span class="text-xs text-slate-500 font-bold uppercase">Success Rate</span>
                            <span class="text-xs ${health?.exit_code === 0 ? 'text-green-400' : 'text-red-400'} font-black italic">
                                ${health ? (health.exit_code === 0 ? "100%" : "FAULT DETECTED") : "N/A"}
                            </span>
                        </div>
                        <div class="flex flex-col gap-1">
                            <span class="text-[9px] text-slate-600 font-black uppercase">Source Integrity</span>
                            <div class="flex gap-1">
                                ${["RSS", "K-API", "U-API", "MACRO"].map(s => `
                                    <div class="flex-1 h-1 bg-slate-800 rounded-full overflow-hidden">
                                        <div class="h-full bg-blue-600/50" style="width: 100%"></div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    </div>
                </div>

                <!-- BLOCK B: 이상징후 감지 상태 -->
                <div class="bg-slate-900/40 border border-slate-800 rounded-2xl p-6 space-y-4">
                    <div class="flex items-center gap-2 text-[10px] font-black text-green-500 uppercase tracking-widest">
                        <span class="w-1.5 h-1.5 bg-green-500 rounded-full"></span>
                        이상징후 감지 (Today)
                    </div>
                    
                    <div class="grid grid-cols-2 gap-4">
                        <div class="bg-black/20 p-4 rounded-xl border border-slate-800/50 text-center">
                            <div class="text-[9px] text-slate-600 font-black uppercase mb-1">Total Signals</div>
                            <div class="text-3xl font-black text-white">${todayItems.length}</div>
                        </div>
                        <div class="bg-black/20 p-4 rounded-xl border border-slate-800/50 text-center">
                            <div class="text-[9px] text-slate-600 font-black uppercase mb-1">Avg Intensity</div>
                            <div class="text-3xl font-black text-blue-400">${Math.round(avgIntensity)}%</div>
                        </div>
                    </div>

                    <div class="grid grid-cols-3 gap-2">
                        ${['Schedule', 'State', 'Hybrid'].map(type => `
                            <div class="bg-slate-800/30 p-2 rounded border border-slate-800/50 text-center">
                                <span class="block text-[8px] text-slate-600 font-black uppercase mb-1">${type}</span>
                                <span class="text-xs font-bold text-slate-400">${dist[type] || 0}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>

                <!-- BLOCK C: 최근 에러 로그 -->
                <div class="lg:col-span-2 bg-slate-900/40 border border-slate-800 rounded-2xl p-6 space-y-4">
                    <div class="flex items-center gap-2 text-[10px] font-black text-red-500 uppercase tracking-widest">
                        <span class="w-1.5 h-1.5 bg-red-500 rounded-full animate-pulse"></span>
                        최근 에러 로그
                    </div>
                    
                    <div class="bg-black/40 rounded-xl border border-slate-800 p-4 font-mono text-[10px] space-y-2 max-h-[200px] overflow-y-auto">
                        ${health && health.recent_failures && health.recent_failures.length > 0 ? health.recent_failures.slice(0, 5).map(f => `
                            <div class="flex gap-3 text-red-400/80 bg-red-500/5 p-2 rounded border border-red-500/10">
                                <span class="font-black flex-shrink-0">[FAIL]</span>
                                <span class="flex-1">${UI_SAFE.get(f.message).substring(0, 120)}...</span>
                                <span class="text-slate-600 text-[8px] uppercase font-black">${UI_SAFE.get(f.nodeid).split('::').pop()}</span>
                            </div>
                        `).join('') : `
                            <div class="text-slate-700 italic py-8 text-center uppercase tracking-widest font-black">
                                NO CRITICAL ERRORS LOGGED IN LAST 24H
                            </div>
                        `}
                        <div class="text-slate-600 border-t border-slate-800 pt-2 mt-2">
                            [SYSTEM] Last Sanity Check: ${UI_SAFE.get(health?.last_passed_at, "-")}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}
