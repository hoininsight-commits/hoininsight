# REF-008 Remote Verification Report

**Status**: ✅ SUCCESS
**Date**: 2026-02-06
**Baseline Commit**: `379f08f55` (REF-006 baseline)

## 1. Summary of Changes
- **Allowlist Registry**: Created `registry/ops/legacy_allowlist_v1.yml` to define exceptions for legacy code execution.
- **Hard Gate Enforcement**: Implemented `legacy_hard_gate.py` to block unauthorized legacy calls when `HOIN_LEGACY_HARD=1`.
- **Decision Ledger**: Implemented `legacy_block_ledger.py` to record both blocked and allowed legacy access attempts.
- **Readiness Reporting**: Added `legacy_hard_report.py` to generate `docs/ops/LEGACY_HARD_READINESS.md`, providing visibility into the "Legacy-Free" transition progress.

## 2. Allowlist Status
- **Total Allowed Modules**: 3
- **Example**: `src.ui.operator_main_contract` (Allowed until 2026-02-28 for testing)

## 3. Verification Logs
```bash
=== VERIFYING REF-008: Legacy Hard Gate ===

[Case 1] HARD=1 + Blocked Module...
[⚠️  LEGACY WARNING] Module 'src.ui.ui_decision_contract' is deprecated.
✅ Correctly Blocked: [REF-008][CRITICAL] Legacy access blocked: src.ui.ui_decision_contract (Reason: NOT_IN_ALLOWLIST)

[Case 2] HARD=1 + Allowed Module...
[⚠️  LEGACY WARNING] Module 'src.ui.operator_main_contract' is deprecated.
✅ Correctly Allowed.

[Case 3] Ledger Persistence...
✅ Ledger verified: 1 blocked, 1 allowed.

[Case 4] Readiness Report...
[HardGate] Readiness report generated at docs/ops/LEGACY_HARD_READINESS.md
✅ Readiness report verified.
=== REF-008 VERIFICATION SUCCESS ===
```

## 4. Final Recommendation
- CI builds should now run with `HOIN_LEGACY_HARD=1` to ensure no new legacy dependencies are introduced.
- Focus on decommissioning `src.ui.publish_ui_assets` next as it's the top remaining operational legacy link.
