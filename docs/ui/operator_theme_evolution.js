/**
 * HOIN Insight: Theme Evolution View 🧬
 * STEP-41: Classifies the lifecycle stage of a theme.
 */
import { fetchJSON } from './utils.js?v=30';

export async function initThemeEvolutionView(container) {
    console.log("[ThemeEvolutionView] Initializing...");
    if (!container) container = document.getElementById('main-content') || document.getElementById('app');
    if (!container) return;
    container.innerHTML = `<div class="p-8 text-slate-400 animate-pulse">Analyzing Lifecycle Evolution...</div>`;

    try {
        const data = await fetchJSON('data/ops/theme_evolution_state.json');
        if (!data) {
            renderError(container, "Evolution data not available. Ensure engine PHASE 1.3.9.7 is complete.");
            return;
        }
        renderEvolution(container, data);
    } catch (e) {
        console.error("[ThemeEvolutionView] Error:", e);
        renderError(container, "Failed to load evolution telemetry.");
    }
}

function renderEvolution(container, data) {
    const stages = ["PRE-STORY", "EMERGING", "EXPANSION", "MAINSTREAM", "EXHAUSTION"];
    const currentIndex = stages.indexOf(data.stage);
    
    container.innerHTML = `
        <div class="max-w-4xl mx-auto py-16 px-6 animate-in fade-in slide-in-from-bottom-12 duration-1000">
            <!-- HEADER -->
            <div class="mb-16 border-b border-slate-800 pb-12">
                <div class="flex items-center gap-3 mb-6">
                    <span class="p-3 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-500">
                        <i class="fas fa-dna text-2xl"></i>
                    </span>
                    <div>
                        <div class="text-[10px] font-black text-cyan-500 uppercase tracking-[0.3em]">Phase 1.3.9.7 Evolution Analysis</div>
                        <h1 class="text-4xl font-black text-white italic tracking-tighter">Lifecycle: ${data.theme}</h1>
                    </div>
                </div>
                <p class="text-lg text-slate-400 font-medium leading-relaxed">
                    테마의 시장 침투도와 서사 확산 속도를 분석하여 현재 어느 단계에 와 있는지 판정합니다.
                </p>
            </div>

            <!-- EVOLUTION TRACKER -->
            <div class="bg-slate-900 border border-slate-800 rounded-[2.5rem] p-12 mb-12 relative overflow-hidden">
                <div class="absolute top-0 right-0 p-8">
                    <div class="text-[8px] font-black text-slate-600 uppercase tracking-[0.3em] mb-1">Evolution Score</div>
                    <div class="text-4xl font-black text-white italic">${(data.score * 100).toFixed(1)}%</div>
                </div>

                <div class="flex justify-between items-center mb-16 relative">
                    <!-- Progress Line -->
                    <div class="absolute top-1/2 left-0 right-0 h-1 bg-slate-800 -translate-y-1/2 rounded-full">
                        <div class="h-full bg-cyan-500 rounded-full shadow-[0_0_20px_rgba(6,182,212,0.5)] transition-all duration-1000" style="width: ${((currentIndex + 1) / stages.length) * 100}%"></div>
                    </div>
                    
                    ${stages.map((s, i) => `
                        <div class="relative z-10 flex flex-col items-center">
                            <div class="w-8 h-8 rounded-full border-2 border-slate-800 flex items-center justify-center transition-all duration-500 
                                ${i <= currentIndex ? 'bg-cyan-500 border-cyan-400 shadow-[0_0_15px_rgba(6,182,212,0.4)]' : 'bg-slate-950'}">
                                ${i <= currentIndex ? '<i class="fas fa-check text-[10px] text-white"></i>' : ''}
                            </div>
                            <div class="absolute top-12 whitespace-nowrap text-[10px] font-black ${i === currentIndex ? 'text-cyan-400' : 'text-slate-600'} uppercase tracking-widest">${s}</div>
                        </div>
                    `).join('')}
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-8 pt-8 border-t border-slate-800/50">
                    <div>
                        <div class="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-4">Why this Stage?</div>
                        <ul class="space-y-3">
                            ${(data.why_stage || []).map(why => `
                                <li class="flex items-start gap-2 text-slate-300 font-bold italic">
                                    <span class="text-cyan-500">▶</span>
                                    <span>${why}</span>
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                    <div class="bg-slate-950/50 rounded-3xl p-8 border border-slate-800/50">
                        <div class="text-[10px] font-black text-amber-500 uppercase tracking-widest mb-4">Operator Action Hint</div>
                        <div class="text-3xl font-black text-white italic mb-2 tracking-tighter">
                            ${data.score > 0.85 ? 'AVOID / EXIT' : (data.score > 0.65 ? 'HOLD / PROFIT' : 'WATCH / TRACK')}
                        </div>
                        <p class="text-[10px] text-slate-500 font-bold leading-relaxed uppercase">
                            Stage alignment suggests tactical patience or proactive positioning based on saturation metrics.
                        </p>
                    </div>
                </div>
            </div>

            <!-- COMPONENT BREAKDOWN -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                ${renderMetricCard("Signal Breadth", data.signal_breadth)}
                ${renderMetricCard("Narrative Spread", data.narrative_spread)}
                ${renderMetricCard("Capital Confirmation", data.capital_flow_confirmation)}
                ${renderMetricCard("Persistence", data.persistence)}
            </div>
        </div>
    `;
}

function renderMetricCard(label, val) {
    return `
        <div class="bg-slate-900 border border-slate-800 rounded-3xl p-6">
            <div class="text-[8px] font-black text-slate-500 uppercase tracking-widest mb-4">${label}</div>
            <div class="text-2xl font-black text-white italic mb-4">${(val * 100).toFixed(0)}%</div>
            <div class="h-1 bg-slate-800 rounded-full overflow-hidden">
                <div class="h-full bg-cyan-500/50 rounded-full transition-all duration-1000" style="width: ${val * 100}%"></div>
            </div>
        </div>
    `;
}

function renderError(container, msg) {
    container.innerHTML = `
        <div class="min-h-[60vh] flex flex-col items-center justify-center text-center p-8">
            <div class="w-20 h-20 bg-slate-800/50 rounded-full flex items-center justify-center mb-6 text-cyan-500 border border-slate-700">
                <i class="fas fa-dna text-3xl"></i>
            </div>
            <h2 class="text-2xl font-black text-white mb-2 italic tracking-tight">Evolution Signal Missing</h2>
            <p class="text-slate-500 max-w-md mx-auto text-sm leading-relaxed">${msg}</p>
        </div>
    `;
}
