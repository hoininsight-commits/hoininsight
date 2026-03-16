/**
 * STEP-30 Operator Action View
 * Visualizes Narrative Actions (OBSERVE, WATCHLIST, TRACK, FOCUS).
 */
import { fetchJSON } from './utils.js?v=29';

export async function initActionView(container) {
    console.log("[ActionView] Initializing...");
    if (!container) container = document.getElementById('main-content') || document.getElementById('app');
    if (!container) return;
    container.innerHTML = `<div class="p-8 text-slate-400 animate-pulse">Scanning Operator Action Protocols...</div>`;

    try {
        const actions = await fetchJSON('data/ops/operator_actions.json');

        if (!actions || actions.length === 0) {
            renderError(container, "No operator actions generated. System requires escalated narratives to trigger action signals.");
            return;
        }

        renderActions(container, actions);
    } catch (e) {
        console.error("[ActionView] Error:", e);
        renderError(container, "Failed to load operator action assets.");
    }
}

function renderActions(container, actions) {
    container.innerHTML = `
        <div class="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <!-- HEADER -->
            <div class="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-slate-800 pb-6">
                <div>
                    <h1 class="text-3xl font-black text-white tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-500">
                        Operator Actions
                    </h1>
                    <p class="text-slate-400 text-sm mt-1">Decision-ready signals converted from narrative intelligence layers.</p>
                </div>
            </div>

            <!-- TOP ACTIONS GRID -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                ${actions.slice(0, 4).map(a => renderActionCard(a)).join('')}
            </div>

            <!-- FULL INVENTORY -->
            <div class="bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden p-6">
                <h2 class="text-lg font-bold text-white mb-6">Action Intelligence Inventory</h2>
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-sm text-slate-400">
                        <thead class="bg-slate-800/50 text-slate-300 text-xs font-black uppercase tracking-wider">
                            <tr>
                                <th class="p-4 font-black">Theme Cluster</th>
                                <th class="p-4 font-black text-center">Action Signal</th>
                                <th class="p-4 font-black text-center">Action Score</th>
                                <th class="p-4 font-black">Recommended Focus</th>
                                <th class="p-4 font-black text-right">Confidence</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-800">
                            ${actions.map(a => `
                                <tr class="hover:bg-slate-800/30 transition-colors">
                                    <td class="p-4 font-bold text-white">${a.theme}</td>
                                    <td class="p-4 text-center">
                                        <span class="px-2 py-1 rounded text-[10px] font-black border ${getActionClass(a.action)}">
                                            ${a.action}
                                        </span>
                                    </td>
                                    <td class="p-4 text-center font-mono font-black text-emerald-400">${a.action_score}</td>
                                    <td class="p-4 text-xs">${a.recommended_focus.join(', ')}</td>
                                    <td class="p-4 text-right">
                                        <span class="text-xs font-bold ${a.confidence === 'HIGH' ? 'text-emerald-400' : 'text-slate-500'}">${a.confidence}</span>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    `;
}

function renderActionCard(a) {
    const actionClass = getActionClass(a.action);
    return `
        <div class="group bg-slate-900 border border-slate-800 rounded-2xl p-6 hover:border-emerald-500/50 transition-all duration-500">
            <div class="flex justify-between items-start mb-6">
                <div class="flex flex-col">
                    <span class="text-[10px] font-black uppercase tracking-widest text-slate-500 mb-1">Operator Protocol</span>
                    <h3 class="text-xl font-bold text-white group-hover:text-emerald-400 transition-colors uppercase">${a.theme}</h3>
                </div>
                <div class="flex flex-col items-end">
                    <span class="text-2xl font-black text-emerald-500 font-mono">${a.action_score}</span>
                    <span class="text-[8px] font-black uppercase text-slate-600">Action Priority</span>
                </div>
            </div>

            <div class="grid grid-cols-2 gap-4 mb-6">
                <div class="bg-slate-800/30 rounded-xl p-4 border border-slate-800/50">
                    <div class="text-[9px] font-black text-slate-500 uppercase mb-1">Mandated Action</div>
                    <div class="text-xs font-black ${actionClass.split(' ')[0]}">${a.action}</div>
                </div>
                <div class="bg-slate-800/30 rounded-xl p-4 border border-slate-800/50">
                    <div class="text-[9px] font-black text-slate-500 uppercase mb-1">Escalation Stage</div>
                    <div class="text-xs font-black text-white">${a.escalation_stage}</div>
                </div>
            </div>

            <div class="bg-slate-800/50 rounded-xl p-4 border border-slate-800/80 mb-6">
                <h4 class="text-[10px] font-black text-slate-500 uppercase mb-3 tracking-wider">Decision Evidence</h4>
                <div class="space-y-2">
                    ${a.why_action.map(reason => `
                        <div class="flex items-start gap-2">
                            <div class="w-1 h-1 rounded-full bg-emerald-500 mt-1.5 shrink-0"></div>
                            <span class="text-[10px] text-slate-300 leading-tight">${reason}</span>
                        </div>
                    `).join('')}
                </div>
            </div>

            <div class="flex items-center justify-between pt-4 border-t border-slate-800">
                <div class="flex flex-col">
                    <span class="text-[8px] font-black text-slate-600 uppercase mb-0.5">Recommended Focus</span>
                    <div class="flex items-center gap-1 text-[9px] text-slate-400 font-bold overflow-hidden">
                        ${a.recommended_focus.join(' • ')}
                    </div>
                </div>
                <div class="flex flex-col items-end">
                    <span class="text-[8px] font-black text-slate-600 uppercase mb-0.5">Next Move</span>
                    <span class="text-[9px] font-black text-amber-500">${a.next_expected_move}</span>
                </div>
            </div>
        </div>
    `;
}

function getActionClass(action) {
    switch(action) {
        case 'OBSERVE': return 'text-slate-400 border-slate-700 bg-slate-800/30';
        case 'WATCHLIST': return 'text-blue-400 border-blue-500/50 bg-blue-500/10';
        case 'TRACK': return 'text-amber-400 border-amber-500/50 bg-amber-500/10';
        case 'FOCUS': return 'text-emerald-400 border-emerald-500/50 bg-emerald-500/10 shadow-[0_0_15px_rgba(16,185,129,0.15)] animate-pulse';
        default: return 'text-slate-400 border-slate-500/50 bg-slate-500/10';
    }
}

function renderError(container, msg) {
    container.innerHTML = `
        <div class="min-h-[60vh] flex flex-col items-center justify-center text-center p-8">
            <div class="w-20 h-20 bg-slate-800/50 rounded-full flex items-center justify-center mb-6 text-slate-500 border border-slate-700">
                <svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
            </div>
            <h2 class="text-2xl font-black text-white mb-2 italic tracking-tight">Action Protocol Inactive</h2>
            <p class="text-slate-500 max-w-md mx-auto text-sm leading-relaxed">${msg}</p>
        </div>
    `;
}
