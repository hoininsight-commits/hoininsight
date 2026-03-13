# Source Diversity & Independence Specification (IS-32)

## 1. Overview
The Source Diversity Layer prevents "Wire Copy chains" or "Circular Reporting" from passing as independent proof. It groups evidence artifacts into `SourceClusters` based on their canonical origin (e.g., all Reuters reprints are one cluster, etc.).

## 2. Source Clustering Rules

### Canonicalizer logic
- **Wire Chain**: If a source cites another source (e.g., "Reuters reports via X"), it belongs to the `Reuters` cluster.
- **Corporate Parent**: If multiple URLs belong to the same parent media group (e.g., WSJ and Dow Jones), they map to the same `ClusterID`.
- **Domain mirroring**: Different domains hosting the exact same PDF artifact map to the same cluster.

### Cluster Enums
- `OFFICIAL`: Government ministries, Central Banks, SEC/KRX filings.
- `MAJOR_MEDIA`: Reuters, Bloomberg, WSJ, Financial Times.
- `MARKET_DATA`: FRED, ECOS, Yahoo Finance.
- `GENERAL_NEWS`: Local news, blogs, smaller outlets.
- `SOCIAL_INFLUENCER`: YouTube analysts, X accounts.

## 3. Enforcement Logic
- **Fact Proof (Ticker Level)**: 2 independent hard facts must belong to **2 different Clusters**.
- **Quote Proof (Signal Level)**:
  - 1 `OFFICIAL` cluster $\implies$ **PASS**.
  - 2 `MAJOR_MEDIA` independent clusters $\implies$ **PASS**.
  - Repetitive same-cluster findings $\implies$ `REJECT:WIRE_CHAIN_DUPLICATION` or `HOLD:CLUSTER_COLLISION`.

## 4. Audit JSON Schema (`source_diversity_audit.json`)
```json
{
  "timestamp": "2026-01-30T00:00:20Z",
  "topic_id": "IS-XXXX",
  "audit_trail": [
    {
      "artifact_ref": "news_reuters_001.json",
      "found_origin": "Reuters",
      "cluster_id": "REUTERS_WIRE",
      "reason": "Explicit citation found in text."
    }
  ],
  "distinct_cluster_count": 2,
  "final_verdict": "PASS"
}
```
