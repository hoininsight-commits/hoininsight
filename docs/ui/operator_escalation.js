/**
 * STEP-29 Narrative Escalation View
 * Visualizes Growth Stages, Escalation Scores, and Evidence Chains.
 */
import { fetchJSON } from './utils.js?v=29';

export async function initEscalationView() {
    console.log("[EscalationView] Initializing...");
    const container = document.getElementById('main-content');
    container.innerHTML = `<div class="p-8 text-slate-400 animate-pulse">Tracking Narrative Escalation Stages...</div>`;

    try {
        const escalations = await fetchJSON('data/ops/narrative_escalation.json');

        if (!escalations || escalations.length === 0) {
            renderError(container, "No escalation data available. System requires early topics to track growth stages.");
            return;
        }

        renderEscalation(container, escalations);
    } catch (e) {
        console.error("[EscalationView] Error:", e);
        renderError(container, "Failed to load narrative escalation assets.");
    }
}

function renderEscalation(container, escalations) {
    container.innerHTML = `
        <div class="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <!-- HEADER -->
            <div class="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-slate-800 pb-6">
                <div>
                    <h1 class="text-3xl font-black text-white tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-fuchsia-500">
                        Narrative Escalation
                    </h1>
                    <p class="text-slate-400 text-sm mt-1">Growth tracking of emerging signals into mainstream market narratives.</p>
                </div>
            </div>

            <!-- TOP ESCALATION GRID -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                ${escalations.slice(0, 4).map(e => renderEscalationCard(e)).join('')}
            </div>

            <!-- FULL INVENTORY -->
            <div class="bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden p-6">
                <h2 class="text-lg font-bold text-white mb-6">Escalation Stage Inventory</h2>
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-sm text-slate-400">
                        <thead class="bg-slate-800/50 text-slate-300 text-xs font-black uppercase tracking-wider">
                            <tr>
                                <th class="p-4 font-black">Theme Cluster</th>
                                <th class="p-4 font-black text-center">Stage</th>
                                <th class="p-4 font-black text-center">Escalation Score</th>
                                <th class="p-4 font-black">Top Reason</th>
                                <th class="p-4 font-black text-right">Confidence</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-800">
                            ${escalations.map(e => `
                                <tr class="hover:bg-slate-800/30 transition-colors">
                                    <td class="p-4 font-bold text-white">${e.theme}</td>
                                    <td class="p-4 text-center">
                                        <span class="px-2 py-1 rounded text-[10px] font-black border ${getStageClass(e.escalation_stage)}">
                                            ${e.escalation_stage}
                                        </span>
                                    </td>
                                    <td class="p-4 text-center font-mono font-black text-fuchsia-400">${e.escalation_score}</td>
                                    <td class="p-4 text-xs">${e.why_escalating[0] || '---'}</td>
                                    <td class="p-4 text-right">
                                        <span class="text-xs font-bold ${e.confidence === 'HIGH' ? 'text-emerald-400' : 'text-slate-500'}">${e.confidence}</span>
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

function renderEscalationCard(e) {
    const stageClass = getStageClass(e.escalation_stage);
    return `
        <div class="group bg-slate-900 border border-slate-800 rounded-2xl p-6 hover:border-fuchsia-500/50 transition-all duration-500">
            <div class="flex justify-between items-start mb-6">
                <div class="flex flex-col">
                    <span class="text-[10px] font-black uppercase tracking-widest text-slate-500 mb-1">Escalation Tracker</span>
                    <h3 class="text-xl font-bold text-white group-hover:text-fuchsia-400 transition-colors uppercase">${e.theme}</h3>
                </div>
                <div class="flex flex-col items-end">
                    <span class="text-2xl font-black text-fuchsia-500 font-mono">${e.escalation_score}</span>
                    <span class="text-[8px] font-black uppercase text-slate-600">Growth Intensity</span>
                </div>
            </div>

            <div class="grid grid-cols-2 gap-4 mb-6">
                <div class="bg-slate-800/30 rounded-xl p-4 border border-slate-800/50">
                    <div class="text-[9px] font-black text-slate-500 uppercase mb-1">Current Stage</div>
                    <div class="text-xs font-black ${stageClass.split(' ')[0]}">${e.escalation_stage}</div>
                </div>
                <div class="bg-slate-800/30 rounded-xl p-4 border border-slate-800/50">
                    <div class="text-[9px] font-black text-slate-500 uppercase mb-1">Early Score</div>
                    <div class="text-xs font-black text-white">${e.early_topic_score}</div>
                </div>
            </div>

            <div class="bg-slate-800/50 rounded-xl p-4 border border-slate-800/80 mb-6">
                <h4 class="text-[10px] font-black text-slate-500 uppercase mb-3 tracking-wider">Analysis Evidence</h4>
                <div class="space-y-2">
                    ${e.why_escalating.slice(0, 3).map(reason => `
                        <div class="flex items-start gap-2">
                            <div class="w-1 h-1 rounded-full bg-fuchsia-500 mt-1.5 shrink-0"></div>
                            <span class="text-[10px] text-slate-300 leading-tight">${reason}</span>
                        </div>
                    `).join('')}
                </div>
            </div>

            <div class="flex items-center justify-between pt-4 border-t border-slate-800">
                <div class="flex flex-col">
                    <span class="text-[8px] font-black text-slate-600 uppercase mb-0.5">Escalation Path</span>
                    <div class="flex items-center gap-1 text-[9px] text-slate-500 font-bold overflow-hidden">
                        ${e.next_escalation_path.map((step, idx) => `
                            <span>${step}</span>
                            ${idx < e.next_escalation_path.length - 1 ? '<span class="text-fuchsia-500">→</span>' : ''}
                        `).join('')}
                    </div>
                </div>
                <div class="flex flex-col items-end">
                    <span class="text-[8px] font-black text-slate-600 uppercase mb-0.5">Confidence</span>
                    <span class="text-[9px] font-black text-emerald-500">${e.confidence}</span>
                </div>
            </div>
        </div>
    `;
}

function getStageClass(stage) {
    switch(stage) {
        case 'WEAK_SIGNAL': return 'text-slate-400 border-slate-700 bg-slate-800/30';
        case 'EMERGING': return 'text-blue-400 border-blue-500/50 bg-blue-500/10';
        case 'ESCALATING': return 'text-fuchsia-400 border-fuchsia-500/50 bg-fuchsia-500/10 shadow-[0_0_10px_rgba(217,70,239,0.1)]';
        case 'DOMINANT': return 'text-rose-400 border-rose-500/50 bg-rose-500/10 shadow-[0_0_15px_rgba(244,63,94,0.15)] animate-pulse';
        default: return 'text-slate-400 border-slate-500/50 bg-slate-500/10';
    }
}

function renderError(container, msg) {
    container.innerHTML = `
        <div class="min-h-[60vh] flex flex-col items-center justify-center text-center p-8">
            <div class="w-20 h-20 bg-slate-800/50 rounded-full flex items-center justify-center mb-6 text-slate-500 border border-slate-700">
                <svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
            </div>
            <h2 class="text-2xl font-black text-white mb-2 italic tracking-tight">Escalation Quiet</h2>
            <p class="text-slate-500 max-w-md mx-auto text-sm leading-relaxed">${msg}</p>
        </div>
    `;
}
