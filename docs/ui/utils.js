
/**
 * Operator UI v2.4 Shared Utilities
 * Features: Strict Safe Getters, Contract Normalization, Anti-Undefined Policy,
 *           Decision Card Schema Adapter (extractDecisions / convertDecisionCardToDecisionItem)
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

/**
 * PHASE ADAPTER: Decision Card → Decision Item
 * Maps final_decision_card.json (card_version schema) to the UI's expected item shape.
 */
export function convertDecisionCardToDecisionItem(card) {
    // Title: prefer `topic` (the real topic title), fallback to `title`
    const rawTitle = card.topic || card.structural_topic || card.title || "-";
    const title = (rawTitle.includes("[Unknown]") || rawTitle === "-")
        ? "제목 미정 (데이터 보완 필요)"
        : rawTitle;

    // Date: card.date first, then parse from selected_at / generated_at_kst
    let date = UI_SAFE.safeStr(card.date, null);
    if (!date || date === "-") {
        const ts = card.selected_at || card.generated_at_kst || null;
        date = ts ? (ts.split("T")[0] || "-") : "-";
    }

    // selected_at — skip the known dummy placeholder "2026-01-01T09:00:00"
    const raw_sat = card.selected_at || "";
    const isDummy = raw_sat.startsWith("2026-01-01");
    const fallbackTs = card.generated_at_kst || card.generated_at
        || (card.date ? `${card.date}T00:00:00` : raw_sat || "-");
    const selected_at = isDummy
        ? UI_SAFE.safeStr(fallbackTs, "-")
        : UI_SAFE.safeStr(raw_sat, fallbackTs || "-");

    // intensity: normalise 0–1 → 0–100
    let intensity = UI_SAFE.safeNum(card.intensity, 0);
    if (intensity > 0 && intensity <= 1) intensity = Math.round(intensity * 100);
    else intensity = Math.round(intensity);

    // speakability: "Review Required" is treated as incomplete
    const rawSpeak = UI_SAFE.safeStr(card.speakability, "HOLD");
    const speakability = rawSpeak === "Review Required" ? "HOLD" : rawSpeak;

    // why_now_type
    const why_now_type = UI_SAFE.safeStr(
        card.why_now?.trigger_type,
        card.anchor_topic || card.why_now_type || "Hybrid"
    );

    // Summary / narrative
    const why_now_summary = UI_SAFE.safeStr(
        card.decision_rationale,
        card.why_now_summary || card.structural_rationale || "-"
    );

    // Completeness
    const data_incomplete = !!(
        card.speakability === "Review Required" ||
        (card.title || "").includes("[Unknown]") ||
        !card.card_version
    );

    return {
        // Core item fields
        title,
        date,
        selected_at,
        intensity,
        speakability,
        why_now_type,
        why_now_summary,
        anomaly_points: UI_SAFE.safeArr(card.anomaly_points),
        related_assets: UI_SAFE.safeArr(card.related_assets),
        content_hook: UI_SAFE.safeStr(card.content_hook, "-"),
        data_incomplete,
        incomplete: data_incomplete,
        missingFields: data_incomplete ? ["complete_signal"] : [],
        display_badge: data_incomplete ? "DATA_INCOMPLETE" : why_now_type,
        // Extras preserved for detail panel
        top_topics: UI_SAFE.safeArr(card.top_topics),
        hero_topic: card.hero_topic || null,
        final_score: card.final_score || null,
        // Source marker
        _card_version: card.card_version || null,
        _source: "decision_card",
    };
}

/**
 * PHASE ADAPTER: Universal dispatch — file JSON → decisions array
 * Used by both operator_today.js and operator_history.js.
 * Never throws; always returns an array (possibly empty).
 */
export function extractDecisions(fileJson) {
    if (!fileJson) return [];
    // Already an array of decision items
    if (Array.isArray(fileJson)) return fileJson;
    // Object with a `.decisions` array
    if (Array.isArray(fileJson.decisions)) return fileJson.decisions;
    // Decision Card schema (card_version + date)
    if (fileJson.card_version && fileJson.date) {
        return [convertDecisionCardToDecisionItem(fileJson)];
    }
    // Fallback: single plain object with a title (legacy interpretation unit)
    if (fileJson.title) return [fileJson];
    // Non-decision file — skip silently
    return [];
}
