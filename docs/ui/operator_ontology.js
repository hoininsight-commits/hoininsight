/**
 * STEP-25 Topic Ontology View
 * Visualizes Topic -> Theme -> Sector mappings and patterns.
 */
import { fetchJSON } from './utils.js?v=27';

export async function initOntologyView(container) {
    console.log("[OntologyView] Initializing...");
    if (!container) container = document.getElementById('main-content') || document.getElementById('app');
    if (!container) return;
    container.innerHTML = `<div class="p-8 text-slate-400 animate-pulse">Loading Ontology Intelligence...</div>`;

    try {
        const [resolved, patterns, ontology] = await Promise.all([
            fetchJSON('data/ontology/topic_resolved.json'),
            fetchJSON('data/memory/narrative_patterns.json'),
            fetchJSON('data/ontology/topic_ontology.json')
        ]);

        if (!resolved || !patterns) {
            renderError(container, "Ontology data not yet available. Run the daily pipeline to generate results.");
            return;
        }

        renderOntology(container, resolved, patterns, ontology);
    } catch (e) {
        console.error("[OntologyView] Error:", e);
        renderError(container, "Failed to load ontology assets.");
    }
}

function renderOntology(container, resolved, patterns, ontology) {
    const topThemes = patterns.top_themes || [];
    const themePatterns = patterns.theme_patterns || [];

    container.innerHTML = `
        <div class="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <!-- HEADER -->
            <div class="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-slate-800 pb-6">
                <div>
                    <h1 class="text-3xl font-black text-white tracking-tight">Topic Ontology</h1>
                    <p class="text-slate-400 text-sm mt-1">Structural mapping of specific topics to macro themes and sectors.</p>
                </div>
                <div class="flex gap-4">
                    <div class="bg-slate-900 border border-slate-800 px-4 py-2 rounded-lg text-xs font-mono text-cyan-400">
                        Total Topics Scaled: ${patterns.total_records || 0}
                    </div>
                </div>
            </div>

            <!-- TOP THEMES GRID -->
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <!-- PANEL: TOP THEMES -->
                <div class="lg:col-span-2 bg-slate-900/50 border border-slate-800 rounded-2xl p-6 backdrop-blur-xl">
                    <div class="flex items-center justify-between mb-6">
                        <h2 class="text-lg font-bold text-white flex items-center gap-2">
                            <span class="w-2 h-2 rounded-full bg-cyan-500 shadow-[0_0_10px_rgba(6,182,212,0.5)]"></span>
                            Dominant Narrative Themes
                        </h2>
                        <span class="text-[10px] text-slate-500 uppercase tracking-widest font-black">Historical Frequency</span>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        ${topThemes.map(t => `
                            <div class="group bg-slate-800/30 border border-slate-800/50 hover:border-cyan-500/50 p-4 rounded-xl transition-all duration-300">
                                <div class="flex justify-between items-start mb-2">
                                    <span class="text-sm font-bold text-slate-200 group-hover:text-cyan-400 transition-colors">${t.theme}</span>
                                    <span class="text-xs font-mono text-slate-500">${t.count} hits</span>
                                </div>
                                <div class="w-full bg-slate-700/30 h-1.5 rounded-full overflow-hidden">
                                    <div class="bg-gradient-to-r from-cyan-600 to-blue-500 h-full transition-all duration-1000" 
                                         style="width: ${Math.min(100, (t.count / (topThemes[0]?.count || 1)) * 100)}%"></div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>

                <!-- PANEL: RECURRENCE -->
                <div class="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 backdrop-blur-xl">
                    <div class="flex items-center justify-between mb-6">
                        <h2 class="text-lg font-bold text-white flex items-center gap-2">
                            <span class="w-2 h-2 rounded-full bg-amber-500 shadow-[0_0_10px_rgba(245,158,11,0.5)]"></span>
                            Theme Intervals
                        </h2>
                    </div>
                    <div class="space-y-4">
                        ${themePatterns.slice(0, 8).map(p => `
                            <div class="flex items-center justify-between p-3 rounded-lg bg-slate-800/20 border border-slate-800/50 text-xs">
                                <span class="text-slate-300 font-medium">${p.theme}</span>
                                <div class="text-right">
                                    <div class="text-amber-400 font-bold">${p.avg_interval_days}d avg</div>
                                    <div class="text-slate-500 text-[10px]">Seen ${p.last_seen}</div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>

            <!-- RECENT RESOLUTIONS -->
            <div class="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
                <h2 class="text-lg font-bold text-white mb-6">Recent Topic Resolutions</h2>
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-sm text-slate-400">
                        <thead class="bg-slate-800/50 text-slate-300 text-xs font-black uppercase tracking-wider">
                            <tr>
                                <th class="p-4 rounded-tl-xl font-black">Topic</th>
                                <th class="p-4 font-black">Mapped Theme</th>
                                <th class="p-4 font-black">Sector</th>
                                <th class="p-4 rounded-tr-xl font-black">Macro Context</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-800">
                            ${resolved.map(r => `
                                <tr class="hover:bg-slate-800/30 transition-colors">
                                    <td class="p-4 font-bold text-white">${r.topic}</td>
                                    <td class="p-4">
                                        <span class="px-2 py-1 rounded bg-cyan-900/40 text-cyan-400 text-[10px] font-bold border border-cyan-800/50">${r.theme}</span>
                                    </td>
                                    <td class="p-4 text-xs font-mono">${r.sector}</td>
                                    <td class="p-4 italic text-slate-500">${r.macro}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    `;
}

function renderError(container, msg) {
    container.innerHTML = `
        <div class="min-h-[60vh] flex flex-col items-center justify-center text-center p-8">
            <div class="w-20 h-20 bg-slate-800/50 rounded-full flex items-center justify-center mb-6 text-slate-500 border border-slate-700">
                <svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
            </div>
            <h2 class="text-2xl font-black text-white mb-2 italic tracking-tight">Ontology Quiet Mode</h2>
            <p class="text-slate-500 max-w-md mx-auto text-sm leading-relaxed">${msg}</p>
        </div>
    `;
}
