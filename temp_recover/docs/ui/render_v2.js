document.addEventListener('DOMContentLoaded', async () => {
    const BASE_PATH = '/hoininsight/data/';
    const LOCAL_DATA_PATH = '../data/';

    const safeText = (v) => v === undefined || v === null ? "" : String(v);
    const safeArray = (v) => Array.isArray(v) ? v : [];
    const safeObj = (v) => (v && typeof v === 'object' && !Array.isArray(v)) ? v : {};

    async function loadJson(file, isCritical = false) {
        const paths = [BASE_PATH + file, LOCAL_DATA_PATH + file];
        for (const path of paths) {
            try {
                const res = await fetch(path);
                if (!res.ok) continue;
                return await res.json();
            } catch (e) {
                console.warn(`[DATA] Fetch failed for ${path}: ${e.message}`);
            }
        }
        if (isCritical) console.error(`[CRITICAL] Missing: ${file}`);
        return null;
    }

    async function init() {
        console.log('[REF-004] V2 Renderer Initializing...');
        const manifest = await loadJson('ui/manifest.json', true);
        if (!manifest) return;

        const app = document.getElementById('app');
        if (!app) return;
        app.innerHTML = ''; // Clear for V2

        // 1. Render Active Assets
        for (const asset of manifest.assets) {
            await renderAssetEntry(asset, app, false);
        }

        // 2. Render Overflow (Collapsed by default)
        if (manifest.overflow && manifest.overflow.length > 0) {
            const overflowBanner = document.createElement('div');
            overflowBanner.className = 'overflow-banner';
            overflowBanner.innerHTML = `<hr style="border: 0.5px dashed #334155; margin: 60px 0 20px 0;">
                                       <div style="color: #475569; font-size: 0.8rem; text-align: center; margin-bottom: 20px;">
                                       보조 지표 및 추가 상세 리포트 (${manifest.overflow.length})
                                       </div>`;
            app.appendChild(overflowBanner);

            const overflowContainer = document.createElement('div');
            overflowContainer.id = 'overflow-content';
            overflowContainer.style.display = 'none';
            app.appendChild(overflowContainer);

            for (const asset of manifest.overflow) {
                await renderAssetEntry(asset, overflowContainer, true);
            }

            const toggleBtn = document.createElement('button');
            toggleBtn.innerText = '모든 보조 지표 보기';
            toggleBtn.className = 'badge';
            toggleBtn.style.display = 'block';
            toggleBtn.style.margin = '0 auto 40px auto';
            toggleBtn.style.cursor = 'pointer';
            toggleBtn.onclick = () => {
                const isHidden = overflowContainer.style.display === 'none';
                overflowContainer.style.display = isHidden ? 'block' : 'none';
                toggleBtn.innerText = isHidden ? '접기' : '모든 보조 지표 보기';
            };
            app.appendChild(toggleBtn);
        }
    }

    async function renderAssetEntry(asset, container, isOverflow) {
        if (!asset.exists) return;
        const data = await loadJson(asset.path);
        if (!data) return;

        const section = document.createElement('section');
        section.id = `card-${asset.key}`;
        section.className = 'ui-card-section';
        if (isOverflow) section.style.opacity = '0.8';

        const header = document.createElement('div');
        header.style.marginBottom = '15px';
        header.innerHTML = `<h2 style="color:#f8fafc; font-size:1.2rem; font-weight:800;">
                               <span style="color:#64748b; font-size:0.8rem; margin-right:8px;">${asset.stage}</span>
                               ${asset.title}
                           </h2>`;
        section.appendChild(header);

        const cardBody = document.createElement('div');
        cardBody.style.background = '#1e293b';
        cardBody.style.padding = '25px';
        cardBody.style.borderRadius = '12px';
        cardBody.style.border = '1px solid #334155';
        cardBody.style.color = '#cbd5e1';

        // Render JSON as pretty code for now (Constitution fallback)
        const code = document.createElement('pre');
        code.style.fontSize = '0.85rem';
        code.style.overflowX = 'auto';
        code.style.lineHeight = '1.4';
        code.innerText = JSON.stringify(data, null, 2);
        cardBody.appendChild(code);

        section.appendChild(cardBody);
        container.appendChild(section);
    }

    init();
});
