/**
 * operator_narrative_brief.js — Narrative and Background Analysis
 * Consolidates Market Story and Theme Narrative.
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

export async function initNarrativeBriefView(container) {
    console.log('[NarrativeBrief] Initializing...');
    
    try {
        const response = await fetch(`data/ops/today_operator_brief.json?t=${Date.now()}`);
        if (!response.ok) throw new Error('Data brief not found');
        const brief = await response.json();
        
        if (!brief || !brief.narrative_brief) {
            container.innerHTML = `<div class="p-8 text-slate-500 bg-slate-900/50 rounded-xl border border-slate-800">No Narrative Brief data available</div>`;
            return;
        }

        const data = brief.narrative_brief;

        container.innerHTML = `
            <div class="animate-in fade-in slide-in-from-bottom-4 duration-700">
                <header class="flex justify-between items-center mb-10">
                    <div>
                        <h2 class="text-3xl font-black text-white tracking-tight flex items-center gap-3">
                            <span class="text-indigo-500 text-4xl">📜</span> Narrative Brief
                        </h2>
                        <p class="text-slate-500 text-sm font-medium mt-1 uppercase tracking-widest">Market Context & Structural Depth</p>
                    </div>
                </header>

                <div class="space-y-8">
                    <!-- Main Story Card -->
                    <div class="bg-gradient-to-br from-[#1c2128] to-[#161b22] border border-slate-800 rounded-3xl p-10 overflow-hidden relative">
                        <div class="absolute top-0 right-0 p-8 opacity-10 text-8xl grayscale">📖</div>
                        
                        <div class="max-w-2xl relative z-10">
                            <div class="text-[10px] font-black text-indigo-400 uppercase tracking-widest mb-4">Today's Market Story</div>
                            <h3 class="text-4xl font-black text-white leading-[1.1] mb-6">${safeText(data.title)}</h3>
                            <p class="text-slate-400 text-lg font-medium leading-relaxed mb-8">
                                ${safeText(data.summary)}
                            </p>
                            
                            <div class="inline-flex items-center gap-2 px-4 py-2 bg-indigo-500/10 border border-indigo-500/20 rounded-full">
                                <span class="text-[10px] font-black text-indigo-400 uppercase">Core Theme:</span>
                                <span class="text-[10px] font-black text-white uppercase ml-1">${safeText(brief.core_theme || data.featured_theme)}</span>
                            </div>
                        </div>
                    </div>

                    <!-- Analysis Grid -->
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                        <!-- Situation & Contradiction -->
                        <div class="bg-[#161b22] border border-slate-800 rounded-2xl p-8">
                           <h4 class="text-slate-500 text-[10px] font-black uppercase tracking-widest mb-6 border-b border-slate-800 pb-4">Structural Analysis</h4>
                           
                           <div class="space-y-8">
                                <div>
                                    <div class="flex items-center gap-3 mb-2">
                                        <div class="w-1.5 h-1.5 rounded-full bg-blue-500"></div>
                                        <div class="text-xs font-black text-slate-300 uppercase">Situation (현황)</div>
                                    </div>
                                    <p class="text-sm text-slate-400 leading-relaxed font-medium pl-4.5">${safeText(data.situation)}</p>
                                </div>

                                <div>
                                    <div class="flex items-center gap-3 mb-2">
                                        <div class="w-1.5 h-1.5 rounded-full bg-amber-500"></div>
                                        <div class="text-xs font-black text-slate-300 uppercase">Structural Contradiction (모순)</div>
                                    </div>
                                    <p class="text-sm text-slate-400 leading-relaxed font-medium pl-4.5">${safeText(data.contradiction)}</p>
                                </div>
                           </div>
                        </div>

                        <!-- Impact & Action -->
                        <div class="bg-[#161b22] border border-slate-800 rounded-2xl p-8">
                            <h4 class="text-slate-500 text-[10px] font-black uppercase tracking-widest mb-6 border-b border-slate-800 pb-4">Sector Impact</h4>
                            <p class="text-sm text-slate-400 leading-relaxed font-medium mb-8">
                                ${safeText(data.sector_impact)}
                            </p>

                            <div class="p-5 bg-indigo-500/5 border border-indigo-500/10 rounded-xl">
                                <div class="text-[10px] font-black text-indigo-400 uppercase mb-3">Narrative Verdict</div>
                                <p class="text-[11px] text-slate-400 font-medium italic">
                                    "${safeText(data.explanation)}"
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

    } catch (err) {
        container.innerHTML = `<div class="p-8 text-red-500 bg-red-500/10 rounded-xl border border-red-500/20">Narrative Brief Data Error: ${err.message}</div>`;
    }
}
