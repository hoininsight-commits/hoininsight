/**
 * HOIN Insight: Structural Tensions (Contradiction Engine View)
 * STEP-34: Detects structural market contradictions.
 */
import { fetchJSON } from './utils.js?v=30';

export async function initStructuralTensionsView(container) {
    console.log("[StructuralTensionsView] Initializing...");
    if (!container) container = document.getElementById('main-content') || document.getElementById('app');
    if (!container) return;
    container.innerHTML = `<div class="p-8 text-slate-400 animate-pulse">Scanning Structural Contradictions...</div>`;

    try {
        const data = await fetchJSON('data/ops/contradiction_state.json');
        if (!data || !data.contradictions || data.contradictions.length === 0) {
            renderEmptyState(container);
            return;
        }
        renderStructuralTensions(container, data);
    } catch (e) {
        console.error("[StructuralTensionsView] Error:", e);
        renderError(container, "Market contradictions data quiet. Ensure engine PHASE 1.3 is complete.");
    }
}

function renderStructuralTensions(container, data) {
    container.innerHTML = `
        <div class="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <!-- HEADER -->
            <div class="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-slate-800 pb-6">
                <div>
                    <h1 class="text-3xl font-black text-white tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-rose-500">
                        Structural Market Tensions
                    </h1>
                    <p class="text-slate-400 text-sm mt-1">Detecting hidden contradictions and structural frictions in market data.</p>
                </div>
                <div class="bg-slate-900 border border-slate-700 px-4 py-2 rounded-xl">
                    <span class="text-[10px] font-black uppercase text-slate-500 block">System State</span>
                    <span class="text-lg font-black text-orange-400 uppercase tracking-tight">${data.contradictions.length} ACTIVE TENSIONS</span>
                </div>
            </div>

            <!-- TENSION GRID -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                ${data.contradictions.map(c => renderTensionCard(c)).join('')}
            </div>
        </div>
    `;
}

function renderTensionCard(c) {
    const strengthPct = Math.round(c.strength * 100);
    const color = strengthPct > 80 ? 'rose' : (strengthPct > 60 ? 'orange' : 'emerald');
    const colorClass = `text-${color}-400 border-${color}-500/30`;
    const bgClass = `bg-${color}-500/5`;
    const ringClass = `ring-${color}-500/20`;

    return `
        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 hover:border-slate-700 transition-all group relative overflow-hidden">
            <!-- Background Glow -->
            <div class="absolute -right-4 -top-4 w-24 h-24 bg-${color}-500/5 blur-3xl rounded-full group-hover:bg-${color}-500/10 transition-all"></div>
            
            <div class="flex justify-between items-start mb-6">
                <div>
                    <span class="text-[10px] font-black uppercase text-slate-500 tracking-widest block mb-1">${c.type}</span>
                    <h3 class="text-xl font-black text-white uppercase tracking-tight">${c.name}</h3>
                </div>
                <div class="flex flex-col items-end">
                    <span class="text-2xl font-black ${colorClass}">${strengthPct}%</span>
                    <span class="text-[8px] font-black uppercase text-slate-600">Friction Strength</span>
                </div>
            </div>

            <div class="mb-6">
                <div class="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                    <div class="h-full bg-gradient-to-r from-${color}-500 to-${color}-400" style="width: ${strengthPct}%"></div>
                </div>
            </div>
            
            <div class="flex flex-wrap gap-2 mb-6">
                ${c.affected_sectors.map(s => `
                    <span class="px-2 py-1 rounded-md text-[10px] font-black border border-slate-700 bg-slate-800/50 text-slate-400 uppercase">
                        ${s}
                    </span>
                `).join('')}
                <span class="ml-auto px-2 py-1 rounded-md text-[10px] font-black border ${colorClass} ${bgClass} uppercase">
                    ${c.confidence} Confidence
                </span>
            </div>
            
            <div class="bg-slate-950/50 border border-slate-800 rounded-xl p-4">
                <p class="text-[13px] text-slate-300 font-medium leading-relaxed">
                    <span class="text-slate-500 font-black uppercase text-[10px] block mb-1">Engine Analysis</span>
                    ${c.reason}
                </p>
            </div>
        </div>
    `;
}

function renderEmptyState(container) {
    container.innerHTML = `
        <div class="min-h-[60vh] flex flex-col items-center justify-center text-center p-8">
            <div class="w-20 h-20 bg-emerald-500/10 rounded-full flex items-center justify-center mb-6 text-emerald-500 border border-emerald-500/20">
                <i class="fas fa-check-circle text-3xl"></i>
            </div>
            <h2 class="text-2xl font-black text-white mb-2 italic tracking-tight">System Equilibrium</h2>
            <p class="text-slate-500 max-w-md mx-auto text-sm leading-relaxed">
                현재 시장 데이터에서 구조적 모순이 감지되지 않았습니다. 
                모든 지표가 상호 정합적인 방향을 가리키고 있습니다.
            </p>
        </div>
    `;
}

function renderError(container, msg) {
    container.innerHTML = `
        <div class="min-h-[60vh] flex flex-col items-center justify-center text-center p-8">
            <div class="w-20 h-20 bg-slate-800/50 rounded-full flex items-center justify-center mb-6 text-slate-500 border border-slate-700">
                <i class="fas fa-bolt text-3xl"></i>
            </div>
            <h2 class="text-2xl font-black text-white mb-2 italic tracking-tight">Tension Data Quiet</h2>
            <p class="text-slate-500 max-w-md mx-auto text-sm leading-relaxed">${msg}</p>
        </div>
    `;
}
