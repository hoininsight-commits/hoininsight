/**
 * manifest_loader.js
 * Shared utility for loading manifest and assets safely.
 */
const ManifestLoader = {
    BASE_PATH: '/hoininsight/data/ui/',
    LOCAL_PATH: '../data/ui/',

    async fetchJson(file, isCritical = false) {
        const paths = [this.BASE_PATH + file, this.LOCAL_PATH + file];
        for (const path of paths) {
            try {
                const res = await fetch(path);
                if (res.ok) return await res.json();
            } catch (e) {
                console.warn(`[Loader] Failed for ${path}: ${e.message}`);
            }
        }
        if (isCritical) console.error(`[CRITICAL] Missing asset: ${file}`);
        return null;
    },

    async loadManifest() {
        return await this.fetchJson('manifest.json', true);
    },

    async loadAsset(assetPath) {
        // Path in manifest is like 'ui/hero_summary.json'
        // We need to resolve it relative to data/
        const fullPaths = [
            '/hoininsight/data/' + assetPath,
            '../data/' + assetPath
        ];

        for (const path of fullPaths) {
            try {
                const res = await fetch(path);
                if (res.ok) return await res.json();
            } catch (e) { }
        }
        return null;
    },

    normalizeText(x) {
        if (x === undefined || x === null || String(x).toLowerCase() === 'undefined' || String(x).toLowerCase() === 'null') return "";
        return String(x);
    },

    normalizeList(x) {
        return Array.isArray(x) ? x : [];
    },

    hasBadStrings(text) {
        const low = String(text).toLowerCase();
        return low.includes('undefined') || low === 'null' || low === 'nan';
    }
};

window.ManifestLoader = ManifestLoader;
