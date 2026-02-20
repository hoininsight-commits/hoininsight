
/**
 * Operator UI v2.3 Shared Utilities
 * Features: Strict Safe Getters, Contract Normalization, Anti-Undefined Policy
 */

export const UI_SAFE = {
    /**
     * G1/PHASE 1: hard fail on undefined/null/empty
     */
    safeStr: (v, fallback = "-") => {
        const isMissing = v === undefined || v === null || v === "" ||
            String(v).toLowerCase() === "undefined" ||
            String(v).toLowerCase() === "null";
        return isMissing ? fallback : String(v);
    },

    safeNum: (v, fallback = 0) => {
        const n = parseFloat(v);
        return isNaN(n) ? fallback : n;
    },

    safeArr: (v) => {
        return Array.isArray(v) ? v : [];
    },

    safeISOTime: (v) => {
        if (!v || v === "-") return "-";
        // If it's already HH:MM
        if (/^\d{2}:\d{2}$/.test(v)) return v;
        // If it's ISO string
        try {
            const date = new Date(v);
            if (isNaN(date.getTime())) return "-";
            return date.toTimeString().substring(0, 5); // HH:MM
        } catch (e) {
            return "-";
        }
    },

    /**
     * Derive YYYY-MM-DD from selected_at
     */
    deriveDateFromSelectedAt: (selectedAt) => {
        if (!selectedAt || selectedAt === "-") return null;
        try {
            return selectedAt.split('T')[0];
        } catch (e) {
            return null;
        }
    }
};

/**
 * PHASE 2: Contract Normalization (ADD-ONLY at UI layer)
 */
export function normalizeDecision(raw) {
    if (!raw) return null;

    let rawTitle = UI_SAFE.safeStr(raw.title, "[Untitled]");
    const title = (rawTitle === "[Untitled]" || rawTitle.includes("[Unknown]"))
        ? "제목 미정 (데이터 보완 필요)"
        : rawTitle;
    const selected_at = UI_SAFE.safeStr(raw.selected_at, raw.timestamp || raw.created_at || "-");
    const date = UI_SAFE.safeStr(raw.date, UI_SAFE.deriveDateFromSelectedAt(selected_at) || "-");
    const why_now_type = UI_SAFE.safeStr(raw.why_now_type, raw.WHY_NOW_TRIGGER_TYPE || "-");
    const speakability = UI_SAFE.safeStr(raw.speakability, raw.speakability_decision || "-");
    const intensity = UI_SAFE.safeNum(raw.intensity, UI_SAFE.safeNum(raw.stress_score, 0) * 100);
    const summary = UI_SAFE.safeStr(raw.why_now_summary, raw.summary || "-");
    const anomaly_points = UI_SAFE.safeArr(raw.anomaly_points);
    const related_assets = UI_SAFE.safeArr(raw.related_assets);
    const content_hook = UI_SAFE.safeStr(raw.content_hook, "-");

    // Completeness check
    let incomplete = false;
    const missingFields = [];
    if (why_now_type === "-") { incomplete = true; missingFields.push("why_now_type"); }
    if (title === "[Untitled]") { incomplete = true; missingFields.push("title"); }
    if (selected_at === "-") { incomplete = true; missingFields.push("selected_at"); }

    const normalized = {
        ...raw, // Preserving raw fields but prioritizing normalized ones below
        title,
        selected_at,
        date,
        why_now_type,
        speakability,
        intensity,
        why_now_summary: summary,
        anomaly_points,
        related_assets,
        content_hook,
        incomplete,
        missingFields,
        display_badge: incomplete ? "DATA_INCOMPLETE" : why_now_type
    };

    return normalized;
}

/**
 * UI-level Assertion for DEV mode (PHASE 1-3)
 */
export function assertNoUndefined(text) {
    if (!text) return;
    const lower = String(text).toLowerCase();
    if (lower.includes("undefined") || lower.includes("null") && !lower.includes("nullish")) {
        console.error("UNDEFINED_DETECTED:", text);
        const banner = document.getElementById('debug-error-banner');
        if (banner) {
            banner.classList.remove('hidden');
            banner.innerText = `⚠ CRITICAL: UI contains [undefined/null] - "${text.substring(0, 30)}..."`;
        }
    }
}
