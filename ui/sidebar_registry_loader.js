/**
 * sidebar_registry_loader.js
 * Dynamically builds the sidebar based on docs/data/ui/manifest.json
 */
async function loadSidebarRegistry() {
    const MANIFEST_PATH = '../data/ui/manifest.json';
    const GITHUB_PAGES_MANIFEST = '/hoininsight/data/ui/manifest.json';

    async function fetchManifest() {
        for (const path of [GITHUB_PAGES_MANIFEST, MANIFEST_PATH]) {
            try {
                const res = await fetch(path);
                if (res.ok) return await res.json();
            } catch (e) { }
        }
        return null;
    }

    const manifest = await fetchManifest();
    if (!manifest || !manifest.assets) {
        console.warn('[Sidebar] Manifest not found or empty.');
        return;
    }

    const stageMap = {
        "DECISION": "오늘의 판단",
        "CONTENT": "컨텐츠 패키지",
        "SUPPORT": "보조 신호"
    };

    const sidebar = document.createElement('div');
    sidebar.id = 'registry-sidebar';
    sidebar.className = 'registry-sidebar';
    sidebar.style.position = 'fixed';
    sidebar.style.left = '0';
    sidebar.style.top = '0';
    sidebar.style.width = '240px';
    sidebar.style.height = '100vh';
    sidebar.style.background = '#0f172a';
    sidebar.style.borderRight = '1px solid #1e293b';
    sidebar.style.padding = '20px';
    sidebar.style.zIndex = '1000';
    sidebar.style.overflowY = 'auto';

    const title = document.createElement('h1');
    title.innerText = 'HOIN INSIGHT';
    title.style.fontSize = '1.2rem';
    title.style.fontWeight = '900';
    title.style.color = '#fff';
    title.style.marginBottom = '30px';
    sidebar.appendChild(title);

    const stages = ["DECISION", "CONTENT", "SUPPORT"];
    stages.forEach(stage => {
        const stageAssets = manifest.assets.filter(a => a.stage === stage && a.exists);
        if (stageAssets.length === 0) return;

        const groupTitle = document.createElement('div');
        groupTitle.innerText = stageMap[stage] || stage;
        groupTitle.style.fontSize = '0.75rem';
        groupTitle.style.color = '#64748b';
        groupTitle.style.textTransform = 'uppercase';
        groupTitle.style.letterSpacing = '0.05em';
        groupTitle.style.marginTop = '20px';
        groupTitle.style.marginBottom = '10px';
        groupTitle.style.fontWeight = '800';
        sidebar.appendChild(groupTitle);

        stageAssets.forEach(asset => {
            const item = document.createElement('div');
            item.innerText = asset.title;
            item.style.padding = '8px 12px';
            item.style.color = '#94a3b8';
            item.style.fontSize = '0.9rem';
            item.style.cursor = 'pointer';
            item.style.borderRadius = '4px';
            item.onmouseover = () => item.style.background = '#1e293b';
            item.onmouseout = () => item.style.background = 'transparent';
            item.onclick = () => {
                // Scroll to target card if exists, or just log
                console.log(`Navigating to ${asset.key}`);
            };
            sidebar.appendChild(item);
        });
    });

    document.body.style.paddingLeft = '240px';
    document.body.prepend(sidebar);
}

document.addEventListener('DOMContentLoaded', loadSidebarRegistry);
