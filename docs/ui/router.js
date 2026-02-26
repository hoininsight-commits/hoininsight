/**
 * router.js - Simple hash-based router for HoinInsight UI
 * Handles switching between Operator Dashboard and Legacy View.
 */
class Router {
    constructor() {
        this.routes = {
            '': 'operator',
            'operator': 'operator',
            'video': 'video',
            'legacy': 'legacy'
        };
        window.addEventListener('hashchange', () => this.handleRoute());
    }

    init() {
        this.handleRoute();
    }

    handleRoute() {
        const hash = window.location.hash.replace('#', '') || '';
        const route = this.routes[hash] || 'operator';
        this.renderRoute(route);
    }

    renderRoute(route) {
        const operatorView = document.getElementById('operator-view');
        const legacyView = document.getElementById('legacy-view');
        const sidebar = document.getElementById('registry-sidebar');

        if (!operatorView || !legacyView) {
            console.error('[Router] View containers not found');
            return;
        }

    } else if(route === 'video') {
    operatorView.style.display = 'block';
    legacyView.style.display = 'none';
    if (sidebar) {
        sidebar.style.display = 'block';
        document.body.style.paddingLeft = '240px';
    }
    // Init Video View
    if (typeof initVideoView === 'function') {
        initVideoView();
    }
} else {
    operatorView.style.display = 'block';
    legacyView.style.display = 'none';
    if (sidebar) {
        sidebar.style.display = 'block';
        document.body.style.paddingLeft = '240px';
    }
    // Trigger main view render if needed
    if (typeof renderMainView === 'function') {
        renderMainView();
    }
}
    }
}

window.router = new Router();
window.addEventListener('DOMContentLoaded', () => window.router.init());
