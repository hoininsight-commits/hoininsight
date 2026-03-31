/**
 * legacy_adapter.js
 * PURE mapping logic for legacy UI compatibility.
 */
const LegacyAdapter = {
    adapt(key, payload) {
        if (!payload) return null;

        switch (key) {
            case 'hero_summary':
                return {
                    title: payload.headline || "오늘의 리포트",
                    bullets: Array.isArray(payload.why_now) ? payload.why_now : [],
                    note: payload.risk_note || ""
                };
            case 'operator_main_card':
                return {
                    headline: payload.hero?.headline || "",
                    oneLiner: payload.hero?.one_liner || "",
                    threeEye: payload.three_eye || []
                };
            case 'schedule_risk_calendar_90d':
            case 'schedule_risk_calendar_180d':
                return {
                    events: Array.isArray(payload.items) ? payload.items : []
                };
            default:
                return payload; // Pass-through for standard JSON
        }
    }
};

window.LegacyAdapter = LegacyAdapter;
