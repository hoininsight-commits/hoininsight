/**
 * STEP-27 Theme Evolution View
 * Visualizes Narrative Chains, Evolution Stages, and Successors.
 */
import { fetchJSON } from './utils.js';

export async function initEvolutionView() {
    console.log("[EvolutionView] Initializing...");
    const container = document.getElementById('main-content');
    container.innerHTML = `<div class="p-8 text-slate-400 animate-pulse">Tracing Narrative Evolution...</div>`;

    try {
        const evolution = await fetchJSON('data/memory/theme_evolution.json');

        if (!evolution || evolution.length === 0) {
            renderError(container, "No evolution chains detected yet. Requires sequential theme appearances.");
            return;
        }

        renderEvolution(container, evolution);
    } catch (e) {
        console.error("[EvolutionView] Error:", e);
        renderError(container, "Failed to load evolution assets.");
    }
}

function renderEvolution(container, evolution) {
    container.innerHTML = `
        <div class="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <!-- HEADER -->
            <div class="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-slate-800 pb-6">
                <div>
                    <h1 class="text-3xl font-black text-white tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-500">
                        Theme Evolution
                    </h1>
                    <p class="text-slate-400 text-sm mt-1">Predictive mapping of narrative transitions and expansion chains.</p>
                </div>
            </div>

            <!-- TOP EVOLUTION GRID -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                ${evolution.slice(0, 4).map(e => renderEvolutionCard(e)).join('')}
            </div>

            <!-- FULL INVENTORY -->
            <div class="bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden p-6">
                <h2 class="text-lg font-bold text-white mb-6">Narrative Transition Inventory</h2>
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-sm text-slate-400">
                        <thead class="bg-slate-800/50 text-slate-300 text-xs font-black uppercase tracking-wider">
                            <tr>
                                <th class="p-4 font-black">Current Theme</th>
                                <th class="p-4 font-black text-center">Stage</th>
                                <th class="p-4 font-black">Dominant Successor</th>
                                <th class="p-4 font-black">Strength</th>
                                <th class="p-4 font-black text-right">Transitions</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-800">
                            ${evolution.map(e => `
                                <tr class="hover:bg-slate-800/30 transition-colors">
                                    <td class="p-4 font-bold text-white">${e.theme}</td>
                                    <td class="p-4 text-center">
                                        <span class="px-2 py-1 rounded text-[10px] font-black border ${getStageClass(e.current_evolution_stage)}">
                                            ${e.current_evolution_stage}
                                        </span>
                                    </td>
                                    <td class="p-4 text-emerald-400 font-bold">${e.dominant_successor}</td>
                                    <td class="p-4">
                                        <div class="flex items-center gap-2">
                                            <div class="flex-1 bg-slate-800 h-1 rounded-full overflow-hidden min-w-[60px]">
                                                <div class="bg-emerald-500 h-full" style="width: ${(e.successor_themes[0]?.evolution_strength || 0) * 100}%"></div>
                                            </div>
                                            <span class="text-[10px] font-mono text-slate-500">${Math.round((e.successor_themes[0]?.evolution_strength || 0) * 100)}%</span>
                                        </div>
                                    </td>
                                    <td class="p-4 text-right font-mono text-slate-500">${e.total_transitions}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    `;
}

function renderEvolutionCard(e) {
    const stageClass = getStageClass(e.current_evolution_stage);
    return `
        <div class="group bg-slate-900 border border-slate-800 rounded-2xl p-6 hover:border-emerald-500/50 transition-all duration-500">
            <div class="flex justify-between items-start mb-6">
                <div class="flex flex-col">
                    <span class="text-[10px] font-black uppercase tracking-widest text-slate-500 mb-1">Evolution Chain</span>
                    <h3 class="text-xl font-bold text-white group-hover:text-emerald-400 transition-colors">${e.theme}</h3>
                </div>
                <span class="px-2 py-1 rounded text-[10px] font-black border ${stageClass}">
                    ${e.current_evolution_stage}
                </span>
            </div>

            <div class="flex items-center gap-4 mb-6 py-4 bg-slate-800/30 rounded-xl px-4 border border-slate-800/50">
                <div class="flex-1 text-center">
                    <div class="text-[10px] text-slate-500 uppercase font-black mb-1">Current</div>
                    <div class="text-xs text-white truncate font-bold">${e.theme}</div>
                </div>
                <div class="text-emerald-500 animate-pulse">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                    </svg>
                </div>
                <div class="flex-1 text-center">
                    <div class="text-[10px] text-emerald-500 uppercase font-black mb-1">Successor</div>
                    <div class="text-xs text-emerald-400 truncate font-black">${e.dominant_successor}</div>
                </div>
            </div>

            <div class="space-y-3">
                <div class="flex justify-between text-[11px]">
                    <span class="text-slate-500 font-bold uppercase">Transition Potential</span>
                    <span class="text-emerald-500 font-black">${Math.round((e.successor_themes[0]?.evolution_strength || 0) * 100)}%</span>
                </div>
                <div class="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                    <div class="bg-gradient-to-r from-emerald-600 to-cyan-400 h-full transition-all duration-1000" 
                         style="width: ${(e.successor_themes[0]?.evolution_strength || 0) * 100}%"></div>
                </div>
            </div>
        </div>
    `;
}

function getStageClass(stage) {
    switch(stage) {
        case 'ORIGIN': return 'text-blue-400 border-blue-500/50 bg-blue-500/10';
        case 'EXPANDING': return 'text-emerald-400 border-emerald-500/50 bg-emerald-500/10 shadow-[0_0_10px_rgba(16,185,129,0.1)]';
        case 'BRIDGING': return 'text-cyan-400 border-cyan-500/50 bg-cyan-500/10';
        case 'DIVERGING': return 'text-purple-400 border-purple-500/50 bg-purple-500/10';
        case 'SATURATING': return 'text-amber-400 border-amber-500/50 bg-amber-500/10';
        default: return 'text-slate-400 border-slate-500/50 bg-slate-500/10';
    }
}

function renderError(container, msg) {
    container.innerHTML = `
        <div class="min-h-[60vh] flex flex-col items-center justify-center text-center p-8">
            <div class="w-20 h-20 bg-slate-800/50 rounded-full flex items-center justify-center mb-6 text-slate-500 border border-slate-700">
                <svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
            </div>
            <h2 class="text-2xl font-black text-white mb-2 italic tracking-tight">Evolution Analysis Quiet</h2>
            <p class="text-slate-500 max-w-md mx-auto text-sm leading-relaxed">${msg}</p>
        </div>
    `;
}
