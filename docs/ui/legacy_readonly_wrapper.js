/**
 * legacy_readonly_wrapper.js
 * Adds a read-only banner to legacy views.
 */
function initLegacyReadonlyWrapper() {
    const legacyContainer = document.getElementById('legacy-view');
    if (!legacyContainer) return;

    // Check if banner already exists
    if (document.getElementById('legacy-readonly-banner')) return;

    const banner = document.createElement('div');
    banner.id = 'legacy-readonly-banner';
    banner.style.background = '#fef3c7';
    banner.style.color = '#92400e';
    banner.style.padding = '10px 20px';
    banner.style.textAlign = 'center';
    banner.style.borderBottom = '1px solid #f59e0b';
    banner.style.fontSize = '0.9rem';
    banner.style.fontWeight = '700';
    banner.style.position = 'sticky';
    banner.style.top = '0';
    banner.style.zIndex = '2000';

    const today = new Date().toISOString().split('T')[0];
    banner.innerHTML = `⚠️ 레거시 메인(읽기 전용) — 운영 동선은 <a href="#" style="color: #0369a1; text-decoration: underline;">신규 운영자 UI</a>를 사용하세요. [기준일: ${today}]`;

    legacyContainer.prepend(banner);

    // Disable potential interactive elements in legacy content
    const buttons = legacyContainer.querySelectorAll('button:not(.nav-back)');
    buttons.forEach(btn => {
        btn.disabled = true;
        btn.style.opacity = '0.5';
        btn.style.cursor = 'not-allowed';
        btn.title = "읽기 전용 모드에서는 비활성화됩니다.";
    });
}

// Export to window for router
window.initLegacyView = initLegacyReadonlyWrapper;
