/**
 * HOIN Insight: Theme Early Detection View
 * STEP-39: Detects latent themes from anomaly clusters.
 */
import { fetchJSON } from './utils.js?v=30';

export async function initEarlyThemeView(container) {
    console.log("[EarlyThemeView] Initializing...");
    if (!container) container = document.getElementById('main-content') || document.getElementById('app');
    if (!container) return;
    container.innerHTML = `<div class="p-8 text-slate-400 animate-pulse">Scanning Structural Anomaly Clusters...</div>`;

    try {
        const data = await fetchJSON('data/ops/top_early_theme.json');
        if (!data) {
            renderError(container, "Early detection data not available. Ensure engine PHASE 1.3.9 is complete.");
            return;
        }
        renderEarlyTheme(container, data);
    } catch (e) {
        console.error("[EarlyThemeView] Error:", e);
        renderError(container, "Failed to load early detection signals.");
    }
}

function renderEarlyTheme(container, data) {
    container.innerHTML = `
        <div class="max-w-4xl mx-auto py-16 px-6 animate-in fade-in slide-in-from-bottom-12 duration-1000">
            <!-- HEADER -->
            <div class="mb-16 border-b border-slate-800 pb-12">
                <div class="flex items-center gap-3 mb-6">
                    <span class="p-3 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
                        <i class="fas fa-compass text-2xl"></i>
                    </span>
                    <div>
                        <div class="text-[10px] font-black text-indigo-500 uppercase tracking-[0.3em]">Phase 1.3.9 Early Detection</div>
                        <h1 class="text-4xl font-black text-white italic tracking-tighter">Compass: Early Theme Detection</h1>
                    </div>
                </div>
                <p class="text-lg text-slate-400 font-medium leading-relaxed max-w-2xl">
                    데이터 이상 패턴을 선제적으로 결합하여, 본격적인 서사가 형성되기 전의 초기 테마를 포착합니다.
                </p>
            </div>

            <!-- PERFORMANCE CARD -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
                <!-- Top Theme Card -->
                <div class="md:col-span-2 bg-slate-900 border border-slate-800 rounded-[2.5rem] p-10 relative overflow-hidden group">
                    <div class="absolute inset-0 bg-gradient-to-br from-indigo-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                    <div class="relative z-10">
                        <div class="flex items-center justify-between mb-8">
                            <span class="px-4 py-2 rounded-full bg-rose-500/10 border border-rose-500/30 text-rose-500 text-[10px] font-black uppercase tracking-widest">
                                Top Early Theme Found
                            </span>
                            <div class="text-right">
                                <span class="block text-[8px] font-black text-slate-600 uppercase tracking-widest mb-1">Detection Score</span>
                                <span class="text-3xl font-black text-white italic">${(data.score * 100).toFixed(1)}%</span>
                            </div>
                        </div>
                        <h2 class="text-5xl font-black text-white mb-6 tracking-tighter leading-tight group-hover:translate-x-2 transition-transform">
                            ${data.theme}
                        </h2>
                        <div class="p-6 bg-slate-950/50 rounded-2xl border border-slate-800">
                            <p class="text-slate-300 font-bold italic leading-relaxed">
                                "${data.summary}"
                            </p>
                        </div>
                    </div>
                </div>

                <!-- Stage Card -->
                <div class="bg-slate-900/50 border border-slate-800 rounded-[2.5rem] p-8 flex flex-col justify-between">
                    <div>
                        <div class="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-4">Maturity Stage</div>
                        <div class="text-2xl font-black text-indigo-400 italic mb-2">${data.stage}</div>
                        <p class="text-[10px] text-slate-600 font-bold leading-relaxed uppercase">
                            Pattern has crossed structural significance but lacks broad narrative momentum.
                        </p>
                    </div>
                    <div class="pt-8 border-t border-slate-800/50">
                        <div class="text-[10px] font-black text-slate-500 uppercase mb-4">Detection Confidence</div>
                        <div class="flex items-center gap-2">
                            <span class="font-black text-white">${data.confidence}</span>
                            <div class="flex-1 h-1 bg-slate-800 rounded-full">
                                <div class="h-full bg-indigo-500 rounded-full" style="width: 85%"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- SIGNALS SECTION -->
            <div class="bg-slate-900 border border-slate-800 rounded-[2.5rem] p-10">
                <h3 class="text-xs font-black text-slate-400 uppercase tracking-[0.3em] mb-8 flex items-center gap-3">
                    <span class="w-2 h-2 rounded-full bg-indigo-500"></span> Supporting Structural Signals
                </h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    ${(data.signals || []).map(sig => `
                        <div class="p-5 bg-slate-950/30 border border-slate-800/50 rounded-2xl flex items-center justify-between group">
                            <span class="text-slate-300 font-bold transition-transform group-hover:translate-x-1">${sig}</span>
                            <span class="text-[10px] font-black text-indigo-500 uppercase tracking-widest px-2 py-1 rounded bg-indigo-500/5">Active</span>
                        </div>
                    `).join('')}
                    ${(data.potential_sectors || []).map(sec => `
                        <div class="p-5 bg-indigo-500/5 border border-indigo-500/10 rounded-2xl flex items-center justify-between group">
                            <div>
                                <span class="block text-[8px] font-black text-indigo-400 uppercase tracking-widest mb-1">Target Sector</span>
                                <span class="text-slate-100 font-black">${sec}</span>
                            </div>
                            <i class="fas fa-link text-indigo-500/30"></i>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
}

function renderError(container, msg) {
    container.innerHTML = `
        <div class="min-h-[60vh] flex flex-col items-center justify-center text-center p-8">
            <div class="w-20 h-20 bg-slate-800/50 rounded-full flex items-center justify-center mb-6 text-slate-500 border border-slate-700">
                <i class="fas fa-compass text-3xl"></i>
            </div>
            <h2 class="text-2xl font-black text-white mb-2 italic tracking-tight">Detection Signal Lost</h2>
            <p class="text-slate-500 max-w-md mx-auto text-sm leading-relaxed">${msg}</p>
        </div>
    `;
}
