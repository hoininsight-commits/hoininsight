/**
 * STEP-26 Narrative Cycle View
 * Visualizes Theme Cycles, Strength, and Recurrence Windows.
 */
import { fetchJSON } from './utils.js';

export async function initCycleView() {
    console.log("[CycleView] Initializing...");
    const container = document.getElementById('main-content');
    container.innerHTML = `<div class="p-8 text-slate-400 animate-pulse">Scanning Narrative Cycles...</div>`;

    try {
        const [cycles] = await Promise.all([
            fetchJSON('data/memory/narrative_cycles.json')
        ]);

        if (!cycles || cycles.length === 0) {
            renderError(container, "No cycle data detected yet. Narrative memory needs more historical depth.");
            return;
        }

        renderCycles(container, cycles);
    } catch (e) {
        console.error("[CycleView] Error:", e);
        renderError(container, "Failed to load cycle assets.");
    }
}

function renderCycles(container, cycles) {
    container.innerHTML = `
        <div class="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <!-- HEADER -->
            <div class="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-slate-800 pb-6">
                <div>
                    <h1 class="text-3xl font-black text-white tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-amber-400 to-orange-600">
                        Narrative Cycles
                    </h1>
                    <p class="text-slate-400 text-sm mt-1">Recurrence intelligence detecting rhythm and tempo of market themes.</p>
                </div>
            </div>

            <!-- TOP RECURRING THEMES GRID -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                ${cycles.slice(0, 6).map(c => renderCycleCard(c)).join('')}
            </div>

            <!-- FULL TABLE -->
            <div class="bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden p-6">
                <h2 class="text-lg font-bold text-white mb-6">Cycle Intelligence Inventory</h2>
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-sm text-slate-400">
                        <thead class="bg-slate-800/50 text-slate-300 text-xs font-black uppercase tracking-wider">
                            <tr>
                                <th class="p-4 font-black">Theme</th>
                                <th class="p-4 font-black text-center">Phase</th>
                                <th class="p-4 font-black">Strength</th>
                                <th class="p-4 font-black">Interval (Avg)</th>
                                <th class="p-4 font-black">Next Expected Window</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-800">
                            ${cycles.map(c => `
                                <tr class="hover:bg-slate-800/30 transition-colors">
                                    <td class="p-4 font-bold text-white">${c.theme}</td>
                                    <td class="p-4 text-center">
                                        <span class="px-2 py-1 rounded text-[10px] font-black border ${getPhaseClass(c.current_cycle_phase)}">
                                            ${c.current_cycle_phase}
                                        </span>
                                    </td>
                                    <td class="p-4">
                                        <div class="flex items-center gap-2">
                                            <div class="flex-1 bg-slate-800 h-1.5 rounded-full overflow-hidden">
                                                <div class="bg-amber-500 h-full" style="width: ${c.cycle_strength * 100}%"></div>
                                            </div>
                                            <span class="text-[10px] font-mono text-amber-500">${Math.round(c.cycle_strength * 100)}%</span>
                                        </div>
                                    </td>
                                    <td class="p-4 text-xs font-mono">${c.avg_interval_days}d <span class="text-slate-600">±${c.interval_std}d</span></td>
                                    <td class="p-4 text-xs font-medium text-slate-300">${c.next_expected_window}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    `;
}

function renderCycleCard(c) {
    const phaseClass = getPhaseClass(c.current_cycle_phase);
    return `
        <div class="group relative bg-slate-900 border border-slate-800 rounded-2xl p-6 hover:border-amber-500/50 transition-all duration-500 overflow-hidden">
            <!-- Decorative Background Signal -->
            <div class="absolute -right-4 -top-4 w-24 h-24 bg-amber-500/5 rounded-full blur-3xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
            
            <div class="flex justify-between items-start mb-4">
                <span class="text-[10px] font-black uppercase tracking-widest text-slate-500">Theme Cycle</span>
                <span class="px-2 py-0.5 rounded text-[8px] font-black border ${phaseClass}">
                    ${c.current_cycle_phase}
                </span>
            </div>
            
            <h3 class="text-xl font-bold text-white mb-2 group-hover:text-amber-400 transition-colors">${c.theme}</h3>
            
            <div class="space-y-4 mt-6">
                <div class="flex justify-between items-end">
                    <span class="text-xs text-slate-500 italic">Cycle Strength</span>
                    <span class="text-lg font-black text-amber-500">${Math.round(c.cycle_strength * 100)}%</span>
                </div>
                <div class="w-full bg-slate-800 h-1 rounded-full overflow-hidden">
                    <div class="bg-gradient-to-r from-amber-600 to-orange-500 h-full" style="width: ${c.cycle_strength * 100}%"></div>
                </div>
                
                <div class="pt-4 border-t border-slate-800">
                    <div class="flex items-center gap-2 mb-1">
                        <span class="text-[10px] text-slate-500 font-bold uppercase">Expected Return</span>
                    </div>
                    <div class="text-sm font-medium text-amber-100">${c.next_expected_window}</div>
                    <div class="text-[10px] text-slate-500 mt-1">Avg Interval: ${c.avg_interval_days} days</div>
                </div>
            </div>
        </div>
    `;
}

function getPhaseClass(phase) {
    switch(phase) {
        case 'REACTIVATION': return 'text-orange-400 border-orange-500/50 bg-orange-500/10 shadow-[0_0_10px_rgba(249,115,22,0.1)]';
        case 'EARLY': return 'text-cyan-400 border-cyan-500/50 bg-cyan-500/10';
        case 'MID': return 'text-blue-400 border-blue-500/50 bg-blue-500/10';
        case 'LATE': return 'text-purple-400 border-purple-500/50 bg-purple-500/10';
        default: return 'text-slate-400 border-slate-500/50 bg-slate-500/10';
    }
}

function renderError(container, msg) {
    container.innerHTML = `
        <div class="min-h-[60vh] flex flex-col items-center justify-center text-center p-8">
            <div class="w-20 h-20 bg-slate-800/50 rounded-full flex items-center justify-center mb-6 text-slate-500 border border-slate-700">
                <svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
            </div>
            <h2 class="text-2xl font-black text-white mb-2 italic tracking-tight">Cycle Detection Quiet</h2>
            <p class="text-slate-500 max-w-md mx-auto text-sm leading-relaxed">${msg}</p>
        </div>
    `;
}
