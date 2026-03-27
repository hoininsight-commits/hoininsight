/**
 * operator_impact_map.js — Theme to Sector and Stock Mapping
 * Consolidates Mentionables Engine results, Investment Decisions & Performance.
 */

export async function initImpactMapView(container) {
    console.log('[ImpactMap] Initializing...');
    
    try {
        const response = await fetch(`data/ops/today_operator_brief.json?t=${Date.now()}`);
        if (!response.ok) throw new Error('Data brief not found');
        const brief = await response.json();
        const data = brief.impact_map;

        container.innerHTML = `
            <div class="animate-in fade-in slide-in-from-bottom-4 duration-700">
                <header class="flex justify-between items-center mb-10">
                    <div>
                        <h2 class="text-3xl font-black text-white tracking-tight flex items-center gap-3">
                            <span class="text-emerald-500 text-4xl">🗺️</span> Impact Map
                        </h2>
                        <p class="text-slate-500 text-sm font-medium mt-1 uppercase tracking-widest">Asset & Sector Sensitivity</p>
                    </div>
                </header>

                <div class="grid grid-cols-1 lg:grid-cols-4 gap-8">
                    <!-- Left: Sector Exposure List -->
                    <div class="lg:col-span-1 space-y-4">
                        <div class="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-4">Affected Sectors</div>
                        ${Object.entries(data.sector_status || {}).length > 0 ? Object.entries(data.sector_status).map(([sector, status]) => `
                            <div class="bg-[#161b22] border border-slate-800 rounded-xl p-4 flex justify-between items-center text-nowrap overflow-hidden">
                                <span class="text-[10px] font-black text-white uppercase tracking-tight truncate mr-2">${sector}</span>
                                <span class="px-2 py-0.5 bg-emerald-500/10 text-emerald-500 text-[9px] font-black rounded uppercase">${status}</span>
                            </div>
                        `).join('') : '<div class="text-slate-600 text-[10px] uppercase font-bold p-4 bg-slate-900/30 rounded-xl border border-slate-800/50">섹터 노출 없음</div>'}
                    </div>

                    <!-- Right: Stock Detail Table -->
                    <div class="lg:col-span-3">
                        <div class="bg-[#161b22] border border-slate-800 rounded-2xl overflow-hidden">
                            <div class="p-6 border-b border-slate-800 flex justify-between items-center bg-slate-900/20">
                                <h3 class="text-xs font-black text-white uppercase tracking-widest">Mentionable Stocks</h3>
                                <div class="text-[10px] font-bold text-slate-500 italic">Target Theme: ${data.theme}</div>
                            </div>
                            <div class="overflow-x-auto">
                                <table class="w-full text-left">
                                    <thead>
                                        <tr class="bg-slate-900/30 text-[10px] font-black text-slate-500 uppercase tracking-widest">
                                            <th class="px-6 py-4">Ticker</th>
                                            <th class="px-6 py-4">Name</th>
                                            <th class="px-6 py-4 text-center">Weight (%)</th>
                                            <th class="px-6 py-4 text-center">PnL (%)</th>
                                            <th class="px-6 py-4">Action</th>
                                            <th class="px-6 py-4 text-center">Conviction</th>
                                        </tr>
                                    </thead>
                                    <tbody class="divide-y divide-slate-800">
                                        ${(data.mentionable_stocks || []).map(stock => `
                                            <tr class="hover:bg-slate-800/20 transition-colors">
                                                <td class="px-6 py-4 font-black text-blue-400 text-xs tracking-tighter">${stock.ticker}</td>
                                                <td class="px-6 py-4 font-bold text-white text-xs whitespace-nowrap">${stock.name}</td>
                                                <td class="px-6 py-4 text-center">
                                                    <div class="text-[11px] font-black text-white">${stock.weight_pct !== undefined ? stock.weight_pct.toFixed(1) + '%' : '0.0%'}</div>
                                                </td>
                                                <td class="px-6 py-4 text-center">
                                                    <span class="px-2 py-1 rounded text-[10px] font-black ${stock.pnl >= 0 ? 'bg-emerald-500/10 text-emerald-500' : 'bg-red-500/10 text-red-500'}">
                                                        ${stock.pnl !== undefined ? (stock.pnl * 100).toFixed(1) + '%' : '0.0%'}
                                                    </span>
                                                </td>
                                                <td class="px-6 py-4">
                                                    <span class="px-2 py-1 ${getActionBgClass(stock.action)} ${getActionColorClass(stock.action)} text-[9px] font-black rounded uppercase border border-current/20">
                                                        ${stock.action || 'WATCH'}
                                                    </span>
                                                </td>
                                                <td class="px-6 py-4 text-center">
                                                     <div class="text-[10px] font-black text-white">${((stock.confidence || 0) * 100).toFixed(0)}%</div>
                                                </td>
                                            </tr>
                                        `).join('')}
                                        ${(!data.mentionable_stocks || data.mentionable_stocks.length === 0) ? `<tr><td colspan="7" class="px-6 py-12 text-center text-slate-600 text-xs font-black uppercase tracking-widest">분석 결과 종목 노출 없음</td></tr>` : ''}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

    } catch (err) {
        container.innerHTML = `<div class="p-8 text-red-500 bg-red-500/10 rounded-xl border border-red-500/20">Impact Map Data Error: ${err.message}</div>`;
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

function getActionBgClass(action) {
    const mapping = {
        'WATCH': 'bg-slate-500/10',
        'EARLY_ENTRY': 'bg-blue-500/10',
        'ACCUMULATE': 'bg-emerald-500/10',
        'HOLD': 'bg-amber-500/10',
        'DISTRIBUTE': 'bg-orange-500/10',
        'EXIT': 'bg-red-500/10'
    };
    return mapping[action] || 'bg-slate-800/50';
}
