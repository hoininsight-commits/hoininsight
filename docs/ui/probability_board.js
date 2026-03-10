/**
 * probability_board.js - UI Component for Topic Probability Ranking
 */

export function renderProbabilitySection(data) {
    if (!data || !data.ranked_candidates || data.ranked_candidates.length === 0) return '';

    return `
        <div id="probability-board" class="space-y-4 mb-8">
            <h3 class="text-[9px] font-black text-slate-600 uppercase tracking-[0.4em] px-1 mb-2 flex items-center gap-2">
                <span>Topic Probability Ranking Board</span>
                <div class="h-[1px] bg-slate-800 flex-1"></div>
            </h3>
            <div class="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden">
                <div class="p-1 space-y-1">
                    ${data.ranked_candidates.map((candidate, idx) => renderProbabilityItem(candidate, idx === 0)).join('')}
                </div>
            </div>
        </div>
    `;
}

function renderProbabilityItem(candidate, isTop) {
    const score = Math.round(candidate.probability_score);
    const barWidth = `${score}%`;
    const bgColor = isTop ? 'bg-blue-600/20' : 'bg-black/20';
    const borderColor = isTop ? 'border-blue-500/30' : 'border-slate-800/50';
    const accentColor = isTop ? 'bg-blue-500' : 'bg-slate-500';
    const textColor = isTop ? 'text-white' : 'text-slate-300';

    return `
        <div class="${bgColor} border ${borderColor} rounded-lg p-4 flex gap-6 items-center group hover:bg-slate-800/40 transition-colors">
            <div class="flex flex-col items-center justify-center min-w-[40px]">
                <div class="text-[9px] font-black text-slate-500 uppercase tracking-widest">RANK</div>
                <div class="text-xl font-black ${isTop ? 'text-blue-500' : 'text-slate-700'}">#${candidate.rank}</div>
            </div>
            
            <div class="flex-1 space-y-2">
                <div class="flex justify-between items-start">
                    <div>
                        <div class="text-[8px] font-black text-slate-500 uppercase tracking-widest mb-1">${candidate.theme}</div>
                        <h4 class="text-[14px] font-black ${textColor} leading-tight">${candidate.potential_topic}</h4>
                    </div>
                    <div class="text-right">
                        <div class="text-[16px] font-black ${isTop ? 'text-blue-400' : 'text-slate-400'}">${score}%</div>
                        <div class="text-[9px] font-black text-slate-600 uppercase">Probability</div>
                    </div>
                </div>
                
                <div class="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                    <div class="h-full ${accentColor} rounded-full transition-all duration-1000" style="width: ${barWidth}"></div>
                </div>

                <div class="flex gap-4 pt-1">
                    <div class="flex flex-wrap gap-1">
                        ${(candidate.supporting_factors || []).map(f => `
                            <span class="text-[9px] text-slate-500 px-1.5 py-0.5 rounded-sm bg-black/40 border border-slate-800/50 flex items-center gap-1">
                                <span class="text-blue-500/50">✔</span> ${f}
                            </span>
                        `).join('')}
                    </div>
                </div>
            </div>
        </div>
    `;
}
