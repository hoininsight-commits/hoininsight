/**
 * HOIN Insight: Today Topic (Pressure Engine) View
 * STEP-38: Evaluates and selects the lead narrative topic.
 */
import { fetchJSON } from './utils.js?v=30';

export async function initTopTopicView(container) {
    console.log("[TopTopicView] Initializing...");
    if (!container) container = document.getElementById('main-content') || document.getElementById('app');
    if (!container) return;
    container.innerHTML = `<div class="p-8 text-slate-400 animate-pulse">Calculating Global Narrative Pressure...</div>`;

    try {
        const data = await fetchJSON('data/ops/top_topic.json');
        if (!data) {
            renderError(container, "Topic selection data not available. Ensure engine PHASE 1.4.6 is complete.");
            return;
        }
        renderTopTopic(container, data);
    } catch (e) {
        console.error("[TopTopicView] Error:", e);
        renderError(container, "Failed to load topic pressure data.");
    }
}

function renderTopTopic(container, data) {
    const pressurePct = (data.topic_pressure * 100).toFixed(1);
    
    container.innerHTML = `
        <div class="max-w-4xl mx-auto py-16 px-6 animate-in fade-in slide-in-from-bottom-12 duration-1000">
            <!-- HEADER -->
            <div class="text-center mb-16">
                <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-500 text-[10px] font-black uppercase tracking-widest mb-6">
                    <span class="relative flex h-2 w-2">
                        <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
                        <span class="relative inline-flex rounded-full h-2 w-2 bg-amber-500"></span>
                    </span>
                    Engine Phase 1.4.6: Narrative Pressure
                </div>
                <h1 class="text-5xl font-black text-white tracking-tighter mb-4 italic">
                    🔥 Today Lead Topic
                </h1>
                <p class="text-slate-500 font-bold uppercase tracking-widest text-xs">
                    Selection optimized for Economic Hunter Content Strategy
                </p>
            </div>

            <!-- MAIN SELECTION CARD -->
            <div class="bg-slate-900 border border-slate-800 rounded-[3rem] p-12 mb-12 relative overflow-hidden shadow-2xl">
                <div class="absolute -top-24 -right-24 w-64 h-64 bg-amber-500/10 blur-[100px] rounded-full"></div>
                
                <div class="relative z-10 flex flex-col md:flex-row items-center gap-12">
                    <!-- CIRCULAR GAUGE -->
                    <div class="flex-shrink-0 relative">
                        <svg class="w-48 h-48 transform -rotate-90">
                            <circle cx="96" cy="96" r="88" fill="none" stroke="rgba(30, 41, 59, 0.5)" stroke-width="12"></circle>
                            <circle cx="96" cy="96" r="88" fill="none" stroke="url(#gradient)" stroke-width="12" 
                                stroke-dasharray="553" stroke-dashoffset="${553 - (553 * data.topic_pressure)}"
                                stroke-linecap="round"
                                class="transition-all duration-1000 ease-out">
                            </circle>
                            <defs>
                                <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                    <stop offset="0%" style="stop-color:#f59e0b" />
                                    <stop offset="100%" style="stop-color:#ef4444" />
                                </linearGradient>
                            </defs>
                        </svg>
                        <div class="absolute inset-0 flex flex-col items-center justify-center">
                            <span class="text-4xl font-black text-white italic">${pressurePct}%</span>
                            <span class="text-[10px] font-black text-slate-500 uppercase tracking-widest">Pressure</span>
                        </div>
                    </div>

                    <!-- TOPIC DETAILS -->
                    <div class="text-center md:text-left">
                        <h2 class="text-4xl font-black text-white mb-4 tracking-tight leading-tight">
                            ${data.selected_topic}
                        </h2>
                        <div class="flex flex-wrap justify-center md:justify-start gap-4">
                            <div class="px-4 py-2 rounded-xl bg-slate-800 border border-slate-700">
                                <span class="block text-[8px] font-black text-slate-500 uppercase mb-1">Topic ID</span>
                                <span class="text-slate-300 font-mono text-xs">${data.topic_id || 'N/A'}</span>
                            </div>
                            <div class="px-4 py-2 rounded-xl bg-slate-800 border border-slate-700">
                                <span class="block text-[8px] font-black text-slate-500 uppercase mb-1">Analysis Date</span>
                                <span class="text-slate-300 font-bold text-xs">${data.updated_at.split(' ')[0]}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- COMPONENTS BREAKDOWN -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                ${Object.entries(data.components).map(([key, val]) => `
                    <div class="bg-slate-900/50 border border-slate-800 p-6 rounded-3xl backdrop-blur-xl group hover:border-slate-500 transition-all">
                        <div class="flex justify-between items-center mb-4">
                            <span class="text-xs font-black text-slate-500 uppercase tracking-widest group-hover:text-slate-300 transition-colors">
                                ${key.replace('_', ' ')}
                            </span>
                            <span class="text-white font-black italic">${(val * 100).toFixed(0)}%</span>
                        </div>
                        <div class="h-2 bg-slate-800 rounded-full overflow-hidden">
                            <div class="h-full bg-gradient-to-r from-amber-500 to-rose-500 transition-all duration-1000" style="width: ${val * 100}%"></div>
                        </div>
                    </div>
                `).join('')}
            </div>

            <p class="mt-12 text-center text-slate-600 text-[10px] font-bold uppercase tracking-[0.2em]">
                System decision based on Anomaly(0.4) • Flow(0.3) • Spread(0.2) • Persistence(0.1)
            </p>
        </div>
    `;
}

function renderError(container, msg) {
    container.innerHTML = `
        <div class="min-h-[60vh] flex flex-col items-center justify-center text-center p-8">
            <div class="w-20 h-20 bg-slate-800/50 rounded-full flex items-center justify-center mb-6 text-slate-500 border border-slate-700">
                <i class="fas fa-fire-alt text-3xl"></i>
            </div>
            <h2 class="text-2xl font-black text-white mb-2 italic tracking-tight">Narrative Pressure Signal Lost</h2>
            <p class="text-slate-500 max-w-md mx-auto text-sm leading-relaxed">${msg}</p>
        </div>
    `;
}
