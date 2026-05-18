/**
 * HOIN Insight: Mentionable Stocks View
 * STEP-36: Maps Market Story to industrial sectors and stocks.
 */
import { fetchJSON } from './utils.js?v=30';

export async function initMentionablesView(container) {
    console.log("[MentionablesView] Initializing...");
    if (!container) container = document.getElementById('main-content') || document.getElementById('app');
    if (!container) return;
    container.innerHTML = `<div class="p-8 text-slate-400 animate-pulse">Scanning Impact Zones and Mapping Relevant Stocks...</div>`;

    try {
        const data = await fetchJSON('data/ops/impact_mentionables.json');
        if (!data) {
            renderError(container, "Mentionables data not available. Ensure engine PHASE 1.4.5 is complete.");
            return;
        }
        renderMentionables(container, data);
    } catch (e) {
        console.error("[MentionablesView] Error:", e);
        renderError(container, "Failed to load mentionable stocks.");
    }
}

function renderMentionables(container, data) {
    container.innerHTML = `
        <div class="max-w-6xl mx-auto py-12 px-6 animate-in fade-in slide-in-from-bottom-8 duration-700">
            <!-- HEADER -->
            <div class="mb-12">
                <div class="flex items-center gap-4 mb-4">
                    <span class="px-3 py-1 rounded bg-orange-500/10 border border-orange-500/30 text-orange-400 text-[10px] font-black uppercase tracking-widest">
                        STEP-36 Impact Engine
                    </span>
                </div>
                <h1 class="text-4xl font-black text-white tracking-tight mb-4 flex items-center gap-4">
                    📈 Mentionable Stocks
                </h1>
                <p class="text-slate-400 text-lg max-w-2xl font-medium leading-relaxed">
                    오늘의 시장 스토리(<span class="text-slate-200">${data.theme}</span>)를 기반으로 도출된 핵심 영향 산업과 주목할 만한 종목 리스트입니다.
                </p>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <!-- LEFT SIDE: SECTORS -->
                <div class="lg:col-span-1 space-y-6">
                    <div class="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 backdrop-blur-xl">
                        <h2 class="text-xs font-black text-slate-500 uppercase tracking-widest mb-6">Affected Impact Zones</h2>
                        <div class="flex flex-col gap-3">
                            ${data.affected_sectors.map(s => `
                                <div class="px-4 py-3 rounded-xl bg-slate-800/50 border border-slate-700 flex items-center justify-between group hover:border-slate-500 transition-all">
                                    <span class="text-slate-300 font-bold text-sm">${s}</span>
                                    <i class="fas fa-check-circle text-orange-500/50 group-hover:text-orange-500 transition-colors"></i>
                                </div>
                            `).join('')}
                        </div>
                    </div>

                    <div class="p-6 bg-gradient-to-br from-orange-500/10 to-transparent border border-orange-500/20 rounded-2xl">
                        <h3 class="text-xs font-black text-orange-400 uppercase tracking-widest mb-2">Scoring Engine V1</h3>
                        <p class="text-slate-400 text-[11px] leading-relaxed">
                            테마 연관성(50%), 자본 흐름(30%), 시장 모멘텀(20%)을 종합하여 산출된 신뢰도 점수입니다.
                        </p>
                    </div>
                </div>

                <!-- RIGHT SIDE: STOCKS -->
                <div class="lg:col-span-2">
                    <div class="bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden backdrop-blur-xl">
                        <table class="w-full text-left">
                            <thead class="bg-slate-800/50 border-b border-slate-800">
                                <tr>
                                    <th class="px-8 py-5 text-[10px] font-black text-slate-500 uppercase tracking-widest">Stock Candidate</th>
                                    <th class="px-8 py-5 text-[10px] font-black text-slate-500 uppercase tracking-widest text-center">Score</th>
                                    <th class="px-8 py-5 text-[10px] font-black text-slate-500 uppercase tracking-widest">Rational</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-slate-800">
                                ${data.mentionable_stocks.map(s => `
                                    <tr class="hover:bg-slate-800/30 transition-colors group">
                                        <td class="px-8 py-6">
                                            <div class="flex items-center gap-4">
                                                <div class="w-10 h-10 rounded-xl bg-orange-500/10 flex items-center justify-center text-orange-500 font-black text-xs border border-orange-500/20">
                                                    ${s.stock.substring(0, 1)}
                                                </div>
                                                <div>
                                                    <div class="text-white font-black text-lg group-hover:text-orange-400 transition-colors">${s.stock}</div>
                                                    <div class="text-[10px] font-bold text-slate-500 uppercase tracking-tighter">${s.sector}</div>
                                                </div>
                                            </div>
                                        </td>
                                        <td class="px-8 py-6 text-center">
                                            <div class="inline-flex flex-col items-center">
                                                <span class="text-2xl font-black text-white italic">${s.score}</span>
                                                <div class="w-12 h-1 bg-slate-800 rounded-full overflow-hidden mt-1">
                                                    <div class="h-full bg-orange-500" style="width: ${s.score}%"></div>
                                                </div>
                                            </div>
                                        </td>
                                        <td class="px-8 py-6 text-slate-400 text-sm font-medium leading-normal">
                                            ${s.reason}
                                        </td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function renderError(container, msg) {
    container.innerHTML = `
        <div class="min-h-[60vh] flex flex-col items-center justify-center text-center p-8">
            <div class="w-20 h-20 bg-slate-800/50 rounded-full flex items-center justify-center mb-6 text-slate-500 border border-slate-700">
                <i class="fas fa-chart-line text-3xl"></i>
            </div>
            <h2 class="text-2xl font-black text-white mb-2 italic tracking-tight">Impact Zone Signal Lost</h2>
            <p class="text-slate-500 max-w-md mx-auto text-sm leading-relaxed">${msg}</p>
        </div>
    `;
}
