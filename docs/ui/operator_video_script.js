/**
 * HOIN Insight: Today Video Script View
 * STEP-37: Synthesizes Market Story and Mentionables into a video script.
 */
import { fetchJSON } from './utils.js?v=30';

export async function initVideoScriptView(container) {
    console.log("[VideoScriptView] Initializing...");
    if (!container) container = document.getElementById('main-content') || document.getElementById('app');
    if (!container) return;
    container.innerHTML = `<div class="p-8 text-slate-400 animate-pulse">Generating Economic Hunter Script...</div>`;

    try {
        const script = await fetchJSON('data/ops/today_video_script.json');
        if (!script) {
            renderError(container, "Video script data not available. Ensure engine PHASE 1.4.7 is complete.");
            return;
        }
        renderVideoScript(container, script);
    } catch (e) {
        console.error("[VideoScriptView] Error:", e);
        renderError(container, "Failed to load video script.");
    }
}

function renderVideoScript(container, script) {
    container.innerHTML = `
        <div class="max-w-5xl mx-auto py-12 px-6 animate-in fade-in slide-in-from-bottom-8 duration-700">
            <!-- HEADER -->
            <div class="mb-12 flex items-end justify-between border-b border-slate-800 pb-8">
                <div>
                    <div class="flex items-center gap-4 mb-4">
                        <span class="px-3 py-1 rounded bg-rose-500/10 border border-rose-500/30 text-rose-400 text-[10px] font-black uppercase tracking-widest">
                            STEP-37 Script Engine
                        </span>
                        <span class="text-slate-500 text-[10px] font-bold uppercase tracking-widest">${script.date}</span>
                    </div>
                    <h1 class="text-4xl font-black text-white tracking-tight mb-2 flex items-center gap-4">
                        🎬 Today Video Script
                    </h1>
                    <p class="text-slate-500 font-bold uppercase tracking-tighter text-xs">
                        Economic Hunter Style Content Architecture • ${script.theme}
                    </p>
                </div>
                <!-- Action Badge -->
                <div class="px-6 py-4 rounded-2xl bg-slate-900 border border-slate-800 text-center min-w-[140px]">
                    <div class="text-[10px] font-black text-slate-600 uppercase tracking-widest mb-1">Operator Stance</div>
                    <div class="text-2xl font-black ${getActionColor(script.operator_action)} italic transition-colors tracking-tighter">
                        ${script.operator_action}
                    </div>
                </div>
            </div>

            <!-- SCRIPT CONTENT -->
            <div class="grid grid-cols-1 lg:grid-cols-4 gap-8">
                <!-- NAV TRACK -->
                <div class="lg:col-span-1 hidden lg:block">
                    <div class="sticky top-24 space-y-2">
                        ${['Hook', 'Situation', 'Contradiction', 'Sectors', 'Stocks', 'Action'].map(item => `
                            <a href="#${item}" class="block px-4 py-2 rounded-lg text-slate-500 hover:text-white hover:bg-slate-800/50 font-bold text-sm transition-all border-l-2 border-transparent">
                                ${item}
                            </a>
                        `).join('')}
                    </div>
                </div>

                <!-- MAIN SCRIPT -->
                <div class="lg:col-span-3 space-y-12 pb-24">
                    <!-- HOOK -->
                    <section id="Hook" class="scroll-mt-24 group">
                        <h2 class="text-[10px] font-black text-rose-500 uppercase tracking-[0.3em] mb-4 flex items-center gap-3">
                            <span class="w-10 h-[1px] bg-rose-500/30"></span> 01 Hook
                        </h2>
                        <div class="p-8 bg-slate-900/50 border border-slate-800 rounded-3xl group-hover:border-rose-500/30 transition-all">
                            <p class="text-2xl font-black text-white leading-tight italic">
                                "${script.hook}"
                            </p>
                        </div>
                    </section>

                    <!-- SITUATION -->
                    <section id="Situation" class="scroll-mt-24">
                        <h2 class="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em] mb-4">02 Market Situation</h2>
                        <p class="text-lg text-slate-300 font-medium leading-relaxed">
                            ${script.situation}
                        </p>
                    </section>

                    <!-- CONTRADICTION -->
                    <section id="Contradiction" class="scroll-mt-24">
                        <h2 class="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em] mb-4">03 Structural Contradiction</h2>
                        <div class="p-8 bg-indigo-500/5 border border-indigo-500/20 rounded-3xl">
                            <p class="text-lg text-indigo-100 font-bold italic leading-relaxed">
                                "${script.contradiction}"
                            </p>
                        </div>
                    </section>

                    <!-- SECTORS -->
                    <section id="Sectors" class="scroll-mt-24">
                        <h2 class="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em] mb-4">04 Sector Impact</h2>
                        <div class="flex flex-wrap gap-2">
                            ${script.sectors.map(s => `
                                <span class="px-4 py-2 rounded-lg bg-slate-800 border border-slate-700 text-slate-400 font-bold text-xs">
                                    ${s}
                                </span>
                            `).join('')}
                        </div>
                    </section>

                    <!-- STOCKS -->
                    <section id="Stocks" class="scroll-mt-24">
                        <h2 class="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em] mb-4">05 Mentionable Stocks</h2>
                        <div class="space-y-3">
                            ${script.stocks.map(s => `
                                <div class="p-5 bg-slate-900/30 border border-slate-800 rounded-2xl flex items-center justify-between">
                                    <div>
                                        <div class="text-white font-black text-lg">${s.stock}</div>
                                        <div class="text-[10px] text-slate-600 font-bold uppercase">${s.sector}</div>
                                    </div>
                                    <div class="text-right">
                                        <div class="text-rose-500 font-black italic text-xl">${s.score}</div>
                                        <div class="text-[9px] text-slate-500 font-bold uppercase tracking-widest">Relevance</div>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </section>

                    <!-- OPERATOR ACTION -->
                    <section id="Action" class="scroll-mt-24">
                        <h2 class="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em] mb-4">06 Operator Decision</h2>
                        <div class="p-10 rounded-3xl bg-slate-950 border-2 border-slate-800 relative overflow-hidden">
                            <div class="absolute inset-0 bg-gradient-to-br from-slate-900 to-transparent opacity-50"></div>
                            <div class="relative z-10">
                                <p class="text-2xl font-black text-white tracking-tight leading-relaxed">
                                    ${script.operator_action === 'FOCUS' ? '🔥' : '⚙️'} ${script.operator_action}: 신호 감도에 따른 최종 행동 지침입니다.
                                </p>
                            </div>
                        </div>
                    </section>
                </div>
            </div>
        </div>
    `;
}

function getActionColor(action) {
    switch(action) {
        case 'FOCUS': return 'text-rose-500';
        case 'TRACK': return 'text-indigo-400';
        case 'WATCH': return 'text-slate-500';
        default: return 'text-white';
    }
}

function renderError(container, msg) {
    container.innerHTML = `
        <div class="min-h-[60vh] flex flex-col items-center justify-center text-center p-8">
            <div class="w-20 h-20 bg-slate-800/50 rounded-full flex items-center justify-center mb-6 text-slate-500 border border-slate-700">
                <i class="fas fa-file-alt text-3xl"></i>
            </div>
            <h2 class="text-2xl font-black text-white mb-2 italic tracking-tight">Script Narrative Lost</h2>
            <p class="text-slate-500 max-w-md mx-auto text-sm leading-relaxed">${msg}</p>
        </div>
    `;
}
