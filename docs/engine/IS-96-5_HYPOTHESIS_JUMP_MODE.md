# IS-96-5: Hypothesis Jump Mode

This mode enables the HOIN Engine to generate interpretation units and narrative candidates triggered by high-impact catalyst events, even in the absence of significant quantitative anomalies.

## 1. Core Logic
When a `CATALYST_EVENT` is detected, the engine "jumps" to a hypothesis by constructing a deterministic reasoning chain.

### Reasoning Chain Schema
- **Trigger Event**: The specific catalyst (e.g., M&A rumor, SEC filing).
- **Mechanism**: How the event translates to sector impact (e.g., "Supply chain bottleneck shift").
- **Affected Layer**: Which structural segment is impacted (e.g., "TECH_INFRA").
- **Beneficiaries/Risks**: Strategic winners and losers.
- **Verification Checklist**: 3+ data points required to graduate from hypothesis to fact.

## 2. Speakability Mapping (Deterministic)

| Status | Condition |
| :--- | :--- |
| **READY** | Source is whitelisted AND (Official Filing/Press Release OR >=2 independent sources) |
| **HOLD** | Single-source rumor OR unverified "sources say" from reputable nodes |
| **DROP** | Untrusted source domain OR missing mandatory reasoning fields |

## 3. Narrative Hook Style
Hypothesis-mode narratives use a specific framing to maintain intellectual honesty:
- **Style**: "지금은 '확정'이 아니라 '가능성'이다" (Now is about potential, not certainty)
- **Example**: "[HYPOTHESIS] SpaceX의 xAI 인수설이 촉발할 AI 인프라 재편 가능성을 가설로 진단합니다."

## 4. Implementation Details
- Module: `src/topics/interpretation/hypothesis_jump_mode.py`
- Integration: Add-only extension to `DecisionAssembler`.
