# IS-97-4 Mentionables Layer

This document defines the **Mentionables Layer**, which links high-conviction topics to specific stocks using strict data-backed evidence.

## 1. Selection Conviction (Why-Must)

To prevent unbacked stock calls, a mentionable must satisfy at least **2 evidence points**:
- **Primary Evidence**: One from {`KR_POLICY`, `GLOBAL_INDEX`, `EARNINGS_VERIFY`}.
- **Secondary Evidence**: One from {`FLOW_ROTATION`, `PRETEXT_VALIDATION`, `ANOMALY_DETECTION`}.

If a topic matches a stock's trigger keywords but lacks this evidence combination, the stock is **restricted** and flagged with `insufficient_evidence`.

---

## 2. Deterministic Mapping

The layer uses `registry/mappings/mentionables_map_v1.yml` to identify candidate stocks based on keyword matches in the topic's root cause and interpretation units.

### 2-1. Why-Must Template Rules
- **Policy**: "정책/제도 집행이 {sector} 수요를 직접 만든다 → {name}는 그 수혜 포지션이다."
- **Index**: "지수/패시브 이벤트는 수급을 강제한다 → {name}는 {index_mechanism} 구간에서 수혜다."
- **Earnings**: "실적/현금흐름이 먼저 찍히는 쪽이 보상받는다 → {name}의 {metric}이 확인 구간이다."
- **Rotation**: "순환매는 '덜 오른 + 명분 있는' 쪽으로 이동한다 → {name}는 {rotation_slot}에 있다."

---

## 3. Governance Rule (Add-only)

This layer follows the **Add-only** principle. It creates `data/decision/mentionables.json` without modifying existing sensing or interpretive logic.
