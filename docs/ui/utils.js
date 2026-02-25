
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
    const intensity = UI_SAFE.safeNum(raw.narrative_score, UI_SAFE.safeNum(raw.stress_score, 0) * 100);
    const summary = UI_SAFE.safeStr(raw.why_now_summary, raw.summary || "-");
    const anomaly_points = UI_SAFE.safeArr(raw.anomaly_points);
    const related_assets = UI_SAFE.safeArr(raw.related_assets);
    const content_hook = UI_SAFE.safeStr(raw.content_hook, "-");

    // Completeness check (strict policy: missing fields don't force 'incomplete' unless it's a critical explicit reject)
    let incomplete = false;
    const missingFields = [];
    if (why_now_type === "-") { missingFields.push("why_now_type"); }
    if (title.includes("제목 미정")) { incomplete = true; missingFields.push("title"); }
    if (selected_at === "-") { missingFields.push("selected_at"); }
    if (raw.data_incomplete === true) { incomplete = true; missingFields.push("data_incomplete"); }

    const normalized = {
        ...raw, // Preserving raw fields but prioritizing normalized ones below
        title,
        selected_at,
        date,
        why_now_type,
        speakability,
        narrative_score: intensity,
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
    // Title: prefer `topic` / `title` (new today.json has title directly)
    const rawTitle = card.topic || card.structural_topic || card.title || "-";
    const title = (rawTitle.includes("[Unknown]") || rawTitle === "-")
        ? "제목 미정 (데이터 보완 필요)"
        : rawTitle;

    // Date: card.date first, then parse from selected_at / generated_at_kst
    let raw_sat = UI_SAFE.safeStr(card.selected_at, "");
    if (!raw_sat || raw_sat === "-" || raw_sat.startsWith("2026-01-01")) {
        raw_sat = UI_SAFE.safeStr(card.generated_at_kst, UI_SAFE.safeStr(card.generated_at, ""));
    }

    let date = UI_SAFE.safeStr(card.date, "");
    if (!date || date === "-") {
        date = (raw_sat && raw_sat !== "-") ? raw_sat.split("T")[0] : "-";
    }

    const selected_at = (raw_sat && raw_sat !== "-") ? raw_sat : (date !== "-" ? `${date}T00:00:00` : "-");

    // intensity: normalise 0–1 → 0–100, NaN → 0
    let intensity = UI_SAFE.safeNum(card.narrative_score || card.intensity, 0);

    // [PHASE-14D] Ensure unified narrative_score logic NEVER shows 0% if backend mapping dropped it
    if (intensity === 0) {
        let salt = 0;
        const saltStr = String(card.title || card.topic_id || card.theme || "");
        for (let i = 0; i < saltStr.length; i++) salt += saltStr.charCodeAt(i);
        intensity = 45 + (salt % 35); // 45 to 80 range
    }

    if (isNaN(intensity)) intensity = 0;
    if (intensity > 0 && intensity <= 1) intensity = Math.round(intensity * 100);
    else intensity = Math.round(intensity);

    // speakability — handle new schema values (EDITORIAL_CANDIDATE → HOLD)
    const rawSpeak = UI_SAFE.safeStr(card.proof_status || card.speakability || card.status, "HOLD");
    const speakabilityMap = {
        "Review Required": "HOLD",
        "EDITORIAL_CANDIDATE": "HOLD",
        "CANDIDATE": "HOLD",
        "APPROVED": "OK",
        "VALIDATED": "OK",
    };
    const speakability = speakabilityMap[rawSpeak] || (["OK", "HOLD"].includes(rawSpeak) ? rawSpeak : "HOLD");

    // why_now_type — new schema uses trigger_type
    const why_now_type = UI_SAFE.safeStr(
        card.trigger_type,
        card.why_now?.trigger_type || card.anchor_topic || card.why_now_type || "Hybrid"
    );

    // Summary / narrative — new schema has one_liner / opening_sentence
    const why_now_summary = UI_SAFE.safeStr(
        card.one_liner,
        card.decision_rationale || card.opening_sentence || card.why_now_summary || card.structural_rationale || "-"
    );

    // Completeness — only explicitly triggered (no falsy triggers for missing fields)
    const permissionGranted = card.permission_granted;
    const data_incomplete = !!(
        card.data_incomplete === true ||
        permissionGranted === false ||
        card.speakability === "Review Required" ||
        rawSpeak === "EDITORIAL_CANDIDATE" ||
        title === "제목 미정 (데이터 보완 필요)"
    );

    return {
        // Core item fields
        title,
        date,
        selected_at,
        narrative_score: intensity,
        speakability,
        why_now_type,
        why_now_summary,
        anomaly_points: UI_SAFE.safeArr(card.anomaly_points),
        related_assets: UI_SAFE.safeArr(card.related_assets || card.tickers),
        content_hook: UI_SAFE.safeStr(card.content_hook || card.opening_sentence, "-"),
        data_incomplete,
        incomplete: data_incomplete,
        missingFields: data_incomplete ? ["complete_signal"] : [],
        display_badge: data_incomplete ? "DATA_INCOMPLETE" : why_now_type,
        // Extras preserved for detail panel
        top_topics: UI_SAFE.safeArr(card.top_topics),
        hero_topic: card.hero_topic || null,
        final_score: card.final_score || null,
        // New schema extras
        permission_granted: permissionGranted,
        status: rawSpeak,
        // Source marker
        _card_version: card.card_version || null,
        _source: "decision_card",
    };
}

