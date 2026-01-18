# Run Log

- started_utc: 2026-01-18T05:14:53Z
- finished_utc: 2026-01-18T05:15:06Z
- status: SUCCESS

## details

```
engine: start
collect: ok
normalize: ok
anomaly: ok
topic: ok
report: ok | data/reports/2026/01/18/daily_brief.md
checks:
[SKIP] outputs(derived_corr_btc_spx_30d) missing
[SKIP] outputs(derived_corr_usdkrw_us10y_30d) missing
schema_checks:
[OK] schema(crypto_btc_usd_spot_coingecko): timeseries_v1
[OK] schema(fx_usdkrw_spot_open_er_api): timeseries_v1
[OK] schema(metal_gold_xauusd_spot_gold_api): timeseries_v1
[OK] schema(metal_silver_xagusd_spot_gold_api): timeseries_v1
[OK] schema(rates_us10y_yield_ustreasury): timeseries_v1
[OK] schema(risk_vix_index_stooq): timeseries_v1
[OK] schema(index_spx_sp500_stooq): timeseries_v1
[OK] schema(index_kospi_stooq): timeseries_v1
[SKIP] schema(derived_corr_btc_spx_30d): missing curated file (soft_fail)
[SKIP] schema(derived_corr_usdkrw_us10y_30d): missing curated file (soft_fail)
[OK] schema(index_nasdaq_ndx_stooq): timeseries_v1
[OK] schema(fx_dxy_index_stooq): timeseries_v1
[OK] schema(rates_us02y_yield_ustreasury): timeseries_v1
[OK] schema(comm_wti_crude_oil_stooq): timeseries_v1
[OK] schema(metal_platinum_xptusd_stooq): timeseries_v1
[OK] schema(crypto_eth_usd_spot_coingecko): timeseries_v1
engine: done
health: data/reports/2026/01/18/health.json
```
