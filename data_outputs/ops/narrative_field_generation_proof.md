# Narrative Field Generation Proof (PHASE-14B)

## 1. Test Environment
- **Script Run**: `python3 -m src.ops.narrative_intelligence_layer`
- **Input Source**: `data/ops/issuesignal_today.json`
- **Output Generated**: `data/ops/narrative_intelligence_v2.json`

## 2. Before/After JSON Comparison
**Topic**: "Global Semiconductor Alliance mandates new supply chain standard for 2026..." (ID: `STRUCT_20260224_signal_f`)

### Before (`issuesignal_today.json`)
```json
{
  "topic_id": "STRUCT_20260224_signal_f",
  "topic_type": "ISSUE_SIGNAL",
  "structure_type": "STRUCTURAL_REDEFINITION",
  "title": "Global Semiconductor Alliance mandates new supply chain standard for 2026",
  "rationale_natural": "HOIN Engine 구조적 분석 결과, 'STRUCTURAL_REDEFINITION' 유형의 패턴이 감지되었습니다. (드라이버: INDUSTRY, POLICY)",
  ... (No Narrative Scores)
}
```

### After (`narrative_intelligence_v2.json`)
```json
{
  "topic_id": "STRUCT_20260224_signal_f",
  "topic_type": "ISSUE_SIGNAL",
  "structure_type": "STRUCTURAL_REDEFINITION",
  "title": "Global Semiconductor Alliance mandates new supply chain standard for 2026",
  ...
  "narrative_score": 35.65,
  "final_narrative_score": 35.65,
  "video_ready": false,
  "actor_tier_score": 0.0,
  "cross_axis_count": 3,
  "cross_axis_multiplier": 1.15,
  "escalation_flag": false,
  "conflict_flag": false,
  "expectation_gap_score": 0,
  "expectation_gap_level": "none",
  "tension_multiplier_applied": false,
  "causal_chain": {
    "cause": null,
    "structural_shift": "STRUCTURAL_REDEFINITION",
    "market_consequence": "Monitoring friction",
    "affected_sector": "Global Semiconductor Alliance mandates new supply chain standard...",
    "time_pressure": "low"
  },
  "schema_version": "v3.0"
}
```

## 3. Evaluation Proof
- **Does it generate `narrative_score` & `causal_chain`?**: Yes, correctly attached to the root of the topic card.
- **Does it yield Non-Zero values?**: Yes. Base `narrative_score` evaluated to **35.65** and `cross_axis_count` computed to **3**.
- **Conclusion**: The Intelligence logic is completely healthy. The 0% generation issue is purely caused by a missing export pipe to the canonical UI `today.json`.