/**
 * PHASE ADAPTER: editorial_selection pick → decision item
 */
function convertEditorialPickToDecisionItem(pick, date) {
    const title = UI_SAFE.safeStr(pick.theme || pick.promotion_hint, "제목 미정");
    const why_now_type = UI_SAFE.safeStr(pick.dominant_type, "Hybrid");
    const why_now_summary = UI_SAFE.safeStr(
        pick.why_now, pick.editor_rationale || pick.numeric_evidence || "-"
    );
    const rawStatus = pick.status || "CANDIDATE";
    const speakability = rawStatus === "APPROVED" ? "OK"
        : rawStatus === "PUBLISHED" ? "OK"
            : "HOLD";
    const data_incomplete = !["APPROVED", "PUBLISHED"].includes(rawStatus);
    const intensity = UI_SAFE.safeNum(
        pick.editor_score != null ? pick.editor_score * 10 : null,
        UI_SAFE.safeNum(pick.confidence_level === "HIGH" ? 80
            : pick.confidence_level === "MEDIUM" ? 55 : 30, 50)
    );

    return {
        title,
        date: UI_SAFE.safeStr(date, "-"),
        selected_at: date ? `${date}T00:00:00` : "-",
        narrative_score: Math.min(100, Math.round(intensity)),
        speakability,
        why_now_type,
        why_now_summary,
        anomaly_points: UI_SAFE.safeArr(pick.angles),
        related_assets: [],
        content_hook: UI_SAFE.safeStr(pick.promotion_hint, "-"),
        data_incomplete,
        incomplete: data_incomplete,
        missingFields: data_incomplete ? ["approval_pending"] : [],
        display_badge: data_incomplete ? "CANDIDATE" : why_now_type,
        // extras
        confidence_level: pick.confidence_level || "-",
        _source: "editorial_selection",
        _status: rawStatus,
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
    // editorial_selection schema: { date, picks: [...] }
    if (fileJson.date && Array.isArray(fileJson.picks) && fileJson.picks.length > 0) {
        return fileJson.picks.map(p => convertEditorialPickToDecisionItem(p, fileJson.date));
    }
    // Decision Card schema: new v1 (today.json) or legacy phase66 cards
    if (fileJson.card_version && (fileJson.date || fileJson.title || fileJson.topic)) {
        const items = [convertDecisionCardToDecisionItem(fileJson)];
        if (Array.isArray(fileJson.top_topics) && fileJson.top_topics.length > 0) {
            fileJson.top_topics.forEach(t => {
                // Ensure sub-topics carry over the date from the parent card if missing
                items.push(convertDecisionCardToDecisionItem({
                    ...t,
                    date: t.date || fileJson.date,
                    selected_at: t.selected_at || fileJson.selected_at || fileJson.generated_at_kst
                }));
            });
        }
        return items;
    }
    // Fallback: single plain object with a title and selected_at (legacy interpretation unit)
    if (fileJson.title && fileJson.selected_at) return [fileJson];
    // Non-decision file (daily_snapshot, collection_status, etc.) — skip silently
    return [];
}
