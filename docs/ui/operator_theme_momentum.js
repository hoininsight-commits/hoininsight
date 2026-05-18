/**
 * HOIN Insight: Theme Momentum View ⚡
 * STEP-42: Analyzes the speed and acceleration of market themes.
 */
import { fetchJSON } from './utils.js?v=30';

export async function initThemeMomentumView(container) {
    console.log("[ThemeMomentumView] Initializing...");
    if (!container) container = document.getElementById('main-content') || document.getElementById('app');
    if (!container) return;
    container.innerHTML = `<div class="p-8 text-slate-400 animate-pulse">Analyzing Narrative Momentum...</div>`;

    try {
        const data = await fetchJSON('data/ops/theme_momentum_state.json');
        if (!data) {
            renderError(container, "Momentum data not available. Ensure engine PHASE 1.3.9.9 is complete.");
            return;
        }
        renderMomentum(container, data);
    } catch (e) {
        console.error("[ThemeMomentumView] Error:", e);
        renderError(container, "Failed to load momentum telemetry.");
    }
}

function renderMomentum(container, data) {
    const isPositive = data.momentum_score > 0;
    const colorClass = data.momentum_score > 0.4 ? 'text-amber-500' : (data.momentum_score > 0.1 ? 'text-orange-400' : (data.momentum_score < -0.1 ? 'text-blue-400' : 'text-slate-400'));
    const bgClass = data.momentum_score > 0.4 ? 'bg-amber-500/10 border-amber-500/20' : (data.momentum_score > 0.1 ? 'bg-orange-500/10 border-orange-500/20' : (data.momentum_score < -0.1 ? 'bg-blue-500/10 border-blue-500/20' : 'bg-slate-800/10 border-slate-700/20'));

    container.innerHTML = `
        <div class="max-w-4xl mx-auto py-16 px-6 animate-in fade-in slide-in-from-bottom-12 duration-1000">
            <!-- HEADER -->
            <div class="mb-16 border-b border-slate-800 pb-12">
                <div class="flex items-center gap-3 mb-6">
                    <span class="p-3 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-500">
                        <i class="fas fa-bolt text-2xl"></i>
                    </span>
                    <div>
                        <div class="text-[10px] font-black text-amber-500 uppercase tracking-[0.3em]">Phase 1.3.9.9 Momentum Telemetry</div>
                        <h1 class="text-4xl font-black text-white italic tracking-tighter">Momentum: ${data.theme}</h1>
                    </div>
                </div>
                <p class="text-lg text-slate-400 font-medium leading-relaxed">
                    테마의 확산 속도(Speed)와 가속도(Acceleration)를 분석하여 기세를 측정합니다.
                </p>
            </div>

            <!-- MOMENTUM DIAL -->
            <div class="bg-slate-900 border border-slate-800 rounded-[2.5rem] p-12 mb-12 relative overflow-hidden">
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                    <div class="flex flex-col items-center">
                        <div class="relative w-64 h-64 flex items-center justify-center">
                            <!-- SVG Gauge -->
                            <svg class="w-full h-full -rotate-90">
                                <circle cx="128" cy="128" r="110" fill="none" stroke="#1e293b" stroke-width="20" />
                                <circle cx="128" cy="128" r="110" fill="none" stroke="currentColor" stroke-width="20" 
                                    class="${isPositive ? 'text-amber-500' : 'text-blue-500'}"
                                    stroke-dasharray="691"
                                    stroke-dashoffset="${691 - (Math.abs(data.momentum_score) * 691)}"
                                    style="transition: stroke-dashoffset 1.5s ease-out" />
                            </svg>
                            <div class="absolute inset-0 flex flex-col items-center justify-center">
                                <span class="text-5xl font-black text-white italic tracking-tighter">${data.momentum_score > 0 ? '+' : ''}${data.momentum_score.toFixed(2)}</span>
                                <span class="text-[10px] font-black text-slate-500 uppercase tracking-widest mt-1">Velocity Score</span>
                            </div>
                        </div>
                    </div>
                    <div>
                        <div class="p-8 rounded-3xl ${bgClass} border mb-8">
                            <div class="text-[10px] font-black uppercase tracking-widest mb-2 ${colorClass}">Current State</div>
                            <div class="text-4xl font-black text-white italic tracking-tighter mb-4">${data.momentum_state}</div>
                            <p class="text-sm text-slate-400 font-bold leading-relaxed italic">
                                "${data.momentum_state === 'ACCELERATING' ? '테마의 기세가 매우 강력하며 대중적 관심이 폭발적으로 증가하는 단계입니다.' : '테마의 방향성과 확산 속도가 안정적인 궤도에 진입했습니다.'}"
                            </p>
                        </div>
                        <div class="grid grid-cols-2 gap-4">
                            <div class="p-6 bg-slate-950/50 rounded-2xl border border-slate-800">
                                <div class="text-[8px] font-black text-slate-500 uppercase tracking-widest mb-1">Direction</div>
                                <div class="text-xl font-black ${isPositive ? 'text-emerald-500' : 'text-rose-500'} italic uppercase">${isPositive ? 'Expanding' : 'Contracting'}</div>
                            </div>
                            <div class="p-6 bg-slate-950/50 rounded-2xl border border-slate-800">
                                <div class="text-[8px] font-black text-slate-500 uppercase tracking-widest mb-1">Action Hint</div>
                                <div class="text-xl font-black text-white italic uppercase">${data.momentum_score > 0.4 ? 'Priority' : 'Monitor'}</div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="mt-12 pt-12 border-t border-slate-800">
                    <div class="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-6">Momentum Drivers</div>
                    <div class="space-y-4">
                        ${(data.why_momentum || []).map(why => `
                            <div class="flex items-center gap-4 p-5 bg-slate-950/30 border border-slate-800/50 rounded-2xl">
                                <div class="w-2 h-2 rounded-full bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.5)]"></div>
                                <div class="text-slate-300 font-bold italic">${why}</div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>

            <!-- COMPONENT BREAKDOWN -->
            <div class="grid grid-cols-2 lg:grid-cols-4 gap-6">
                ${renderMetricCard("Narrative Accel", data.narrative_acceleration)}
                ${renderMetricCard("Flow Accel", data.capital_flow_acceleration)}
                ${renderMetricCard("Signal Density", data.signal_density_change)}
                ${renderMetricCard("Pressure Trend", data.topic_pressure_trend)}
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
                <div class="h-full bg-amber-500/50 rounded-full transition-all duration-1000" style="width: ${val * 100}%"></div>
            </div>
        </div>
    `;
}

function renderError(container, msg) {
    container.innerHTML = `
        <div class="min-h-[60vh] flex flex-col items-center justify-center text-center p-8">
            <div class="w-20 h-20 bg-slate-800/50 rounded-full flex items-center justify-center mb-6 text-amber-500 border border-slate-700">
                <i class="fas fa-bolt text-3xl"></i>
            </div>
            <h2 class="text-2xl font-black text-white mb-2 italic tracking-tight">Momentum Signal Missing</h2>
            <p class="text-slate-500 max-w-md mx-auto text-sm leading-relaxed">${msg}</p>
        </div>
    `;
}
