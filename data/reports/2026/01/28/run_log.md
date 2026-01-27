# Run Log

- started_utc: 2026-01-27T15:27:38Z
- finished_utc: 2026-01-27T15:28:12Z
- status: SUCCESS

## details

```
engine: start
collect: ok
normalize: ok
derived: ok
anomaly: ok
fact_harvester: ok
topic: ok
pre_structural_layer: ok
anchor_engine: ok
snapshot: ok (data/reports/2026/01/28/data_snapshot.md)
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
decision: ok
report: ok | data/reports/2026/01/28/daily_brief.md
checks:
[SKIP] outputs(fx_dxy_index_stooq) missing
[SKIP] outputs(metal_platinum_xptusd_stooq) missing
[SKIP] outputs(crypto_eth_usd_spot_coingecko) missing
[SKIP] outputs(struct_krx_foreigner_flow) missing
[SKIP] outputs(real_estate_price_index) missing
[SKIP] outputs(real_estate_volume) missing
[SKIP] outputs(real_estate_unsold) missing
schema_checks:
[OK] schema(crypto_btc_usd_spot_coingecko): timeseries_v1
[OK] schema(rates_us10y_fred): timeseries_v1
[OK] schema(risk_vix_fred): timeseries_v1
[OK] schema(index_spx_fred): timeseries_v1
[OK] schema(index_kospi_stooq): timeseries_v1
[OK] schema(index_nasdaq_fred): timeseries_v1
[OK] schema(fx_dxy_index_stooq): timeseries_v1
[OK] schema(rates_us02y_fred): timeseries_v1
[OK] schema(comm_wti_fred): timeseries_v1
[OK] schema(metal_platinum_xptusd_stooq): timeseries_v1
[OK] schema(metal_gold_paxg_coingecko): timeseries_v1
[OK] schema(metal_silver_kag_coingecko): timeseries_v1
[OK] schema(metal_silver_kag_coingecko): timeseries_v1
[OK] schema(crypto_eth_usd_spot_coingecko): timeseries_v1
[OK] schema(rates_kor_base_rate_ecos): timeseries_v1
[OK] schema(inflation_kor_cpi_ecos): timeseries_v1
[OK] schema(fx_usdkrw_ecos): timeseries_v1
[OK] schema(rates_fed_funds_fred): timeseries_v1
[OK] schema(inflation_cpi_fred): timeseries_v1
[OK] schema(inflation_pce_fred): timeseries_v1
[OK] schema(liquidity_m2_fred): timeseries_v1
[OK] schema(employment_unrate_fred): timeseries_v1
[OK] schema(credit_hy_spread_fred): timeseries_v1
[OK] schema(risk_financial_stress_fred): timeseries_v1
[OK] schema(derived_yield_curve_10y_2y): timeseries_v1
[OK] schema(derived_gold_silver_ratio): timeseries_v1
[OK] schema(struct_dart_cb_bw): timeseries_v1
[OK] schema(struct_dart_disposal): timeseries_v1
[SKIP] schema(struct_krx_foreigner_flow): missing curated file (soft_fail)
[OK] schema(real_estate_price_index): timeseries_v1
[OK] schema(real_estate_volume): timeseries_v1
[OK] schema(real_estate_unsold): timeseries_v1
engine: done
health: data/reports/2026/01/28/health.json
dashboard_projection: skipped (no snapshot)
```
