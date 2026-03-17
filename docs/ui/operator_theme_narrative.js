/**
 * HOIN Insight: Theme Narrative View 📜
 * STEP-40: Expands early themes into structured narratives.
 */
import { fetchJSON } from './utils.js?v=30';

export async function initThemeNarrativeView(container) {
    console.log("[ThemeNarrativeView] Initializing...");
    if (!container) container = document.getElementById('main-content') || document.getElementById('app');
    if (!container) return;
    container.innerHTML = `<div class="p-8 text-slate-400 animate-pulse">Expanding Theme Narrative...</div>`;

    try {
        const data = await fetchJSON('data/ops/theme_narrative.json');
        if (!data) {
            renderError(container, "Narrative data not available. Ensure engine PHASE 1.3.9.5 is complete.");
            return;
        }
        renderNarrative(container, data);
    } catch (e) {
        console.error("[ThemeNarrativeView] Error:", e);
        renderError(container, "Failed to load thematic narrative.");
    }
}

function renderNarrative(container, data) {
    container.innerHTML = `
        <div class="max-w-4xl mx-auto py-16 px-6 animate-in fade-in slide-in-from-bottom-12 duration-1000">
            <!-- HEADER -->
            <div class="mb-16 border-b border-slate-800 pb-12">
                <div class="flex items-center gap-3 mb-6">
                    <span class="p-3 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-500">
                        <i class="fas fa-scroll text-2xl"></i>
                    </span>
                    <div>
                        <div class="text-[10px] font-black text-amber-500 uppercase tracking-[0.3em]">Phase 1.3.9.5 Narrative Expansion</div>
                        <h1 class="text-4xl font-black text-white italic tracking-tighter">Theme Narrative: ${data.theme}</h1>
                    </div>
                </div>
                <div class="p-8 bg-slate-900 border border-slate-800 rounded-3xl">
                    <p class="text-xl text-slate-300 font-bold italic leading-relaxed">
                        "${data.explanation}"
                    </p>
                </div>
            </div>

            <!-- NARRATIVE BLOCKS -->
            <div class="space-y-12">
                <!-- Situation -->
                <div class="group">
                    <div class="flex items-center gap-3 mb-6">
                        <span class="text-[10px] font-black text-slate-500 uppercase tracking-widest">01 Situation</span>
                        <div class="h-px flex-1 bg-slate-800 group-hover:bg-amber-500/30 transition-colors"></div>
                    </div>
                    <div class="text-3xl font-black text-white mb-4 italic tracking-tight leading-tight">
                        배경 상황: ${data.theme}의 전개
                    </div>
                    <div class="text-lg text-slate-400 font-medium leading-relaxed">
                        ${data.situation}
                    </div>
                </div>

                <!-- Contradiction -->
                <div class="group">
                    <div class="flex items-center gap-3 mb-6">
                        <span class="text-[10px] font-black text-rose-500 uppercase tracking-widest">02 Structural Contradiction</span>
                        <div class="h-px flex-1 bg-slate-800 group-hover:bg-rose-500/30 transition-colors"></div>
                    </div>
                    <div class="text-3xl font-black text-white mb-4 italic tracking-tight leading-tight">
                        구조적 모순: 왜 지금 문제인가
                    </div>
                    <div class="p-8 bg-rose-500/5 border border-rose-500/10 rounded-3xl">
                        <div class="text-xl text-rose-100 font-black italic leading-relaxed">
                            "${data.contradiction}"
                        </div>
                    </div>
                </div>

                <!-- Sector Impact -->
                <div class="group">
                    <div class="flex items-center gap-3 mb-6">
                        <span class="text-[10px] font-black text-indigo-500 uppercase tracking-widest">03 Sector Impact</span>
                        <div class="h-px flex-1 bg-slate-800 group-hover:bg-indigo-500/30 transition-colors"></div>
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        ${(data.sector_impact || []).map(sector => `
                            <div class="p-6 bg-indigo-500/5 border border-indigo-500/10 rounded-2xl flex flex-col justify-center">
                                <span class="text-[8px] font-black text-indigo-400 uppercase tracking-widest mb-1">Impacted Sector</span>
                                <span class="text-white font-black text-lg">${sector}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>

                <!-- Why It Matters -->
                <div class="group">
                    <div class="flex items-center gap-3 mb-6">
                        <span class="text-[10px] font-black text-emerald-500 uppercase tracking-widest">04 Strategic Importance</span>
                        <div class="h-px flex-1 bg-slate-800 group-hover:bg-emerald-500/30 transition-colors"></div>
                    </div>
                    <div class="text-3xl font-black text-white mb-4 italic tracking-tight leading-tight">
                        결론: 경제사냥꾼의 시선
                    </div>
                    <div class="text-lg text-slate-400 font-medium leading-relaxed italic border-l-4 border-emerald-500 pl-6">
                        ${data.why_it_matters}
                    </div>
                </div>
            </div>
        </div>
    `;
}

function renderError(container, msg) {
    container.innerHTML = `
        <div class="min-h-[60vh] flex flex-col items-center justify-center text-center p-8">
            <div class="w-20 h-20 bg-slate-800/50 rounded-full flex items-center justify-center mb-6 text-amber-500 border border-slate-700">
                <i class="fas fa-scroll text-3xl"></i>
            </div>
            <h2 class="text-2xl font-black text-white mb-2 italic tracking-tight">Narrative Link Broken</h2>
            <p class="text-slate-500 max-w-md mx-auto text-sm leading-relaxed">${msg}</p>
        </div>
    `;
}
