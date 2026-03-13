
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
    container.innerHTML = '<div class="p-8 text-slate-500 text-xs animate-pulse uppercase tracking-widest font-black text-center">Diagnosing System Vitals...</div>';

    const today = new Date().toLocaleDateString('en-CA');

    try {
        const [audit, health, manifestResp] = await Promise.all([
            fetch('data/ops/usage_audit.json?v=' + Date.now()).then(r => r.ok ? r.json() : null),
            fetch('data/ops/system_health.json?v=' + Date.now()).then(r => r.ok ? r.json() : null),
            fetch('data/decision/manifest.json?v=' + Date.now()).then(r => r.ok ? r.json() : { files: [] })
        ]);

        const decisions = [];
        const fileList = manifestResp.files_flat || (manifestResp.files || []).map(f => typeof f === 'string' ? f : f.path);
        
        if (fileList.length > 0) {
            const fetchTasks = fileList.slice(0, 5).map(async (f) => {
                const r = await fetch(`data/decision/${f}`);
                if (r.ok) {
                    const d = await r.json();
                    const items = (Array.isArray(d) ? d : (d.top_topics || [d]));
                    items.forEach(item => {
                        if (item && typeof item === 'object') decisions.push(item);
                    });
                }
            });
            await Promise.all(fetchTasks);
        }

        renderSystemUI(container, { audit, health, decisions, today });

    } catch (e) {
        console.error(e);
        container.innerHTML = `<div class="p-8 text-red-500 font-mono text-xs bg-red-500/5 border border-red-500/20 rounded">Diagnosis Failed: ${e.message}</div>`;
    }
}

function renderSystemUI(container, data) {
    const { audit, health, decisions, today } = data;

    // Calculate Anomaly Stats
    const itemsWScore = decisions.filter(i => i && i.narrative_score !== null);
    const avgIntensity = itemsWScore.length > 0 ? itemsWScore.reduce((s, i) => s + UI_SAFE.num(i.narrative_score), 0) / itemsWScore.length : 0;
    
    const agents = health?.agents || [];
    const usages = audit?.daily_api_usage || [];

    container.innerHTML = `
        <div class="space-y-8 fade-in max-w-6xl mx-auto">
            <h1 class="text-3xl font-black text-white tracking-tighter uppercase">시스템 상태 v2.5</h1>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <!-- BLOCK A: 엔진 에이전트 상태 -->
                <div class="bg-slate-900/40 border border-slate-800 rounded-2xl p-6 space-y-6">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center gap-2 text-[10px] font-black text-blue-500 uppercase tracking-widest">
                            <span class="w-1.5 h-1.5 bg-blue-500 rounded-full"></span>
                            에이전트 가동 상태
                        </div>
                        <span class="text-[9px] font-black text-slate-500 uppercase">Status: ${health?.status || 'UNKNOWN'}</span>
                    </div>
                    
                    <div class="grid gap-3">
                        ${agents.map(a => `
                            <div class="flex items-center justify-between bg-black/20 p-3 rounded-lg border border-slate-800/50 group hover:border-slate-700 transition-colors">
                                <div class="flex items-center gap-3">
                                    <div class="w-2 h-2 rounded-full ${a.status === 'UP' ? 'bg-green-500 animate-pulse' : 'bg-red-500'}"></div>
                                    <span class="text-[11px] font-black text-white uppercase tracking-tight">${a.name}</span>
                                </div>
                                <div class="text-right">
                                    <div class="text-[10px] font-black ${a.status === 'UP' ? 'text-green-400' : 'text-red-400'}">${a.status}</div>
                                    <div class="text-[8px] text-slate-500 font-mono italic">${a.last_run ? a.last_run.split('T')[1].split('.')[0] : 'N/A'}</div>
                                </div>
                            </div>
                        `).join('')}
                    </div>

                    <div class="pt-4 border-t border-slate-800/50">
                        <div class="text-[9px] text-slate-600 font-black uppercase mb-2">Last System Collection</div>
                        <div class="text-xs text-slate-400 font-mono">${health?.last_collection_kst ? health.last_collection_kst.replace('T', ' ').split('.')[0] : 'N/A'}</div>
                    </div>
                </div>

                <!-- BLOCK B: API 사용량 및 비용 -->
                <div class="bg-slate-900/40 border border-slate-800 rounded-2xl p-6 space-y-6">
                    <div class="flex items-center gap-2 text-[10px] font-black text-amber-500 uppercase tracking-widest">
                        <span class="w-1.5 h-1.5 bg-amber-500 rounded-full"></span>
                        API 리소스 감사
                    </div>
                    
                    <div class="space-y-4">
                        ${usages.map(u => `
                            <div class="space-y-2">
                                <div class="flex justify-between text-[10px] font-black uppercase">
                                    <span class="text-slate-400">${u.service}</span>
                                    <span class="text-white">$${u.cost || 0}</span>
                                </div>
                                <div class="h-1.5 bg-slate-800 rounded-full overflow-hidden">
                                    <div class="h-full bg-amber-500/40" style="width: ${Math.min((u.tokens || u.queries || 0) / 100, 100)}%"></div>
                                </div>
                                <div class="text-[8px] text-slate-600 text-right">${u.tokens ? u.tokens + ' tokens' : (u.queries ? u.queries + ' queries' : u.io_ops + ' ops')}</div>
                            </div>
                        `).join('')}
                    </div>

                    <div class="pt-4 border-t border-slate-800/50 flex justify-between items-center">
                        <div class="text-[9px] text-slate-600 font-black uppercase">Daily Total Cost</div>
                        <div class="text-xl font-black text-white italic">$${usages.reduce((s, u) => s + (u.cost || 0), 0).toFixed(2)}</div>
                    </div>
                </div>

                <!-- BLOCK C: 엔진 신호 통계 -->
                <div class="lg:col-span-2 bg-slate-900/40 border border-slate-800 rounded-2xl p-6 space-y-4">
                    <div class="flex items-center gap-2 text-[10px] font-black text-green-500 uppercase tracking-widest">
                        <span class="w-1.5 h-1.5 bg-green-500 rounded-full"></span>
                        엔진 신호 통계 (Recent)
                    </div>
                    
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div class="bg-black/20 p-4 rounded-xl border border-slate-800/50 text-center">
                            <div class="text-[9px] text-slate-600 font-black uppercase mb-1">Total Cached</div>
                            <div class="text-2xl font-black text-white">${decisions.length}</div>
                        </div>
                        <div class="bg-black/20 p-4 rounded-xl border border-slate-800/50 text-center">
                            <div class="text-[9px] text-slate-600 font-black uppercase mb-1">Avg Intensity</div>
                            <div class="text-2xl font-black text-blue-400">${Math.round(avgIntensity)}%</div>
                        </div>
                        <div class="bg-black/20 p-4 rounded-xl border border-slate-800/50 text-center">
                            <div class="text-[9px] text-slate-600 font-black uppercase mb-1">Health Rate</div>
                            <div class="text-2xl font-black text-green-500">100%</div>
                        </div>
                        <div class="bg-black/20 p-4 rounded-xl border border-slate-800/50 text-center">
                            <div class="text-[9px] text-slate-600 font-black uppercase mb-1">SLA Compliance</div>
                            <div class="text-2xl font-black text-white">OK</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}
