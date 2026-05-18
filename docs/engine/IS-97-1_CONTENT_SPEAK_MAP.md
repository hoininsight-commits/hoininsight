# IS-97-1 Content Speak Map Layer

This document defines the **Content Speak Map Layer**, which deterministically decides the production strategy for topics based on the engine's interpretation and speakability outputs.

## 1. Purpose

The Content Speak Map Layer bridges the gap between "what the engine discovered" and "how the content should be produced." it ensures that high-integrity signals are given appropriate weight (SHORT vs. LONG form) and that ambiguous signals are held for further observation.

---

## 2. Decision Matrix (Deterministic Rules)

### Rule A: Speakability Binding (DROP)
- If `speakability` == `DROP`:
    - `content_mode` = `HOLD`
    - `content_count` = 0
    - `blocked_reason` = `drop_note` (from IS-96-3)

### Rule B: READY Routing
If `speakability` == `READY`:
- **SHORT**: Narrative skeleton exists with HOOK + CLAIM + 3 EVIDENCE.
- **LONG**: `interpretation_units` contains multi-sector links OR `flow_rotation` is confirmed.
- **COMBO (SHORT + LONG)**: `policy_execution_gap` <= 0.2 AND `pretext_score` >= 0.9.

### Rule C: HOLD Routing
If `speakability` == `HOLD`:
- `content_mode` = `HOLD`
- `content_count` = 1
- `primary_angle` = "관찰 중: 트리거 대기"
- `supporting_angles` must include `hold_trigger` (from IS-96-3).

---

## 3. Input & Output Asset

### Input Assets (from IS-96-4)
- `data/decision/interpretation_units.json`
- `data/decision/speakability_decision.json`
- `data/decision/narrative_skeleton.json`

### Output Asset
- **File**: `data/decision/content_speak_map.json`
- **Schema**:
```json
{
  "topic_id": "string",
  "speakability": "READY | HOLD | DROP",
  "content_mode": "SHORT | LONG | HOLD",
  "content_count": number,
  "primary_angle": "string",
  "supporting_angles": ["string"],
  "why_now_hook": "string",
  "blocked_reason": "string | null"
}
```

---

## 4. Governance Rule

This layer must NOT use LLMs. All logic is based on metric thresholds and tag existence checks. It defines the "What" and "How much," not the "Script content" itself.
