# IS-97-3 Script Realization Layer

This document defines the **Script Realization Layer**, which assembles structural data and communicative intent into finalized script sentences.

## 1. Purpose

The Script Realization Layer transforms the metadata from the Interpretation, Speakability, and Persona Lock layers into actual communicative content. It follows a strict "Template + Data" approach to ensure determinism and prevent hallucinations.

---

## 2. Assembly Templates

### 2-1. HOOK Templates
- **SHORT**: "님들, 지금 {topic_title} 이슈에서 시장이 진짜 무서워하는 건 {root_cause}야."
- **LONG**: "오늘은 {topic_title}을 '왜 지금인가' 관점에서 데이터로만 정리할게. 핵심은 {root_cause}다."
- **MONITORING**: "지금은 {topic_title}이 확정 구간이 아니라 '조건 대기' 구간이야. 트리거만 확인하면 된다."

### 2-2. CLAIM Templates
- **STRUCTURAL**: "이건 단기 뉴스가 아니라 구조 변화다. {pretext_judgement} + {flow_pattern} 조합이 근거다."
- **DATA_VALIDATED**: "숫자가 확인됐다. {earnings_key_point}가 핵심 증거다."
- **PRECONDITIONED**: "이슈는 진행 중이지만 조건이 완성되려면 {hold_trigger}가 필요하다."

---

## 3. Evidence & Checklist Rules

### 3-1. EVIDENCE_3
Prioritizes the following from `interpretation_units`:
1. `EARNINGS_VERIFY` values.
2. `KR_POLICY` or `GLOBAL_INDEX` milestone dates.
3. `FLOW_ROTATION` patterns.

### 3-2. CHECKLIST_3
Format: `n. "지표 {tag}: {what_to_check} — {pass_condition}"`

---

## 4. Governance Rule (Add-only)

This layer produces `data/decision/script_realization.json`. It does NOT modify any existing logic or constitutional documentation. It is strictly deterministic with no LLM dependency.
