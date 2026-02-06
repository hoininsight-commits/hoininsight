/**
 * router.js - Simple hash-based router for HoinInsight UI
 * Handles switching between Operator Dashboard and Legacy View.
 */
class Router {
    constructor() {
        this.routes = {
            '': 'operator',
            'operator': 'operator',
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

        if (route === 'legacy') {
            operatorView.style.display = 'none';
            legacyView.style.display = 'block';
            if (sidebar) sidebar.style.display = 'none';
            document.body.style.paddingLeft = '0';

            // Trigger legacy load if needed
            if (typeof initLegacyView === 'function') {
                initLegacyView();
            }
        } else {
            operatorView.style.display = 'block';
            legacyView.style.display = 'none';
            if (sidebar) {
                sidebar.style.display = 'block';
                document.body.style.paddingLeft = '240px';
            }
        }
    }
}

window.router = new Router();
window.addEventListener('DOMContentLoaded', () => window.router.init());
