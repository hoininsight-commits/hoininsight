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
    const interactiveElements = legacyContainer.querySelectorAll('button, a:not([href="#"]), input');
    interactiveElements.forEach(el => {
        if (el.tagName === 'BUTTON') {
            el.disabled = true;
            el.style.opacity = '0.5';
            el.style.cursor = 'not-allowed';
        } else {
            el.style.pointerEvents = 'none';
            el.style.opacity = '0.5';
        }
        el.title = "레거시 화면에서는 실행/수정할 수 없습니다. (읽기 전용)";
    });
}

// Export to window for router
window.initLegacyView = initLegacyReadonlyWrapper;
