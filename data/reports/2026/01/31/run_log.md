# Run Log

- started_utc: 2026-01-31T22:57:52+09:00
- finished_utc: 2026-01-31T22:58:25+09:00
- status: SUCCESS

## details

```
engine: start
collect: ok
normalize: ok
derived: ok
anomaly: ok
fact_harvester: ok
fact_first_ingress: ok
topic: ok
pre_structural_layer: ok
anchor_engine: ok
snapshot: ok (data/reports/2026/01/31/data_snapshot.md)
pick_correlator: ok
topic_gate: ok
topic_view: ok
human_pref_overlay: ok
calibration_report: ok
topic_quality_review: ok
speakability_gate: ok
speak_bundle: ok
script_skeletons: ok
topic_console: ok
structural_seeder: ok
issuesignal_builder: ok
video_selector: ok
top1_compressor: ok
whynow_trigger: ok
whynow_escalation: ok
topic_lock: ok (lock=False)
economic_hunter_narrator: ok (Standard)
topic_exporter: ok
operational_dashboard: ok | data/reports/2026/01/31/operational_dashboard.md
decision_dashboard: ok | data/reports/2026/01/31/decision_dashboard.md
decision: ok
judgment_ledger: ok | None
judgment_comparison: ok | None
narrative_preview: ok | NO_TOPIC
report: ok | data/reports/2026/01/31/daily_brief.md
checks:
[SKIP] outputs(metal_platinum_xptusd_stooq) missing
schema_checks:
[OK] schema(index_nasdaq_fred): timeseries_v1
[OK] schema(rates_us02y_fred): timeseries_v1
[OK] schema(comm_wti_fred): timeseries_v1
[OK] schema(metal_platinum_xptusd_stooq): timeseries_v1
[OK] schema(metal_gold_paxg_coingecko): timeseries_v1
[OK] schema(metal_silver_kag_coingecko): timeseries_v1
[OK] schema(metal_silver_kag_coingecko): timeseries_v1
[OK] schema(rates_kor_base_rate_ecos): timeseries_v1
[OK] schema(rates_fed_funds_fred): timeseries_v1
[OK] schema(derived_yield_curve_10y_2y): timeseries_v1
[OK] schema(derived_gold_silver_ratio): timeseries_v1
engine: done
health: data/reports/2026/01/31/health.json
dashboard_projection: skipped (no snapshot)
```
