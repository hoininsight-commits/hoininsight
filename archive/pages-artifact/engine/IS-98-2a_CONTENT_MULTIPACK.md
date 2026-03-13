# IS-98-2a Multi-Pack Layer

This document defines the **Multi-Pack Layer**, which bundles daily content into a single distribution package consisting of 1 Long-form item and up to 4 Shorts items.

## 1. Selection Rules (Deterministic Score)

Candidates from `content_pack.json` are ranked based on the following score:
- **Base**: `READY` status (+100)
- **Citations**: +1 per `VERIFIED` source.
- **Mentionables**: +10 for presence of stocks.
- **Complexity**: +20 if multiple interpretation units are linked.

## 2. Partitioning

### 2-1. Long-form (1 item)
- The highest scoring item.
- **Prerequisite**: Must be `READY` and have at least 3 citations OR 2+ mentionables.
- If the top item fails prerequisites, the next one is evaluated.

### 2-2. Shorts (up to 4 items)
- Next 4 highest scoring items after Long-form selection.

## 3. Fallback & Promotion

If fewer than 5 `READY` items exist:
- `HOLD` items can be promoted if their `interpretation_key` contains high-impact keywords (e.g., "발표", "출시", "확정") and they have `PARTIAL`+ citations.
- Minimum package size is not forced; it's better to have fewer high-quality items than 5 low-quality.

---

## 4. Governance Rule (Add-only)

This layer follows the **Add-only** principle. It creates `data/decision/content_pack_multipack.json` without modifying any upstream logic or constitutional documentation.
