# Decision Card V2 Schema (IS-30)

## 1. Overview
The V2 schema extends the existing IssueSignal decision card to include atomic, verified proof packs for each ticker. This ensures that every recommendation is backed by traceable hard evidence.

## 2. New Fields (Additive)
In addition to the V1 fields (`topic_id`, `title`, `status`, etc.), V2 adds:

- **authority_sentence**: The one-sentence justification (IS-19).
- **forced_capex**: Data points regarding committed capital.
- **bottleneck**: Description of the structural bottleneck identified.
- **proof_packs**: A list of `ProofPack` objects, mapped to the `tickers` list.

## 3. ProofPack Object
```json
{
  "ticker": "ASML",
  "company_name": "ASML Holding N.V.",
  "bottleneck_role": "High-NA EUV Monopoly Provider",
  "why_irreplaceable_now": "Sole supplier of equipment required for <2nm process nodes.",
  "hard_facts": [
    {
      "fact_type": "CONTRACT",
      "fact_claim": "Signed delivery agreement with Intel for Twinscan EXE:5200.",
      "source_kind": "OFFICIAL_PRESS",
      "source_ref": "data/ops/evidence/asml_intel_2nm.json",
      "source_date": "2026-01-15",
      "independence_key": "press_release_20260115_asml"
    },
    {
      "fact_type": "CAPEX",
      "fact_claim": "Intel 2026 Capex guidance includes $2B for next-gen lithography.",
      "source_kind": "EARNINGS_CALL",
      "source_ref": "data/snapshots/memory/2026-01-20.json",
      "source_date": "2026-01-20",
      "independence_key": "intel_q4_earnings_call"
    }
  ],
  "proof_status": "PROOF_OK"
}
```

## 4. Backward Compatibility
Systems reading V1 cards will find all original fields in their expected locations. V2 fields are new top-level keys or nested objects that V1 readers can safely ignore.
