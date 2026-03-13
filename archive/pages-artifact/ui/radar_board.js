/**
 * radar_board.js - UI Component for Economic Hunter Radar
 */

export function renderRadarSection(data) {
    if (!data || !data.radar_candidates || data.radar_candidates.length === 0) return '';

    const getStrengthColor = (s) => {
        if (s === 'HIGH') return 'text-red-500 bg-red-500/10 border-red-500/20';
        if (s === 'MEDIUM') return 'text-orange-500 bg-orange-500/10 border-orange-500/20';
        return 'text-blue-400 bg-blue-400/10 border-blue-400/20';
    };

    return `
        <div id="radar-board" class="space-y-4 mb-8">
            <h3 class="text-[9px] font-black text-slate-600 uppercase tracking-[0.4em] px-1 mb-2 flex items-center gap-2">
                <span>Economic Hunter Radar Board</span>
                <div class="h-[1px] bg-slate-800 flex-1"></div>
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                ${data.radar_candidates.map(candidate => `
                    <div class="bg-slate-900/60 border border-slate-800 rounded-xl p-5 space-y-3 hover:border-slate-700 transition-colors group">
                        <div class="flex justify-between items-start">
                            <div class="text-[8px] font-black text-slate-500 uppercase tracking-widest">${candidate.theme}</div>
                            <span class="px-2 py-0.5 rounded border text-[8px] font-black uppercase ${getStrengthColor(candidate.signal_strength)}">
                                ${candidate.signal_strength}
                            </span>
                        </div>
                        <div class="space-y-1">
                            <h4 class="text-[13px] font-bold text-slate-200 leading-tight group-hover:text-blue-400 transition-colors">
                                ${candidate.potential_topic}
                            </h4>
                            <div class="text-[10px] text-slate-500 font-medium">Indicator: ${candidate.early_indicator}</div>
                        </div>
                        <div class="pt-2 border-t border-slate-800/50">
                            <div class="text-[8px] font-black text-slate-600 uppercase mb-1">Why Now</div>
                            <p class="text-[10px] text-slate-400 line-clamp-2 italic leading-relaxed">"${candidate.why_now}"</p>
                        </div>
                        <div class="flex justify-between items-center pt-1">
                            <span class="text-[8px] font-black text-slate-700 uppercase tracking-tighter">${candidate.signal_id}</span>
                            <span class="text-[9px] font-bold text-slate-500">Conf: ${candidate.confidence}</span>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}
