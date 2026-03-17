/**
 * operator_market_radar.js — Market Change and Timing Analysis
 * Consolidates Early Theme, Evolution, and Momentum telemetry.
 */

export async function initMarketRadarView(container) {
    console.log('[MarketRadar] Initializing...');
    
    try {
        const response = await fetch('data/ops/today_operator_brief.json');
        if (!response.ok) throw new Error('Data brief not found');
        const brief = await response.json();
        const data = brief.market_radar;

        container.innerHTML = `
            <div class="animate-in fade-in slide-in-from-bottom-4 duration-700">
                <header class="flex justify-between items-center mb-10">
                    <div>
                        <h2 class="text-3xl font-black text-white tracking-tight flex items-center gap-3">
                            <span class="text-blue-500 text-4xl">📡</span> Market Radar
                        </h2>
                        <p class="text-slate-500 text-sm font-medium mt-1 uppercase tracking-widest">Theme Detection & Timing Analysis</p>
                    </div>
                </header>

                <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    <!-- 1. Detection Card -->
                    <div class="bg-[#161b22] border border-slate-800 rounded-2xl p-8">
                        <div class="flex justify-between items-start mb-6">
                            <div class="w-12 h-12 bg-blue-500/10 rounded-xl flex items-center justify-center text-2xl">🧭</div>
                            <div class="text-[10px] font-black text-blue-500 bg-blue-500/10 px-2 py-1 rounded uppercase">Detection</div>
                        </div>
                        <h3 class="text-slate-400 text-xs font-black uppercase tracking-widest mb-2">Primary Emerging Theme</h3>
                        <div class="text-2xl font-black text-white mb-4">${data.theme}</div>
                        <div class="flex items-end gap-3">
                            <div class="text-4xl font-black text-blue-500">${(data.early_signal_score * 100).toFixed(0)}%</div>
                            <div class="text-slate-500 text-[10px] font-bold uppercase mb-1.5">Signal Strength</div>
                        </div>
                    </div>

                    <!-- 2. Evolution Card -->
                    <div class="bg-[#161b22] border border-slate-800 rounded-2xl p-8">
                        <div class="flex justify-between items-start mb-6">
                            <div class="w-12 h-12 bg-emerald-500/10 rounded-xl flex items-center justify-center text-2xl">🧬</div>
                            <div class="text-[10px] font-black text-emerald-500 bg-emerald-500/10 px-2 py-1 rounded uppercase">Lifecycle</div>
                        </div>
                        <h3 class="text-slate-400 text-xs font-black uppercase tracking-widest mb-2">Maturity Stage</h3>
                        <div class="text-2xl font-black text-white mb-4">${data.evolution_stage}</div>
                        <div class="px-3 py-1 bg-emerald-500/10 text-emerald-500 text-[10px] font-black rounded uppercase border border-emerald-500/20 inline-block">
                            ${data.evolution_hint}
                        </div>
                    </div>

                    <!-- 3. Momentum Card -->
                    <div class="bg-[#161b22] border border-slate-800 rounded-2xl p-8">
                        <div class="flex justify-between items-start mb-6">
                            <div class="w-12 h-12 bg-amber-500/10 rounded-xl flex items-center justify-center text-2xl">⚡</div>
                            <div class="text-[10px] font-black text-amber-500 bg-amber-500/10 px-2 py-1 rounded uppercase">Velocity</div>
                        </div>
                        <h3 class="text-slate-400 text-xs font-black uppercase tracking-widest mb-2">Momentum State</h3>
                        <div class="text-2xl font-black text-white mb-4">${data.momentum_state}</div>
                        <div class="text-4xl font-black text-amber-500">${(data.momentum_score * 100).toFixed(0)}</div>
                    </div>
                </div>

                <div class="mt-10 p-8 bg-slate-900/50 border border-slate-800 rounded-2xl">
                    <h4 class="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-6 border-b border-slate-800 pb-4">Momentum Drivers</h4>
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        ${data.momentum_drivers.map(d => `
                            <div class="p-4 bg-[#0d1117] border border-slate-800 rounded-xl text-[11px] font-bold text-slate-300">
                                ${d}
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;

    } catch (err) {
        container.innerHTML = `<div class="p-8 text-red-500 bg-red-500/10 rounded-xl border border-red-500/20">Market Radar Data Error: ${err.message}</div>`;
    }
}
