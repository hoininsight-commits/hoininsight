# UI Contract Authority Declaration

**Effective Date**: 2026-02-06
**Scope**: All UI Assets and Data Contracts for HoinInsight

## 1. The Single Source of Truth
Implicit and fragmented UI data generation is now deprecated. The **Official UI Contract Layer** (`src/ui_contracts/`) is the sole authority for:
1. JSON Schema definition for UI cards.
2. Data validation (types, required fields, and citations).
3. Manifest generation (order and staging).

## 2. Prohibited Actions
- **Direct Manifest Editing**: No script outside of `ui_contracts` should modify `data/ui/manifest.json`.
- **Legacy Path Extension**: New UI features must NOT be added to `src/ui/`.
- **Out-of-Contract Assets**: Rendering assets not registered in `registry/ui_cards/ui_card_registry_v1.yml` is prohibited.

## 3. Maintenance Policy
- `src/ui/` is preserved for historical reference (ADD-ONLY constraint).
- All new development must follow the "Registry -> Contract -> Publish" flow.
