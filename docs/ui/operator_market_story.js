/**
 * HOIN Insight: Today Market Story View
 * STEP-35: Synthesizes market state, contradictions, and themes.
 */
import { fetchJSON } from './utils.js?v=30';

export async function initMarketStoryView(container) {
    console.log("[MarketStoryView] Initializing...");
    if (!container) container = document.getElementById('main-content') || document.getElementById('app');
    if (!container) return;
    container.innerHTML = `<div class="p-8 text-slate-400 animate-pulse">Constructing Today's Market Narrative...</div>`;

    try {
        const story = await fetchJSON('data/ops/today_story.json');
        if (!story) {
            renderError(container, "Market story data not available. Ensure engine PHASE 1.4 is complete.");
            return;
        }
        renderMarketStory(container, story);
    } catch (e) {
        console.error("[MarketStoryView] Error:", e);
        renderError(container, "Failed to load market story.");
    }
}

function renderMarketStory(container, story) {
    container.innerHTML = `
        <div class="max-w-4xl mx-auto py-12 px-6 animate-in fade-in slide-in-from-bottom-8 duration-1000">
            <!-- HEADER -->
            <div class="text-center mb-16">
                <span class="inline-block px-4 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-[10px] font-black uppercase tracking-widest mb-6">
                    Today's Market Story • ${story.date}
                </span>
                <h1 class="text-5xl md:text-6xl font-black text-white tracking-tight leading-tight mb-8">
                    ${story.title}
                </h1>
                <div class="h-1.5 w-24 bg-gradient-to-r from-indigo-500 to-rose-500 mx-auto rounded-full"></div>
            </div>

            <!-- STORY BOARD -->
            <div class="bg-slate-900/50 border border-slate-800 rounded-3xl p-10 md:p-16 backdrop-blur-xl relative overflow-hidden group">
                <!-- Background Accents -->
                <div class="absolute -right-20 -top-20 w-64 h-64 bg-indigo-500/10 blur-3xl rounded-full"></div>
                <div class="absolute -left-20 -bottom-20 w-64 h-64 bg-rose-500/10 blur-3xl rounded-full"></div>

                <div class="relative z-10 space-y-12">
                    <!-- SUMMARY -->
                    <section>
                        <h2 class="text-sm font-black text-slate-500 uppercase tracking-widest mb-6 flex items-center gap-3">
                            <span class="w-8 h-[1px] bg-slate-800"></span> 시장 상황 및 내러티브
                        </h2>
                        <p class="text-xl md:text-2xl text-slate-200 font-medium leading-relaxed">
                            ${story.summary}
                        </p>
                    </section>

                    <!-- THEME -->
                    <section class="p-8 bg-indigo-500/5 border border-indigo-500/20 rounded-2xl">
                        <h2 class="text-xs font-black text-indigo-400 uppercase tracking-widest mb-4">Featured Investment Theme</h2>
                        <h3 class="text-2xl font-black text-white uppercase tracking-tight mb-2">${story.featured_theme}</h3>
                        <p class="text-slate-400 text-sm italic">Engine identified this as the highest-probability path based on structural anomalies.</p>
                    </section>

                    <!-- IMPACT SECTORS -->
                    <section>
                        <h2 class="text-sm font-black text-slate-500 uppercase tracking-widest mb-6">Affected Industrial Sectors</h2>
                        <div class="flex flex-wrap gap-3">
                            ${story.impact_sectors.map(s => `
                                <span class="px-5 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-slate-300 font-bold text-sm hover:border-slate-500 transition-all cursor-default">
                                    ${s}
                                </span>
                            `).join('')}
                        </div>
                    </section>
                </div>
            </div>

            <!-- FOOTER NOTE -->
            <div class="mt-12 text-center">
                <p class="text-slate-600 text-[11px] font-bold uppercase tracking-widest">
                    Synthesized by HOIN MarketStoryEngine v1.0 • Autonomous Narrative Intelligence
                </p>
            </div>
        </div>
    `;
}

function renderError(container, msg) {
    container.innerHTML = `
        <div class="min-h-[60vh] flex flex-col items-center justify-center text-center p-8">
            <div class="w-20 h-20 bg-slate-800/50 rounded-full flex items-center justify-center mb-6 text-slate-500 border border-slate-700">
                <i class="fas fa-book-open text-3xl"></i>
            </div>
            <h2 class="text-2xl font-black text-white mb-2 italic tracking-tight">Story Data Quiet</h2>
            <p class="text-slate-500 max-w-md mx-auto text-sm leading-relaxed">${msg}</p>
        </div>
    `;
}
