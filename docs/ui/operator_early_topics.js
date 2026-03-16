/**
 * STEP-28 Early Topic View
 * Visualizes Emerging Signals, Early Scores, and Evidence Chains.
 */
import { fetchJSON } from './utils.js';

export async function initEarlyView() {
    console.log("[EarlyView] Initializing...");
    const container = document.getElementById('main-content');
    container.innerHTML = `<div class="p-8 text-slate-400 animate-pulse">Scanning for Early Topic Signals...</div>`;

    try {
        const candidates = await fetchJSON('data/ops/early_topic_candidates.json');

        if (!candidates || candidates.length === 0) {
            renderError(container, "No early topics detected. System requires stronger combined signals from Memory, Cycle, and Evolution.");
            return;
        }

        renderEarlyTopics(container, candidates);
    } catch (e) {
        console.error("[EarlyView] Error:", e);
        renderError(container, "Failed to load early topic candidates.");
    }
}

function renderEarlyTopics(container, candidates) {
    container.innerHTML = `
        <div class="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <!-- HEADER -->
            <div class="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-slate-800 pb-6">
                <div>
                    <h1 class="text-3xl font-black text-white tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-rose-500">
                        Early Topic Detector
                    </h1>
                    <p class="text-slate-400 text-sm mt-1">Proactive identification of pre-narrative signals before mainstream adoption.</p>
                </div>
            </div>

            <!-- TOP CANDIDATES GRID -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                ${candidates.slice(0, 6).map(c => renderEarlyCard(c)).join('')}
            </div>

            <!-- FULL INVENTORY -->
            <div class="bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden p-6">
                <h2 class="text-lg font-bold text-white mb-6">Signal Intelligence Inventory</h2>
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-sm text-slate-400">
                        <thead class="bg-slate-800/50 text-slate-300 text-xs font-black uppercase tracking-wider">
                            <tr>
                                <th class="p-4 font-black">Candidate Theme</th>
                                <th class="p-4 font-black">Classification</th>
                                <th class="p-4 font-black text-center">Score</th>
                                <th class="p-4 font-black">Confidence</th>
                                <th class="p-4 font-black text-right">Phase</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-800">
                            ${candidates.map(c => `
                                <tr class="hover:bg-slate-800/30 transition-colors">
                                    <td class="p-4">
                                        <div class="flex flex-col">
                                            <span class="font-bold text-white">${c.theme}</span>
                                            <span class="text-[10px] text-slate-500">${c.topic_name}</span>
                                        </div>
                                    </td>
                                    <td class="p-4">
                                        <span class="px-2 py-1 rounded text-[10px] font-black border ${getClassificationClass(c.classification)}">
                                            ${c.classification}
                                        </span>
                                    </td>
                                    <td class="p-4 text-center font-mono font-black text-orange-400">${c.early_topic_score}</td>
                                    <td class="p-4">
                                        <span class="text-xs font-bold ${c.confidence === 'HIGH' ? 'text-emerald-400' : 'text-slate-400'}">${c.confidence}</span>
                                    </td>
                                    <td class="p-4 text-right font-bold text-slate-500">${c.current_phase}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    `;
}

function renderEarlyCard(c) {
    const classStyle = getClassificationClass(c.classification);
    return `
        <div class="group bg-slate-900 border border-slate-800 rounded-2xl p-6 hover:border-orange-500/50 transition-all duration-500">
            <div class="flex justify-between items-start mb-6">
                <div class="flex flex-col">
                    <span class="text-[10px] font-black uppercase tracking-widest text-slate-500 mb-1">Early Indicator</span>
                    <h3 class="text-xl font-bold text-white group-hover:text-orange-400 transition-colors uppercase">${c.theme}</h3>
                    <p class="text-[10px] text-slate-400 mt-1 italic">${c.topic_name}</p>
                </div>
                <div class="flex flex-col items-end">
                    <span class="text-2xl font-black text-orange-500 font-mono">${c.early_topic_score}</span>
                    <span class="text-[8px] font-black uppercase text-slate-600">Growth Score</span>
                </div>
            </div>

            <div class="space-y-4 mb-6">
                <div class="flex flex-wrap gap-2">
                    <span class="px-2 py-0.5 rounded text-[9px] font-black border ${classStyle}">${c.classification}</span>
                    <span class="px-2 py-0.5 rounded text-[9px] font-black border border-slate-700 text-slate-400">${c.confidence} CONF</span>
                </div>
            </div>

            <div class="bg-slate-800/50 rounded-xl p-4 border border-slate-800/80 mb-6">
                <h4 class="text-[10px] font-black text-slate-500 uppercase mb-3 tracking-wider">Evidence Chain</h4>
                <div class="space-y-2">
                    ${c.why_early.map(reason => `
                        <div class="flex items-start gap-2">
                            <div class="w-1 h-1 rounded-full bg-orange-500 mt-1.5 shrink-0"></div>
                            <span class="text-[10px] text-slate-300 leading-tight">${reason}</span>
                        </div>
                    `).join('')}
                </div>
            </div>

            <div class="flex items-center justify-between pt-4 border-t border-slate-800">
                <div class="flex items-center gap-2">
                    <div class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
                    <span class="text-[10px] text-emerald-500 font-black uppercase">${c.current_phase}</span>
                </div>
                <div class="text-[10px] text-slate-500 font-bold">NEXT: ${c.next_theme_path[1] || '---'}</div>
            </div>
        </div>
    `;
}

function getClassificationClass(cls) {
    if (cls.includes('PRIORITY')) return 'text-rose-400 border-rose-500/50 bg-rose-500/10 shadow-[0_0_10px_rgba(244,63,94,0.1)]';
    if (cls.includes('WATCH')) return 'text-orange-400 border-orange-500/50 bg-orange-500/10';
    return 'text-slate-400 border-slate-700 bg-slate-800/30';
}

function renderError(container, msg) {
    container.innerHTML = `
        <div class="min-h-[60vh] flex flex-col items-center justify-center text-center p-8">
            <div class="w-20 h-20 bg-slate-800/50 rounded-full flex items-center justify-center mb-6 text-slate-500 border border-slate-700">
                <svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
            </div>
            <h2 class="text-2xl font-black text-white mb-2 italic tracking-tight">Signal Detection Quiet</h2>
            <p class="text-slate-500 max-w-md mx-auto text-sm leading-relaxed">${msg}</p>
        </div>
    `;
}
