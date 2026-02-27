/**
 * router.js - Simple hash-based router for HoinInsight UI
 * Handles switching between Operator Dashboard views.
 */
class Router {
    constructor() {
        this.routes = {
            '': 'operator',
            'operator': 'operator',
            'video': 'video'
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
        const sidebar = document.getElementById('registry-sidebar');

        if (!operatorView) {
            console.error('[Router] View container not found');
            return;
        }

        if (route === 'video') {
            operatorView.style.display = 'block';
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
