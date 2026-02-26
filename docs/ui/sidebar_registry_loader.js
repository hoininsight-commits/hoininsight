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

    // [REF-011] Fixed Navigation Links
    const navGroup = document.createElement('div');
    navGroup.style.marginBottom = '20px';

    const createNavLink = (text, href, icon) => {
        const link = document.createElement('a');
        link.href = href;
        link.innerHTML = `${icon} ${text}`;
        link.style.display = 'block';
        link.style.padding = '10px 12px';
        link.style.color = '#f8fafc';
        link.style.textDecoration = 'none';
        link.style.fontSize = '0.9rem';
        link.style.fontWeight = '600';
        link.style.borderRadius = '6px';
        link.onmouseover = () => link.style.background = '#1e293b';
        link.onmouseout = () => link.style.background = 'transparent';
        return link;
    };

    navGroup.appendChild(createNavLink('오늘의 운영자 메인', '#', '🏠'));
    navGroup.appendChild(createNavLink('영상 후보 (편집 회의)', '#video', '🎬'));
    sidebar.appendChild(navGroup);

    const divider = document.createElement('hr');
    divider.style.border = '0';
    divider.style.borderTop = '1px solid #1e293b';
    divider.style.margin = '10px 0 20px 0';
    sidebar.appendChild(divider);

    const stages = ["DECISION", "CONTENT", "SUPPORT"];
    stages.forEach(stage => {
        const stageAssets = manifest.assets.filter(a => a.stage === stage && a.exists);
        const stageOverflow = (manifest.overflow || []).filter(a => a.stage === stage && a.exists);

        if (stageAssets.length === 0 && stageOverflow.length === 0) return;

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

        const renderItem = (asset) => {
            const item = document.createElement('div');
            item.innerText = asset.title || 'Untitled Card';
            item.style.padding = '8px 12px';
            item.style.color = '#94a3b8';
            item.style.fontSize = '0.9rem';
            item.style.cursor = 'pointer';
            item.style.borderRadius = '4px';
            item.onmouseover = () => item.style.background = '#1e293b';
            item.onmouseout = () => item.style.background = 'transparent';
            item.onclick = () => {
                const target = document.getElementById(`card-${asset.key}`);
                if (target) target.scrollIntoView({ behavior: 'smooth' });
            };
            sidebar.appendChild(item);
        };

        stageAssets.forEach(renderItem);

        if (stageOverflow.length > 0) {
            const overflowBtn = document.createElement('div');
            overflowBtn.innerText = `... 더보기 (${stageOverflow.length})`;
            overflowBtn.style.padding = '4px 12px';
            overflowBtn.style.color = '#475569';
            overflowBtn.style.fontSize = '0.8rem';
            overflowBtn.style.cursor = 'pointer';
            overflowBtn.style.fontStyle = 'italic';

            const overflowContainer = document.createElement('div');
            overflowContainer.style.display = 'none';
            stageOverflow.forEach(asset => {
                const item = document.createElement('div');
                item.innerText = asset.title;
                item.style.padding = '4px 20px';
                item.style.color = '#64748b';
                item.style.fontSize = '0.85rem';
                item.style.cursor = 'pointer';
                item.onclick = () => {
                    const target = document.getElementById(`card-${asset.key}`);
                    if (target) target.scrollIntoView({ behavior: 'smooth' });
                };
                overflowContainer.appendChild(item);
            });

            overflowBtn.onclick = () => {
                const isHidden = overflowContainer.style.display === 'none';
                overflowContainer.style.display = isHidden ? 'block' : 'none';
                overflowBtn.innerText = isHidden ? '접기' : `... 더보기 (${stageOverflow.length})`;
            };

            sidebar.appendChild(overflowBtn);
            sidebar.appendChild(overflowContainer);
        }
    });

    document.body.style.paddingLeft = '240px';
    document.body.prepend(sidebar);
}

document.addEventListener('DOMContentLoaded', loadSidebarRegistry);
