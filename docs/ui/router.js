/**
 * router.js — Modular ES Router for HoinInsight Dashboard
 * Features: Lazy-loading Operator Views, Active State Tracking, Error Recovery
 */

export async function initRouter() {
    console.log('[Router] v2.8 Initializing...');
    window.addEventListener('hashchange', handleRoute);
    await handleRoute();
}

async function handleRoute() {
    const hash = window.location.hash || '#today';
    const app = document.getElementById('app');
    
    // 1. Update active state in sidebar
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === hash) link.classList.add('active');
    });

    // 2. Loading State
    app.innerHTML = `
        <div class="flex flex-col items-center justify-center h-[60vh] animate-in fade-in">
            <div class="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mb-4"></div>
            <p class="text-[10px] font-black text-slate-500 uppercase tracking-widest">Routing to ${hash.substring(1)}...</p>
        </div>
    `;

    try {
        switch (hash) {
            case '#today':
                const { initTodayView } = await import('./operator_today.js?v=' + Date.now());
                await initTodayView(app);
                break;
            case '#history':
                const { initHistoryView } = await import('./operator_history.js?v=' + Date.now());
                await initHistoryView(app);
                break;
            case '#system':
                const { initSystemView } = await import('./operator_system.js?v=' + Date.now());
                await initSystemView(app);
                break;
            case '#video':
                const { initVideoView } = await import('./operator_video.js?v=' + Date.now());
                await initVideoView(app);
                break;
            default:
                window.location.hash = '#today';
        }
    } catch (err) {
        console.error('[Router] Load Error:', err);
        app.innerHTML = `
            <div class="p-8 bg-red-500/10 border border-red-500/20 rounded-xl m-4 text-center">
                <div class="text-2xl mb-2">⚠</div>
                <div class="text-sm font-bold text-red-500 uppercase mb-1">Navigation Error</div>
                <div class="text-[10px] text-slate-500 font-mono">${err.message}</div>
                <button onclick="location.reload()" class="mt-4 px-4 py-1.5 bg-red-600 text-white text-[10px] font-black rounded uppercase hover:bg-red-500 transition-colors">Reload Dashboard</button>
            </div>
        `;
    }
}
