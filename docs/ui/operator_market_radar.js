/**
 * operator_market_radar.js — Market Change and Timing Analysis
 * Consolidates Early Theme, Evolution, and Momentum telemetry with Investment Decisions & Risk.
 */

window.onerror = function(message, source, lineno, colno, error) {
    console.error("UI ERROR:", message);
    return true;
};

function safeNumber(value, digits = 2) {
    if (value === null || value === undefined || isNaN(value)) {
        return "N/A";
    }
    return Number(value).toFixed(digits);
}

function safeText(value) {
    if (!value) return "N/A";
    return value;
}

function safeArray(arr) {
    if (!Array.isArray(arr) || arr.length === 0) {
        return [];
    }
    return arr;
}

export async function initMarketRadarView(container) {
    console.log('[MarketRadar] Initializing...');
    
    try {
        const response = await fetch(`data/ops/today_operator_brief.json?t=${Date.now()}`);
        if (!response.ok) throw new Error('Data brief not found');
        const brief = await response.json();
        
        if (!brief || !brief.market_radar) {
            container.innerHTML = `<div class="p-8 text-slate-500 bg-slate-900/50 rounded-xl border border-slate-800">No Market Radar data available</div>`;
            return;
        }

        const data = brief.market_radar;
        const risk = brief.risk || { risk_level: 'LOW', risk_score: 0.2, invalidation: 'N/A' };

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
                        <div class="text-2xl font-black text-white mb-4">${safeText(data.theme)}</div>
                        <div class="flex items-end gap-3">
                            <div class="text-4xl font-black text-blue-500">${safeNumber((data.early_signal_score || 0) * 100, 0)}%</div>
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
                        <div class="text-2xl font-black text-white mb-4">${safeText(data.evolution_stage)}</div>
                        <div class="px-3 py-1 bg-emerald-500/10 text-emerald-500 text-[10px] font-black rounded uppercase border border-emerald-500/20 inline-block">
                            ${safeText(data.evolution_hint)}
                        </div>
                    </div>

                    <!-- 3. Momentum Card -->
                    <div class="bg-[#161b22] border border-slate-800 rounded-2xl p-8">
                        <div class="flex justify-between items-start mb-6">
                            <div class="w-12 h-12 bg-amber-500/10 rounded-xl flex items-center justify-center text-2xl">⚡</div>
                            <div class="text-[10px] font-black text-amber-500 bg-amber-500/10 px-2 py-1 rounded uppercase">Velocity</div>
                        </div>
                        <h3 class="text-slate-400 text-xs font-black uppercase tracking-widest mb-2">Momentum State</h3>
                        <div class="text-2xl font-black text-white mb-4">${safeText(data.momentum_state)}</div>
                        <div class="text-4xl font-black text-amber-500">${safeNumber((data.momentum_score || 0) * 100, 0)}</div>
                    </div>
                </div>

                <!-- 4. Decision & Risk Row -->
                <div class="mt-8 grid grid-cols-1 lg:grid-cols-5 gap-6">
                    <!-- Investment Action -->
                    <div class="bg-[#1c2128] border border-indigo-500/20 rounded-2xl p-6 relative overflow-hidden shadow-xl shadow-indigo-500/5">
                        <div class="absolute top-0 right-0 p-3 opacity-10 text-3xl">🎯</div>
                        <h3 class="text-slate-500 text-[9px] font-black uppercase tracking-widest mb-3 text-nowrap">Investment Action</h3>
                        <div class="text-2xl font-black ${getActionColorClass(safeText(brief.investment_decision?.action))} mb-1">
                            ${safeText(brief.investment_decision?.action)}
                        </div>
                        <div class="text-[9px] font-bold text-slate-500 uppercase tracking-tighter">Recommended Strategy</div>
                    </div>

                    <!-- Entry Timing -->
                    <div class="bg-[#1c2128] border border-slate-800 rounded-2xl p-6 relative overflow-hidden">
                        <div class="absolute top-0 right-0 p-3 opacity-10 text-3xl">⏱️</div>
                        <h3 class="text-slate-400 text-[9px] font-black uppercase tracking-widest mb-3">Entry Timing</h3>
                        <div class="text-2xl font-black text-white mb-1 uppercase tracking-tighter">
                            ${safeText(brief.investment_decision?.timing)}
                        </div>
                        <div class="text-[9px] font-bold text-slate-500 uppercase tracking-tighter">Phase Alignment</div>
                    </div>

                    <!-- Decision Confidence -->
                    <div class="bg-[#1c2128] border border-slate-800 rounded-2xl p-6 relative overflow-hidden">
                        <div class="absolute top-0 right-0 p-3 opacity-10 text-3xl">🛡️</div>
                        <h3 class="text-slate-400 text-[9px] font-black uppercase tracking-widest mb-3">Confidence</h3>
                        <div class="text-2xl font-black text-blue-400 mb-1">
                            ${safeNumber((brief.investment_decision?.confidence || 0) * 100, 0)}%
                        </div>
                        <div class="text-[9px] font-bold text-slate-500 uppercase tracking-tighter">Weighted Conviction</div>
                    </div>

                    <!-- RISK ASSESSMENT -->
                    <div class="bg-[#1c2128] border ${getRiskBorderClass(safeText(risk.risk_level))} rounded-2xl p-6 relative overflow-hidden">
                        <div class="absolute top-0 right-0 p-3 opacity-10 text-3xl">⚠️</div>
                        <h3 class="text-slate-400 text-[9px] font-black uppercase tracking-widest mb-3">Risk Assessment</h3>
                        <div class="flex items-center gap-3 mb-1">
                            <div class="text-2xl font-black ${getRiskColorClass(safeText(risk.risk_level))}">${safeText(risk.risk_level)}</div>
                            <div class="text-xs font-black text-slate-500 border border-slate-800 px-1.5 rounded">${safeNumber(risk.risk_score, 2)}</div>
                        </div>
                        <div class="text-[9px] font-bold text-slate-400 uppercase tracking-tight">
                            <span class="text-slate-600 font-black">INV:</span> ${safeText(risk.invalidation)}
                        </div>
                    </div>

                    <!-- TOTAL EXPOSURE -->
                    <div class="bg-[#1c2128] border border-blue-500/20 rounded-2xl p-6 relative overflow-hidden shadow-lg shadow-blue-500/5">
                        <div class="absolute top-0 right-0 p-3 opacity-10 text-3xl">💹</div>
                        <h3 class="text-slate-400 text-[9px] font-black uppercase tracking-widest mb-3">Total Exposure</h3>
                        <div class="text-2xl font-black text-blue-500 mb-1">
                            ${safeNumber((brief.portfolio_allocation?.theme_exposure || 0) * 100, 1)}%
                        </div>
                        <div class="text-[9px] font-bold text-slate-500 uppercase tracking-tighter italic">Risk-Weighted Allocation</div>
                    </div>
                </div>

                <div class="mt-8 p-6 bg-slate-900/50 border border-slate-800 rounded-2xl">
                    <h4 class="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-4 border-b border-slate-800 pb-3 font-mono">Momentum Drivers</h4>
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
                        ${safeArray(data.momentum_drivers).length === 0 ? '<div class="text-[10px] text-slate-600 italic uppercase">No momentum data available</div>' : safeArray(data.momentum_drivers).map(d => `
                            <div class="p-3 bg-[#0d1117] border border-slate-800 rounded-xl text-[10px] font-bold text-slate-400 flex items-center gap-2">
                                <span class="w-1 h-1 bg-amber-500 rounded-full"></span> ${safeText(d)}
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

function getActionColorClass(action) {
    const mapping = {
        'WATCH': 'text-slate-500',
        'EARLY_ENTRY': 'text-blue-500',
        'ACCUMULATE': 'text-emerald-500',
        'HOLD': 'text-amber-500',
        'DISTRIBUTE': 'text-orange-500',
        'EXIT': 'text-red-500'
    };
    return mapping[action] || 'text-slate-400';
}

function getRiskColorClass(level) {
    const mapping = {
        'LOW': 'text-emerald-500',
        'MEDIUM': 'text-amber-500',
        'HIGH': 'text-red-500'
    };
    return mapping[level] || 'text-slate-400';
}

function getRiskBorderClass(level) {
    const mapping = {
        'LOW': 'border-emerald-500/20',
        'MEDIUM': 'border-amber-500/30',
        'HIGH': 'border-red-500/40'
    };
    return mapping[level] || 'border-slate-800';
}
