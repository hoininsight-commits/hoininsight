# REF-009 Legacy Freeze Report

**Status**: ✅ SUCCESS (FREEZE ACTIVE)
**Date**: 2026-02-06
**Baseline Commit**: `37c2f68db`

## 1. Goal: Stopping technical debt expansion
REF-009 establishes a strict boundary between existing legacy area and new development areas. 
The expansion of legacy patterns (`src.ui` imports or `hit_legacy` calls) is now blocked at the CI/Test level.

## 2. Policy Enforced
| Context | Pattern | Rule |
| :--- | :--- | :--- |
| **Legacy Root** (`src/ui/`, `src/collectors/`, etc.) | Legacy usage | ✅ ALLOWED (Maintenance) |
| **New Context** (`src/ui_logic/`, `src/topics/`, etc.) | Legacy usage | ❌ BLOCKED (Freeze violation) |
| **Any Context** | Non-allowlisted legacy | ❌ BLOCKED (Hard Gate rule) |

## 3. Implementation Details
- **`src/legacy_guard/boundary.py`**: The source of truth for "Legacy Context" definitions.
- **`tests/verify_ref009_no_new_legacy.py`**: A static analyzer that ensures no new files adopt legacy patterns.
- **Enforcement**: The `Legacy Hard Gate` now cross-checks the caller's file path against the legacy boundary.

## 4. Example Violation Log
```text
[REF-009][BLOCK] New legacy usage detected:
- file: src/ui_logic/reporting/new_generator.py
- reason: Pattern from src\.ui\. found in NEW context
```

## 5. Next Steps
- **REF-010**: Automated "Legacy Sanitizer" to suggest replacements for detected violations in new contexts.
- CI integration of `scripts/precommit_check_ref009.py`.
