/**
 * legacy_render.js
 * manifest-only read strategy for legacy view.
 */
async function initLegacyViewFromManifest() {
    const container = document.getElementById('legacy-view');
    if (!container) return;

    // 1. Ensure read-only banner
    if (typeof initLegacyView === 'function') initLegacyView();

    const loader = window.ManifestLoader;
    const adapter = window.LegacyAdapter;

    if (!loader || !adapter) {
        console.error('[Legacy] Dependencies missing');
        return;
    }

    const contentArea = document.getElementById('legacy-content-placeholder');
    if (contentArea) contentArea.innerHTML = '<p>데이터를 불러오는 중...</p>';

    const manifest = await loader.loadManifest();
    if (!manifest) {
        if (contentArea) contentArea.innerHTML = '<p style="color:red;">⚠️ 매니페스트 부재: 렌더링 불가</p>';
        return;
    }

    if (contentArea) contentArea.innerHTML = ''; // Clear placeholder

    // Group by stage
    const grouped = { DECISION: [], CONTENT: [], SUPPORT: [] };
    manifest.assets.forEach(a => {
        if (grouped[a.stage]) grouped[a.stage].push(a);
    });

    for (const stage of ["DECISION", "CONTENT", "SUPPORT"]) {
        const assets = grouped[stage];
        if (assets.length === 0) continue;

        const stageTitle = document.createElement('h2');
        stageTitle.innerText = `[레거시] ${stage}`;
        stageTitle.style.borderBottom = '1px solid #ddd';
        stageTitle.style.paddingBottom = '5px';
        stageTitle.style.color = '#475569';
        container.appendChild(stageTitle);

        for (const asset of assets) {
            if (!asset.exists) continue;

            const payload = await loader.loadAsset(asset.path);
            const adapted = adapter.adapt(asset.key, payload);

            const card = document.createElement('div');
            card.style.background = '#fff';
            card.style.border = '1px solid #e2e8f0';
            card.style.padding = '15px';
            card.style.marginBottom = '20px';
            card.style.borderRadius = '5px';
            card.style.boxShadow = '0 1px 3px rgba(0,0,0,0.1)';

            card.innerHTML = `
                <div style="font-weight:bold; color:#1e293b; margin-bottom:10px;">${asset.title}</div>
                <pre style="font-size:0.8rem; background:#f8fafc; padding:10px; overflow-x:auto; border-radius:4px;">${JSON.stringify(adapted, null, 2)}</pre>
            `;
            container.appendChild(card);
        }
    }
}

// Ensure it loads if hash is legacy
window.addEventListener('DOMContentLoaded', () => {
    if (window.location.hash === '#legacy') {
        initLegacyViewFromManifest();
    }
});

// Register to window for router call
window.initLegacyView = initLegacyViewFromManifest;
