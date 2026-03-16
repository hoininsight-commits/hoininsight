/**
 * STEP-33 Market Prediction Benchmark View
 * Visualizes Liquidity, Macro Regime, Risk, and Structural Shifts.
 */
import { fetchJSON } from './utils.js?v=30';

export async function initMarketStateView(container) {
    console.log("[MarketStateView] Initializing...");
    if (!container) container = document.getElementById('main-content') || document.getElementById('app');
    if (!container) return;
    container.innerHTML = `<div class="p-8 text-slate-400 animate-pulse">Calculating Market Prediction Benchmarks...</div>`;

    try {
        const benchmark = await fetchJSON('data/ops/market_prediction_benchmark.json');

        if (!benchmark) {
            renderError(container, "Market Benchmark data not available. Ensure the prediction engine has been executed.");
            return;
        }

        renderMarketState(container, benchmark);
    } catch (e) {
        console.error("[MarketStateView] Error:", e);
        renderError(container, "Failed to load market prediction benchmark.");
    }
}

function renderMarketState(container, data) {
    const { liquidity, macro_regime, risk, structural_shift, benchmark_summary } = data;

    container.innerHTML = `
        <div class="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <!-- HEADER -->
            <div class="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-slate-800 pb-6">
                <div>
                    <h1 class="text-3xl font-black text-white tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-500">
                        Market Prediction Benchmark
                    </h1>
                    <p class="text-slate-400 text-sm mt-1">Core baseline metrics identifying the primary market environment for narrative intelligence.</p>
                </div>
                <div class="bg-slate-900 border border-slate-700 px-4 py-2 rounded-xl">
                    <span class="text-[10px] font-black uppercase text-slate-500 block">Current Market State</span>
                    <span class="text-lg font-black text-emerald-400 uppercase tracking-tight">${benchmark_summary.market_state}</span>
                </div>
            </div>

            <!-- MAIN GRID -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <!-- Liquidity Card -->
                ${renderStateCard("Liquidity State", liquidity, "blue")}
                <!-- Macro Regime Card -->
                ${renderRegimeCard("Macro Regime", macro_regime)}
                <!-- Risk Stance Card -->
                ${renderStateCard("Risk Stance", risk, "rose")}
                <!-- Structural Shift Card -->
                ${renderStructuralCard(structural_shift)}
            </div>

            <!-- DETAILED SUMMARY BOX -->
            <div class="bg-slate-900 border border-slate-800 rounded-2xl p-8">
                <h3 class="text-sm font-black text-slate-500 uppercase tracking-widest mb-4">Strategic Focus Benchmarks</h3>
                <div class="flex flex-wrap gap-3">
                    ${benchmark_summary.focus.map(f => `
                        <span class="px-4 py-2 bg-slate-800 border border-slate-700 rounded-full text-xs font-bold text-slate-300">
                            ${f}
                        </span>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
}

function renderStateCard(title, data, color) {
    const colorClass = color === 'blue' ? 'text-blue-400 border-blue-500/30' : 'text-rose-400 border-rose-500/30';
    const bgClass = color === 'blue' ? 'bg-blue-500/5' : 'bg-rose-500/5';
    
    return `
        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 hover:border-slate-700 transition-all">
            <div class="flex justify-between items-start mb-6">
                <h3 class="text-sm font-black text-slate-500 uppercase tracking-widest">${title}</h3>
                <div class="flex flex-col items-end">
                    <span class="text-2xl font-black ${colorClass}">${data.score}</span>
                    <span class="text-[8px] font-black uppercase text-slate-600">Intensity Score</span>
                </div>
            </div>
            
            <div class="mb-4">
                <span class="px-3 py-1 rounded-full text-xs font-black border ${colorClass} ${bgClass}">
                    ${data.state}
                </span>
            </div>
            
            <p class="text-sm text-slate-300 font-medium mb-6">${data.summary}</p>
            
            <div class="space-y-2">
                ${data.drivers.map(d => `
                    <div class="flex items-center gap-2 text-[11px] text-slate-500 font-bold uppercase tracking-tight">
                        <div class="w-1.5 h-1.5 rounded-full ${color === 'blue' ? 'bg-blue-500' : 'bg-rose-500'}"></div>
                        ${d}
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

function renderRegimeCard(title, data) {
    return `
        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 hover:border-slate-700 transition-all">
            <div class="flex justify-between items-start mb-6">
                <h3 class="text-sm font-black text-slate-500 uppercase tracking-widest">${title}</h3>
                <div class="flex flex-col items-end">
                    <span class="text-2xl font-black text-emerald-400">${Math.round(data.confidence * 100)}%</span>
                    <span class="text-[8px] font-black uppercase text-slate-600">Model Confidence</span>
                </div>
            </div>
            
            <div class="mb-4">
                <span class="px-3 py-1 rounded-full text-xs font-black border text-emerald-400 border-emerald-500/30 bg-emerald-500/5">
                    ${data.regime}
                </span>
            </div>
            
            <p class="text-sm text-slate-300 font-medium mb-6">${data.summary}</p>
            
            <div class="space-y-2">
                ${data.drivers.map(d => `
                    <div class="flex items-center gap-2 text-[11px] text-slate-500 font-bold uppercase tracking-tight">
                        <div class="w-1.5 h-1.5 rounded-full bg-emerald-500"></div>
                        ${d}
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

function renderStructuralCard(data) {
    return `
        <div class="md:col-span-2 bg-slate-900 border border-slate-800 rounded-2xl p-6 hover:border-slate-700 transition-all">
            <h3 class="text-sm font-black text-slate-500 uppercase tracking-widest mb-6">Active Structural Shifts</h3>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                ${data.active_shifts.map(shift => `
                    <div class="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
                        <div class="flex justify-between items-center mb-2">
                            <h4 class="text-md font-bold text-white uppercase tracking-tight">${shift.theme}</h4>
                            <span class="text-[10px] font-black px-2 py-0.5 rounded border ${shift.intensity === 'HIGH' ? 'text-rose-400 border-rose-500/50' : 'text-orange-400 border-orange-500/50'}">${shift.intensity} INTENSITY</span>
                        </div>
                        <p class="text-xs text-slate-400 mb-3">${shift.summary}</p>
                        <div class="flex flex-wrap gap-2 text-[9px] font-black text-slate-500 uppercase">
                            ${shift.linked_sectors.map(s => `<span class="bg-slate-700 px-2 py-0.5 rounded italic">#${s}</span>`).join('')}
                        </div>
                    </div>
                `).join('')}
            </div>
            <p class="text-xs text-slate-500 mt-6 italic font-bold">Structural Summary: ${data.summary}</p>
        </div>
    `;
}

function renderError(container, msg) {
    container.innerHTML = `
        <div class="min-h-[60vh] flex flex-col items-center justify-center text-center p-8">
            <div class="w-20 h-20 bg-slate-800/50 rounded-full flex items-center justify-center mb-6 text-slate-500 border border-slate-700">
                <svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
            </div>
            <h2 class="text-2xl font-black text-white mb-2 italic tracking-tight">Benchmark Data Quiet</h2>
            <p class="text-slate-500 max-w-md mx-auto text-sm leading-relaxed">${msg}</p>
        </div>
    `;
}
