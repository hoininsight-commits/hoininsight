# Catalyst Event Sensing Layer (IS-95-2)

This layer enables the sensing of corporate and regulatory events that act as catalysts for market movement. It expands the "Economic Hunter" observation scope beyond macro signals.

## 1. Sensing Tags (CATALYST_EVENT Family)

| Tag | Description | Trigger Example |
| :--- | :--- | :--- |
| `US_MA_RUMOR` | M&A or merger rumors | Reputable IR/News feeds mentioning "merger", "acquisition", "rumor" |
| `US_SEC_FILING` | SEC Item-level triggers | 8-K Items 1.01 (Entry into Material Agreement), 5.02, etc. |
| `US_CONTRACT_AWARD` | Major contract awards | Gov agency announcements (NASA, DoD) or press releases |
| `US_REGULATORY_APPROVAL` | Regulatory milestones | FCC equipment authorization, FAA flight approvals |
| `KR_DART_DISCLOSURE` | DART major triggers | 유상증자, 지분 양수도, 경영권 변경 |
| `KR_KRX_DISCLOSURE` | KRX disclosure triggers | 조회공시, 상장폐지 우려, 단기과열 |
| `EXEC_STATEMENT` | Executive statements | CEO blog posts, Earnings Call "Future Outlook" sections |

## 2. Classification Logic (Deterministic)

### Confidence Levels
- **A (High)**: Official filing (SEC/DART) or agency announcement.
- **B (Medium)**: Official company press release or reputable "Sources say" from whitelisted nodes.
- **C (Low)**: Single-source rumor or mentions without primary confirmation.

### Why-now Hints
- **Schedule-driven**: Related to known earnings dates, regulatory deadlines, or announced auctions.
- **State-driven**: Unexpected filings (8-K), sudden rumors, or emergency interventions.
- **Hybrid-driven**: Rumors ahead of a scheduled meeting or approval window.

## 3. Data Flow
1. **Collector**: Fetches RSS/Public JSON feeds.
2. **Mapper**: Matches keywords against `catalyst_source_registry_v1.yml`.
3. **Extractor**: Regex-based entity (TICKER/Entity Name) isolation.
4. **Output**: `data/ops/catalyst_events.json`.

## 4. Governance
- No LLM used for extraction or classification.
- Metadata is strictly derived from source text and registry rules.
- Add-only approach: New collector is registered as an additional pipeline step.
