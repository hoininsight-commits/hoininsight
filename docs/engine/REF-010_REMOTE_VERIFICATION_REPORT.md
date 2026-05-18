# REF-010 Remote Verification Report

**Status**: ✅ SUCCESS (Guidance Active)
**Date**: 2026-02-06
**Baseline Commit**: `52c325a70`

## 1. Goal: Legacy Deprecation & Guidance
REF-010 establishes a system to detect legacy patterns, issue deprecation warnings with sunset dates, and provide clear migration instructions to the operator.

## 2. Verification Summary
- **Registry**: `registry/refactor/legacy_map_v1.yml` successfully defines detection rules.
- **Scanner**: `src/refactor/legacy_deprecation_scanner.py` correctly identifies legacy patterns in `index.html` and `engine/__init__.py`.
- **Enforcement**: Verified that `HOIN_LEGACY_ENFORCE=1` correctly fails the pipeline if `HIGH` severity hits are detected.
- **Guidance UI**: `docs/ui/cards/deprecation_notice_card.js` renders a warning panel on the dashboard when the ledger contains warnings.

## 3. Execution Logs
```bash
=== VERIFYING REF-010: Deprecation Ledger ===
[Canonical Publish] Starting...
...
=== REF-010 Legacy Deprecation Scanner ===
[Scanner] Created ledger with 1 hits at data_outputs/ops/deprecation_ledger.json
[Publisher] Published ledger to docs/data/ops/deprecation_ledger.json

[Canonical Publish] Complete. SSOT: data_outputs/ops/
=== VERIFYING REF-010: Deprecation Ledger ===

[Case 2] Testing HOIN_LEGACY_ENFORCE=1...
✅ Correctly failed in enforce mode: RuntimeError: [REF-010][BLOCK] critical legacy hits found: 1

=== REF-010 VERIFICATION SUCCESS ===
```

## 4. Final Recommendation
- Review `data_outputs/ops/deprecation_ledger.json` daily to identify top migration priorities.
- Encourage developers to check `replacement` fields for standardized new paths.
