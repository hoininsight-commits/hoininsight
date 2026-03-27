/**
 * operator_content_studio.js — Content Generation & Production
 * Consolidates Topic Pressure, Today Topic, Investment Decisions & Risk.
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

export async function initContentStudioView(container) {
    console.log('[ContentStudio] Initializing...');
    
    try {
        const response = await fetch(`data/ops/today_operator_brief.json?t=${Date.now()}`);
        if (!response.ok) throw new Error('Data brief not found');
        const brief = await response.json();
        
        if (!brief || !brief.content_studio) {
            container.innerHTML = `<div class="p-8 text-slate-500 bg-slate-900/50 rounded-xl border border-slate-800">No Content Studio data available</div>`;
            return;
        }

        const data = brief.content_studio;
        const risk = brief.risk || { risk_level: 'LOW', risk_score: 0.0, invalidation: 'N/A' };

        container.innerHTML = `
            <div class="animate-in fade-in slide-in-from-bottom-4 duration-700">
                <header class="flex justify-between items-center mb-10">
                    <div>
                        <h2 class="text-3xl font-black text-white tracking-tight flex items-center gap-3">
                            <span class="text-orange-500 text-4xl">🎬</span> Content Studio
                        </h2>
                        <p class="text-slate-500 text-sm font-medium mt-1 uppercase tracking-widest">Script Engineering & Production Sync</p>
                    </div>
                </header>

                <!-- TODAY STRATEGY Banner -->
                <div class="mb-8 bg-gradient-to-r from-slate-900 to-indigo-900/30 border border-indigo-500/30 rounded-2xl overflow-hidden shadow-2xl">
                    <div class="p-6 flex flex-wrap items-center justify-between gap-6">
                        <div class="flex items-center gap-4">
                            <div class="w-12 h-12 bg-indigo-500/20 rounded-full flex items-center justify-center text-2xl shadow-inner shadow-indigo-500/20">🎯</div>
                            <div>
                                <div class="text-[10px] font-black text-indigo-400 uppercase tracking-widest mb-1">Today Strategy</div>
                                <div class="text-lg font-black text-white">Theme: <span class="text-indigo-300 font-extrabold">${safeText(brief.core_theme)}</span></div>
                            </div>
                        </div>
                        
                        <div class="flex items-center gap-8">
                            <div class="text-center">
                                <div class="text-[9px] font-bold text-slate-500 uppercase tracking-widest mb-1">Action</div>
                                <div class="text-sm font-black ${getActionColorClass(safeText(brief.investment_decision?.action))}">${safeText(brief.investment_decision?.action)}</div>
                            </div>
                            <div class="text-center">
                                <div class="text-[9px] font-bold text-slate-500 uppercase tracking-widest mb-1">Timing</div>
                                <div class="text-sm font-black text-white">${safeText(brief.investment_decision?.timing)}</div>
                            </div>
                            <div class="text-center">
                                <div class="text-[9px] font-bold text-slate-500 uppercase tracking-widest mb-1">Risk Level</div>
                                <div class="text-sm font-black ${getRiskColorClass(safeText(risk.risk_level))}">${safeText(risk.risk_level)}</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Risk Disclaimer Sub-bar -->
                    <div class="px-6 py-2.5 bg-black/40 border-t border-indigo-500/10 flex items-center justify-between">
                         <div class="flex items-center gap-2">
                            <span class="text-[9px] font-black text-slate-500 uppercase">Invalidation:</span>
                            <span class="text-[10px] font-bold text-slate-400">${safeText(risk.invalidation)}</span>
                         </div>
                         <div class="text-[9px] font-black text-indigo-400">SCORE: ${safeNumber(risk.risk_score, 2)}</div>
                    </div>

                    <!-- TODAY PORTFOLIO -->
                    <div class="px-6 py-4 bg-slate-900/40 border-t border-indigo-500/10 grid grid-cols-1 md:grid-cols-4 gap-4">
                        <div class="md:col-span-1 flex items-center gap-2">
                            <span class="text-[10px] font-black text-white uppercase tracking-widest">Today Portfolio:</span>
                        </div>
                        <div class="md:col-span-3 flex flex-wrap gap-3">
                            ${safeArray(brief.portfolio_allocation?.allocations).filter(a => a.weight > 0).map(a => `
                                <div class="px-3 py-1.5 bg-[#0d131f] border border-indigo-500/20 rounded-lg flex items-center gap-3">
                                    <span class="text-[10px] font-black text-blue-400">${safeText(a.ticker)}</span>
                                    <span class="text-[10px] font-black text-white">${safeNumber(a.weight * 100, 1)}%</span>
                                </div>
                            `).join('') || '<span class="text-[10px] font-medium text-slate-600 italic uppercase">No capital allocated</span>'}
                        </div>
                    </div>
                </div>

                <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
                    <!-- Right: Script Editor View (Priority) -->
                    <div class="lg:col-span-2 space-y-8">
                        <!-- Selection Context -->
                        <div class="bg-[#161b22] border border-slate-800 rounded-2xl p-8 relative overflow-hidden">
                            <div class="absolute top-0 right-0 w-64 h-64 bg-rose-500/5 blur-[100px] rounded-full -mr-20 -mt-20"></div>
                            
                            <div class="relative z-10">
                                <div class="flex items-center gap-3 mb-4">
                                    <div class="text-[10px] font-black text-rose-500 bg-rose-500/10 px-2 py-1 rounded uppercase">Selected Topic</div>
                                    <div class="flex items-center gap-1">
                                        <div class="text-[10px] font-black text-slate-500 uppercase">Pressure Index:</div>
                                        <div class="text-[10px] font-black text-rose-400">${safeNumber((data.topic_pressure || 0) * 100, 0)}</div>
                                    </div>
                                </div>
                                <h3 class="text-2xl font-black text-white mb-6 leading-tight">${safeText(data.selected_topic)}</h3>
                                
                                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <div class="p-6 bg-slate-900/50 border border-slate-800 rounded-xl space-y-3">
                                        <h4 class="text-slate-500 text-[10px] font-black uppercase tracking-widest">Core Message</h4>
                                        <p class="text-xs text-slate-300 font-medium leading-relaxed">${safeText(data.script?.core_message)}</p>
                                    </div>
                                    <div class="p-6 bg-slate-900/50 border border-slate-800 rounded-xl space-y-3">
                                        <h4 class="text-slate-500 text-[10px] font-black uppercase tracking-widest">Pressure Drivers</h4>
                                        <ul class="space-y-2">
                                            ${safeArray(data.pressure_drivers).map(d => `
                                                <li class="text-[10px] text-slate-400 font-medium flex items-center gap-2">
                                                    <span class="w-1 h-1 rounded-full bg-rose-500"></span> ${safeText(d)}
                                                </li>
                                            `).join('')}
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Video Script Content -->
                        <div class="bg-[#161b22] border border-slate-800 rounded-2xl p-10">
                             <div class="flex justify-between items-center mb-10 pb-6 border-b border-slate-800">
                                <h4 class="text-slate-200 text-xs font-black uppercase tracking-widest flex items-center gap-3">
                                    <span class="text-rose-500">✍️</span> Production Script (Realization)
                                </h4>
                                <button class="px-4 py-2 bg-rose-500 hover:bg-rose-600 text-white text-[11px] font-black rounded-lg transition-all shadow-lg shadow-rose-500/20 active:scale-95">COPY SCRIPT</button>
                             </div>

                             <div class="space-y-10">
                                <div>
                                    <div class="text-[10px] font-black text-rose-500 uppercase mb-4 tracking-widest">[ HOOK / OPENING ]</div>
                                    <div class="p-6 bg-slate-900/80 border-l-4 border-rose-500 rounded-r-xl text-lg font-bold text-white leading-relaxed">
                                        "${safeText(data.script?.hook)}"
                                    </div>
                                </div>

                                <div class="opacity-30 pointer-events-none select-none">
                                    <div class="text-[10px] font-black text-slate-500 uppercase mb-4 tracking-widest">[ BODY / ANALYSIS ]</div>
                                    <div class="p-6 bg-slate-900/50 border border-slate-800 rounded-xl text-sm font-medium text-slate-500 leading-relaxed italic">
                                        (상세 스크립트 본문은 Video Agent 및 자동화 엔진을 통해 생성된 전체 내역을 참조하십시오. 이 화면은 결과 요약 및 운용 승인용입니다.)
                                    </div>
                                </div>
                             </div>
                        </div>
                    </div>

                    <!-- Left: Production Checks -->
                    <div class="space-y-8">
                        <div class="bg-[#0d1117] border border-slate-800 rounded-2xl p-8 sticky top-8">
                            <h4 class="text-slate-500 text-[10px] font-black uppercase tracking-widest mb-6 px-1">Production Checklist</h4>
                            <div class="space-y-4">
                                <div class="flex items-center gap-4 p-4 bg-slate-900/30 rounded-xl border border-slate-800/50">
                                    <div class="w-6 h-6 rounded-full border-2 border-rose-500 flex items-center justify-center">
                                        <div class="w-2.5 h-2.5 bg-rose-500 rounded-full"></div>
                                    </div>
                                    <span class="text-xs font-bold text-slate-300">핵심 로직 검증 완료</span>
                                </div>
                                <div class="flex items-center gap-4 p-4 bg-slate-900/30 rounded-xl border border-slate-800/50">
                                    <div class="w-6 h-6 rounded-full border-2 border-rose-500 flex items-center justify-center">
                                        <div class="w-2.5 h-2.5 bg-rose-500 rounded-full"></div>
                                    </div>
                                    <span class="text-xs font-bold text-slate-300">내러티브 정합성 확인</span>
                                </div>
                                <div class="flex items-center gap-4 p-4 bg-slate-900/30 rounded-xl border border-slate-800/50 opacity-50">
                                    <div class="w-6 h-6 rounded-full border-2 border-slate-700 flex items-center justify-center"></div>
                                    <span class="text-xs font-bold text-slate-500">배포 데이터 대기 중</span>
                                </div>
                            </div>

                            <div class="mt-10 pt-10 border-t border-slate-800 text-center">
                                <p class="text-[9px] font-black text-slate-500 uppercase mb-6 leading-relaxed">
                                    이 주제는 오늘의 TOP-1 결정으로 선정되었습니다.<br/>최종 스크립트를 확정하고 배포하십시오.
                                </p>
                                <button class="w-full py-4 bg-slate-900 border border-rose-500/50 hover:bg-rose-500 text-rose-500 hover:text-white text-xs font-black rounded-2xl transition-all uppercase tracking-widest active:scale-95 shadow-lg shadow-rose-500/5">
                                    Approve & Publish
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

    } catch (err) {
        container.innerHTML = `<div class="p-8 text-red-500 bg-red-500/10 rounded-xl border border-red-500/20">Content Studio Data Error: ${err.message}</div>`;
    }
}

function getActionColorClass(action) {
    const mapping = {
        'WATCH': 'text-slate-500',
        'EARLY_ENTRY': 'text-blue-500',
        'ACCUMULATE': 'text-emerald-500',
        'HOLD': 'text-amber-500',
        'DISTRIBUTE': 'text-orange-500',
        'EXIT': 'text-red-500'
    };
    return mapping[action] || 'text-slate-400';
}

function getRiskColorClass(level) {
    const mapping = {
        'LOW': 'text-emerald-500',
        'MEDIUM': 'text-amber-500',
        'HIGH': 'text-red-500'
    };
    return mapping[level] || 'text-slate-400';
}
