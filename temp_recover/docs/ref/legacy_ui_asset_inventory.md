# Legacy UI Asset Inventory

This document tracks UI assets and their migration status to the `ui_contracts` layer.

## Assets in `data/ui/`

| Asset | Origin (src/ui/...) | Migration Status | Replacement/Contract |
| :--- | :--- | :--- | :--- |
| `operator_main_card.json` | `natural_language_summary.py` | **MIGRATED** | `ui_contracts/operator_main_card` |
| `operator_narrative_order.json` | `operator_narrative_order_builder.py` | **MIGRATED** | `ui_contracts/operator_narrative_order` |
| `hero_summary.json` | `natural_language_summary.py` | DEPRECATED | - |
| `narrative_entry_hook.json` | `narrative_entry_hook_generator.py` | **MIGRATED** | `ui_contracts/narrative_entry_hook` |
| `upcoming_risk_topN.json` | `schedule_risk_calendar.py` | ACTIVE | `ui_contracts/risk_calendar` |
| `capital_perspective.json` | `capital_perspective_narrator.py` | ACTIVE | `ui_contracts/capital_eye` |
| `daily_content_package.json` | `multi_topic_selector.py` | ACTIVE | `ui_contracts/content_package` |
| `policy_capital_transmission.json`| `policy_capital_transmission.py` | ACTIVE | - |
| `relationship_stress_card.json`| `relationship_stress_generator.py`| ACTIVE | - |
| `valuation_reset_card.json` | `valuation_reset_detector.py` | ACTIVE | - |
| `sector_rotation_acceleration.json`| `sector_rotation_exporter.py` | ACTIVE | - |
| `time_to_money.json` | `time_to_money_resolver.py` | ACTIVE | - |
| `expectation_gap_card.json` | `expectation_gap_exporter.py` | ACTIVE | - |
| `risk_timeline_narrative.json` | `risk_timeline_narrator.py` | ACTIVE | - |
| `daily_narrative_fusion.json` | `narrative_fusion_engine.py` | ACTIVE | - |
| `manifest.json` | `manifest_builder.py` | **MIGRATED** | `ui_contracts/manifest_builder_v2` |

## Key Decisions
- All `src/ui/*.py` scripts are considered **LEGACY**.
- New features must implement builders within `src/ui_contracts/`.
- `manifest_builder_v2` will prune assets not defined in the central registry.
