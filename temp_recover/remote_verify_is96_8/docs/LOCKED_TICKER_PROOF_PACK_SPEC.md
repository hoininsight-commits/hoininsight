# Locked Ticker Proof Pack Specification (IS-30)

## 1. Overview
A "Proof Pack" is a set of hard facts that justify why a specific ticker is an irreplaceable bottleneck owner for a given issue. To achieve "Economic Hunter-grade" authority, every locked ticker must be supported by at least **2 independent hard facts** from reliable sources.

## 2. Hard Fact Structure
Each fact in the proof pack must contain:
- **fact_type**: `CONTRACT` | `REGULATION` | `CERTIFICATION` | `DELIVERY` | `CAPEX` | `EARNINGS_STRUCTURAL` | `GOVERNMENT_DOC` | `OFFICIAL_GUIDANCE`
- **fact_claim**: A concise statement of the verified fact.
- **source_kind**: `GOV` | `FILING` | `EARNINGS_CALL` | `OFFICIAL_PRESS` | `DATA_PROVIDER` | `COURT_DOC` | `REGULATOR` | `INDUSTRY_ASSOC`
- **source_ref**: File path or URL to the source artifact.
- **source_date**: Date of the source (YYYY-MM-DD).
- **independence_key**: A unique key (e.g., hash of the source document) to ensure that two facts are not just re-quotes of the same source.

## 3. PASS / FAIL Rules
- **Minimum Requirements**: Each ticker must have $\ge 2$ hard facts.
- **Independence Rule**: At least 2 facts must have different `independence_key` AND different `source_kind` (OR different `source_ref` if kinds are similar but entities are different).
- **Derivation**: All data must be derived from local HoinEngine/IssueSignal artifacts. No external search or general knowledge allowed during the proof pack assembly.

## 4. Operational Enforcement
- If a ticker fails the proof requirement, it is removed from the decision candidate.
- If $0$ tickers remain for a candidate, the entire issue is **REJECTED** with `NO_PROOF_TICKER`.
- If an issue was `TRUST_LOCKED` but lacks proof packs for its tickers, it must be downgraded to **HOLD** with `NEED_PROOF_PACK`.
