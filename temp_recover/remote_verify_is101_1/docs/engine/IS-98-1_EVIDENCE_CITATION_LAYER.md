# IS-98-1 Evidence Citation Layer

This document defines the **Evidence Citation Layer**, which ensures all claims are backed by verifiable official sources or qualified with cautionary language.

## 1. Citation Status Logic

Each evidence piece is assigned a status based on matching with `registry/sources/source_registry_v1.yml`:

- **VERIFIED**: At least one source matches the `evidence_tag` and keyword criteria.
- **PARTIAL**: Match exists but coverage is incomplete (Reserved for future complex logic).
- **UNVERIFIED**: No matching source found in the registry.

---

## 2. Tone Guard Mechanism (Automatic Downshifting)

If any claim in a topic is marked as **UNVERIFIED**, the corresponding script sentences must avoid assertive language.

### 2-1. Transformation Rules
- **Assertive (READY)**: "~으로 밝혀졌다", "~이다"
- **Cautionary (UNVERIFIED Guard)**: "~로 해석된다", "~ 가능성이 있다", "~ 관찰 중이다"

The results are saved to `data/decision/script_with_citation_guard.json`.

---

## 3. Governance Rule (Add-only)

This layer follows the **Add-only** principle. It creates new decision assets (`evidence_citations.json`, `script_with_citation_guard.json`) without modifying existing logic or constitutional documentation.
