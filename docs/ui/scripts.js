/**
 * STEP-31 Auto Narrative Script View
 * Displays automatically generated 1-2 minute video scripts.
 */
import { fetchJSON } from './utils.js?v=31';

export async function initScriptView(container) {
    console.log("[ScriptView] Initializing...");
    if (!container) container = document.getElementById('main-content') || document.getElementById('app');
    if (!container) return;
    container.innerHTML = `<div class="p-8 text-slate-400 animate-pulse">Assembling Narrative Scripts...</div>`;

    try {
        const scripts = await fetchJSON('data/content/auto_scripts.json');

        if (!scripts || scripts.length === 0) {
            renderError(container, "No high-priority scripts generated. System requires TRACK/FOCUS signals to synthesize content.");
            return;
        }

        renderScripts(container, scripts);
    } catch (e) {
        console.error("[ScriptView] Error:", e);
        renderError(container, "Failed to load narrative scripts.");
    }
}

function renderScripts(container, scripts) {
    container.innerHTML = `
        <div class="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <!-- HEADER -->
            <div class="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-slate-800 pb-6">
                <div>
                    <h1 class="text-3xl font-black text-white tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-rose-500">
                        Auto Narrative Scripts
                    </h1>
                    <p class="text-slate-400 text-sm mt-1">AI-synthesized 1-2 minute video protocols for dominant narratives.</p>
                </div>
            </div>

            <!-- SCRIPTS GRID -->
            <div class="grid grid-cols-1 gap-12">
                ${scripts.map(s => renderScriptItem(s)).join('')}
            </div>
        </div>
    `;
}

function renderScriptItem(s) {
    const actionClass = s.action === 'FOCUS' ? 'text-emerald-400 border-emerald-500/50' : 'text-amber-400 border-amber-500/50';
    return `
        <div class="bg-slate-900 border border-slate-800 rounded-3xl overflow-hidden shadow-2xl">
            <!-- TOP STRIP -->
            <div class="bg-slate-800/50 px-8 py-4 flex justify-between items-center border-b border-slate-800">
                <div class="flex items-center gap-4">
                    <span class="text-xs font-black text-slate-500 uppercase tracking-widest">Protocol Content</span>
                    <h2 class="text-xl font-bold text-white uppercase tracking-tight">${s.theme}</h2>
                </div>
                <div class="flex items-center gap-3">
                    <span class="px-3 py-1 rounded-full text-[10px] font-black border ${actionClass}">${s.action}</span>
                    <span class="text-sm font-mono font-black text-slate-400">${s.action_score}</span>
                </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-5 h-full">
                <!-- SCRIPT BLOCKS (LATER-LEFT) -->
                <div class="lg:col-span-3 p-8 border-r border-slate-800 space-y-8 overflow-y-auto max-h-[70vh]">
                    ${renderBlock("HOOK (오프닝)", s.script.hook, "text-emerald-400")}
                    ${renderBlock("CONTEXT (배경)", s.script.context)}
                    ${renderBlock("WHY NOW (트리거)", s.script.why_now)}
                    ${renderBlock("EVIDENCE (데이터)", s.script.evidence)}
                    ${renderBlock("MARKET IMPACT (시장)", s.script.market_impact)}
                    ${renderBlock("OPERATOR INSIGHT (전략)", s.script.operator_insight, "text-rose-400")}
                    ${renderBlock("CLOSING (마무리)", s.script.closing)}
                </div>

                <!-- FULL TEXT (RIGHT) -->
                <div class="lg:col-span-2 bg-black/40 p-10 flex flex-col">
                    <div class="flex items-center justify-between mb-8">
                        <h3 class="text-xs font-black text-slate-500 uppercase tracking-widest">Teleprompter Full Text</h3>
                        <button onclick="navigator.clipboard.writeText(\`${s.script_full}\`)" class="text-[10px] font-bold text-emerald-500 hover:text-emerald-400 transition-colors uppercase">Copy Script</button>
                    </div>
                    <div class="text-lg leading-relaxed text-slate-300 font-medium whitespace-pre-wrap italic opacity-80 select-all selection:bg-emerald-500/30">
                        "${s.script_full}"
                    </div>
                    <div class="mt-auto pt-8 border-t border-slate-800/50 flex justify-between items-center">
                        <div class="text-[10px] font-bold text-slate-600">DURATION: ~1:45s</div>
                        <div class="text-[10px] font-bold text-slate-600">TONE: ECONOMIC HUNTER</div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function renderBlock(label, content, accent = "text-white") {
    return `
        <div class="space-y-2">
            <h4 class="text-[10px] font-black text-slate-500 uppercase tracking-widest">${label}</h4>
            <p class="text-sm leading-relaxed ${accent}">${content}</p>
        </div>
    `;
}

function renderError(container, msg) {
    container.innerHTML = `
        <div class="min-h-[60vh] flex flex-col items-center justify-center text-center p-8">
            <div class="w-20 h-20 bg-slate-800/50 rounded-full flex items-center justify-center mb-6 text-slate-500 border border-slate-700">
                <svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                </svg>
            </div>
            <h2 class="text-2xl font-black text-white mb-2 italic tracking-tight">Content Pipeline Idle</h2>
            <p class="text-slate-500 max-w-md mx-auto text-sm leading-relaxed">${msg}</p>
        </div>
    `;
}
