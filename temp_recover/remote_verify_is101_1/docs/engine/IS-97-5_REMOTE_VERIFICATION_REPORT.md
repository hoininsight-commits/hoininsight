# IS-97-5 WHY-MUST RANKING - REMOTE VERIFICATION REPORT

**Date**: 2026-02-04
**Baseline Hash**: `f0c6635bf259dd16ba2d98218146740669298418`
**Verified Hash**: `d90bcecf4395ed11d599a2f635e17e7031c3b2e4`
**Status**: ✅ PASS

## Verification Scope
- **Logic Layer**: `src/topics/mentionables/why_must_ranking.py`
- **Capability**: Deterministic Ranking by Structural Necessity (Score 0.0-1.0).
- **Compliance**: Add-Only Revisions (No changes to `DATA_COLLECTION_MASTER.md`).

## Test Results
- **Test Script**: `tests/verify_is97_5_why_must_ranking.py`
- **Result**: PASSED in Remote Clean Clone.
- **Validations**:
  1. **Bottleneck Dominance**: `GRID_INFRA` (1.0) correctly outranks `FINANCIAL` (0.4).
  2. **Hypothesis Penalty**: `HOLD` status reduces Timeline score to 0.2.
  3. **Deduplication**: Max 2 entities per role enforced.
  4. **Reliability Filter**: Integrity maintained.

## Final Sign-off
 The "Why-Must Ranking Layer" is active. Mentionables are now prioritized by their contribution to the thematic bottleneck, not by market popularity.
