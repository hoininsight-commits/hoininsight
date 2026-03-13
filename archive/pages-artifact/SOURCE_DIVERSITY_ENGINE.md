# SOURCE DIVERSITY ENGINE (IS-32)

## Purpose
The Source Diversity Engine ensures that IssueSignal evidence is truly independent. It prevents the engine from treating derived content (syndication, wire copies, press release echoes) as multiple independent facts.

## Core Rules

### 1. Canonicalization
All sources are passed through the `SOURCE_CANONICALIZER`. This collapses:
- Same URL (ignoring UTM parameters and query strings).
- Mirror sites hosting the same official document identifier (e.g., SEC Accession No).
- Duplicate headlines from the same publisher on the same day.

### 2. Dependency Chain Detection
The `DEPENDENCY_CHAIN_DETECTOR` classifies evidence as **ORIGINAL** or **DERIVED**.
- **ORIGINAL**: The root source (e.g., a press release on an official gov site, a primary interview).
- **DERIVED**: Content that cites or syndicates another source (e.g., "Reuters reports...", "보도자료에 따르면").

### 3. Diversity Enforcement
To achieve a **PASS** status for evidence (Facts or Quotes), the evidence set must meet the following:
- **Cluster Diversity**: At least **2 independent origin clusters** (distinct root events).
- **Family Diversity**: At least **2 different source type families**:
  - `OFFICIAL` (Gov portals, Central Banks)
  - `REGULATORY` (SEC, Financial regulators)
  - `FILINGS` (Company reports)
  - `TRANSCRIPT` (Earnings calls, Speeches)
  - `MARKET_DATA` (Direct exchange data)
  - `MAJOR_MEDIA` (Primary news reports)

## Reason Codes

| Code | Description | Verdict |
|------|-------------|---------|
| `LACK_SOURCE_DIVERSITY` | Less than 2 clusters or families found. | HOLD |
| `WIRE_CHAIN_DUPLICATION` | Multiple items detected as derived from the same wire service. | HOLD |
| `SINGLE_ORIGIN_CIRCULAR` | Sources are citing each other in a loop without a new root fact. | REJECT |

## Examples

### [HOLD] Wire Chain
1. News A: "Reuters: Fed may hike rates."
2. News B: "According to Reuters, Fed considers hike."
- Result: 1 Cluster (Reuters). **FAIL**.

### [PASS] Diverse Evidence
1. Official Fed Statement (OFFICIAL)
2. WSJ Interview with Fed Official (MAJOR_MEDIA)
- Result: 2 Clusters, 2 Families. **PASS**.
