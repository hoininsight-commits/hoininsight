# Data Snapshot

<<<<<<< Updated upstream
- ts_utc: `2026-01-24T04:52:23Z`
=======
- ts_utc: `2026-01-24T05:00:41Z`
>>>>>>> Stashed changes
- ymd_utc: `2026/01/24`
- enabled_datasets: `32`

## Per-dataset Status (Today)

| report_key | dataset_id | status_today | rows | first_ts_utc | last_ts_utc | last_7d_rows | last_30d_rows | ok_7d | skipped_7d | fail_7d | curated_path | chart_png |
|---|---|---:|---:|---|---|---:|---:|---:|---:|---:|---|---|
<<<<<<< Updated upstream
| BLOCK_DEAL_PROXY | struct_krx_foreigner_flow | UNKNOWN | 0 | - | - | 0 | 0 | 0 | 2 | 0 | data/curated/structural/foreigner_flow.csv | - |
| BTCUSD | crypto_btc_usd_spot_coingecko | UNKNOWN | 181 | 2026-01-15T07:32:29Z | 2026-01-24T04:51:33Z | 133 | 181 | 6 | 0 | 0 | data/curated/crypto/btc_usd.csv | [png](data/reports/2026/01/24/charts/crypto_btc_usd_spot_coingecko.png) |
| CPI_USA | inflation_cpi_fred | UNKNOWN | 947 | 1947-01-01T00:00:00Z | 2025-12-01T00:00:00Z | 0 | 0 | 6 | 0 | 0 | data/curated/inflation/cpi_usa.csv | [png](data/reports/2026/01/24/charts/inflation_cpi_fred.png) |
| DXY | fx_dxy_index_stooq | UNKNOWN | 4 | 2026-01-15T00:00:00Z | 2026-01-18T00:00:00Z | 1 | 4 | 1 | 5 | 0 | data/curated/fx/dxy.csv | [png](data/reports/2026/01/24/charts/fx_dxy_index_stooq.png) |
| ETHUSD | crypto_eth_usd_spot_coingecko | UNKNOWN | 11 | 2026-01-15T00:00:00Z | 2026-01-24T00:00:00Z | 8 | 11 | 1 | 5 | 0 | data/curated/crypto/eth_usd.csv | [png](data/reports/2026/01/24/charts/crypto_eth_usd_spot_coingecko.png) |
| FED_FUNDS | rates_fed_funds_fred | UNKNOWN | 858 | 1954-07-01T00:00:00Z | 2025-12-01T00:00:00Z | 0 | 0 | 6 | 0 | 0 | data/curated/rates/fed_funds.csv | [png](data/reports/2026/01/24/charts/rates_fed_funds_fred.png) |
| FIN_STRESS | risk_financial_stress_fred | UNKNOWN | 1463 | 1993-12-31T00:00:00Z | 2022-01-07T00:00:00Z | 0 | 0 | 6 | 0 | 0 | data/curated/risk/financial_stress_usa.csv | [png](data/reports/2026/01/24/charts/risk_financial_stress_fred.png) |
| GOLD | metal_gold_paxg_coingecko | UNKNOWN | 82 | 2026-01-15T08:10:58Z | 2026-01-24T00:00:00Z | 36 | 82 | 6 | 0 | 0 | data/curated/metals/gold_usd.csv | [png](data/reports/2026/01/24/charts/metal_gold_paxg_coingecko.png) |
| GS_RATIO | derived_gold_silver_ratio | UNKNOWN | 72 | 2026-01-15T08:10:58Z | 2026-01-24T00:00:00Z | 32 | 72 | 6 | 0 | 0 | data/curated/derived/metals/gold_silver_ratio.csv | [png](data/reports/2026/01/24/charts/derived_gold_silver_ratio.png) |
| HY_SPREAD | credit_hy_spread_fred | UNKNOWN | 7587 | 1996-12-31T00:00:00Z | 2026-01-22T00:00:00Z | 4 | 19 | 6 | 0 | 0 | data/curated/credit/hy_spread_usa.csv | [png](data/reports/2026/01/24/charts/credit_hy_spread_fred.png) |
| KOR_CPI | inflation_kor_cpi_ecos | UNKNOWN | 61 | 2021-01-01T00:00:00Z | 2025-12-01T00:00:00Z | 0 | 0 | 6 | 0 | 0 | data/curated/ecos/inflation/korea_cpi.csv | [png](data/reports/2026/01/24/charts/inflation_kor_cpi_ecos.png) |
| KOR_RATE | rates_kor_base_rate_ecos | UNKNOWN | 61 | 2021-01-01T00:00:00Z | 2025-12-01T00:00:00Z | 0 | 0 | 6 | 0 | 0 | data/curated/ecos/rates/korea_base_rate.csv | [png](data/reports/2026/01/24/charts/rates_kor_base_rate_ecos.png) |
| KOSPI | index_kospi_stooq | UNKNOWN | 180 | 2026-01-15T07:32:40Z | 2026-01-24T04:51:36Z | 132 | 180 | 6 | 0 | 0 | data/curated/indices/kospi.csv | [png](data/reports/2026/01/24/charts/index_kospi_stooq.png) |
| M2_USA | liquidity_m2_fred | UNKNOWN | 803 | 1959-01-01T00:00:00Z | 2025-11-01T00:00:00Z | 0 | 0 | 6 | 0 | 0 | data/curated/liquidity/m2_usa.csv | [png](data/reports/2026/01/24/charts/liquidity_m2_fred.png) |
| M_AND_A_CB | struct_dart_cb_bw | UNKNOWN | 1 | 2026-01-22T18:00:00Z | 2026-01-22T18:00:00Z | 1 | 1 | 2 | 0 | 0 | data/curated/structural/cb_bw.csv | [png](data/reports/2026/01/24/charts/struct_dart_cb_bw.png) |
| M_AND_A_DISP | struct_dart_disposal | UNKNOWN | 2 | 2026-01-22T18:00:00Z | 2026-01-24T18:00:00Z | 2 | 2 | 2 | 0 | 0 | data/curated/structural/disposal.csv | [png](data/reports/2026/01/24/charts/struct_dart_disposal.png) |
| NASDAQ | index_nasdaq_fred | UNKNOWN | 10099 | 1986-01-02T00:00:00Z | 2026-01-23T00:00:00Z | 5 | 23 | 6 | 0 | 0 | data/curated/indices/nasdaq.csv | [png](data/reports/2026/01/24/charts/index_nasdaq_fred.png) |
| PCE_USA | inflation_pce_fred | UNKNOWN | 803 | 1959-01-01T00:00:00Z | 2025-11-01T00:00:00Z | 0 | 0 | 6 | 0 | 0 | data/curated/inflation/pce_usa.csv | [png](data/reports/2026/01/24/charts/inflation_pce_fred.png) |
| PLATINUM | metal_platinum_xptusd_stooq | UNKNOWN | 4 | 2026-01-15T00:00:00Z | 2026-01-18T00:00:00Z | 1 | 4 | 1 | 5 | 0 | data/curated/metals/platinum.csv | [png](data/reports/2026/01/24/charts/metal_platinum_xptusd_stooq.png) |
| RE_PRICE | real_estate_price_index | UNKNOWN | 2 | 2026-01-22T00:00:00Z | 2026-01-24T00:00:00Z | 2 | 2 | 0 | 2 | 0 | data/curated/real_estate/price_index.csv | [png](data/reports/2026/01/24/charts/real_estate_price_index.png) |
| RE_UNSOLD | real_estate_unsold | UNKNOWN | 2 | 2026-01-22T00:00:00Z | 2026-01-24T00:00:00Z | 2 | 2 | 0 | 2 | 0 | data/curated/real_estate/unsold.csv | [png](data/reports/2026/01/24/charts/real_estate_unsold.png) |
| RE_VOL | real_estate_volume | UNKNOWN | 2 | 2026-01-22T00:00:00Z | 2026-01-24T00:00:00Z | 2 | 2 | 0 | 2 | 0 | data/curated/real_estate/volume.csv | [png](data/reports/2026/01/24/charts/real_estate_volume.png) |
| SILVER | metal_silver_kag_coingecko | UNKNOWN | 82 | 2026-01-15T08:10:58Z | 2026-01-24T00:00:00Z | 36 | 82 | 6 | 0 | 0 | data/curated/metals/silver_usd.csv | [png](data/reports/2026/01/24/charts/metal_silver_kag_coingecko.png) |
| SILVER | metal_silver_kag_coingecko | UNKNOWN | 82 | 2026-01-15T08:10:58Z | 2026-01-24T00:00:00Z | 36 | 82 | 6 | 0 | 0 | data/curated/metals/silver_usd.csv | [png](data/reports/2026/01/24/charts/metal_silver_kag_coingecko.png) |
| SPX | index_spx_fred | UNKNOWN | 2596 | 2016-01-19T00:00:00Z | 2026-01-23T00:00:00Z | 33 | 96 | 6 | 0 | 0 | data/curated/indices/spx.csv | [png](data/reports/2026/01/24/charts/index_spx_fred.png) |
| UNRATE | employment_unrate_fred | UNKNOWN | 935 | 1948-01-01T00:00:00Z | 2025-12-01T00:00:00Z | 0 | 0 | 6 | 0 | 0 | data/curated/employment/unrate_usa.csv | [png](data/reports/2026/01/24/charts/employment_unrate_fred.png) |
| US02Y | rates_us02y_fred | UNKNOWN | 12410 | 1976-06-01T00:00:00Z | 2026-01-22T00:00:00Z | 4 | 22 | 6 | 0 | 0 | data/curated/rates/us02y.csv | [png](data/reports/2026/01/24/charts/rates_us02y_fred.png) |
| US10Y | rates_us10y_fred | UNKNOWN | 16075 | 1962-01-02T00:00:00Z | 2026-01-22T00:00:00Z | 32 | 95 | 6 | 0 | 0 | data/curated/rates/us10y.csv | [png](data/reports/2026/01/24/charts/rates_us10y_fred.png) |
| USDKRW_ECOS | fx_usdkrw_ecos | UNKNOWN | 1236 | 2021-01-18T00:00:00Z | 2026-01-23T00:00:00Z | 5 | 20 | 6 | 0 | 0 | data/curated/ecos/fx/usdkrw.csv | [png](data/reports/2026/01/24/charts/fx_usdkrw_ecos.png) |
| VIX | risk_vix_fred | UNKNOWN | 9184 | 1990-01-02T00:00:00Z | 2026-01-22T00:00:00Z | 33 | 96 | 6 | 0 | 0 | data/curated/risk/vix.csv | [png](data/reports/2026/01/24/charts/risk_vix_fred.png) |
| WTI | comm_wti_fred | UNKNOWN | 10085 | 1986-01-02T00:00:00Z | 2026-01-20T00:00:00Z | 2 | 20 | 6 | 0 | 0 | data/curated/commodities/wti.csv | [png](data/reports/2026/01/24/charts/comm_wti_fred.png) |
| YIELD_CURVE | derived_yield_curve_10y_2y | UNKNOWN | 12406 | 1976-06-01T00:00:00Z | 2026-01-22T00:00:00Z | 3 | 18 | 6 | 0 | 0 | data/curated/derived/rates/yield_curve_10y_2y.csv | [png](data/reports/2026/01/24/charts/derived_yield_curve_10y_2y.png) |
=======
| BTCUSD | crypto_btc_usd_spot_coingecko | OK | 181 | 2026-01-15T07:32:29Z | 2026-01-24T04:49:09Z | 133 | 181 | 7 | 0 | 0 | data/curated/crypto/btc_usd.csv | - |
| CPI_USA | inflation_cpi_fred | OK | 947 | 1947-01-01T00:00:00Z | 2025-12-01T00:00:00Z | 0 | 0 | 7 | 0 | 0 | data/curated/inflation/cpi_usa.csv | - |
| FED_FUNDS | rates_fed_funds_fred | OK | 858 | 1954-07-01T00:00:00Z | 2025-12-01T00:00:00Z | 0 | 0 | 7 | 0 | 0 | data/curated/rates/fed_funds.csv | - |
| FIN_STRESS | risk_financial_stress_fred | OK | 1463 | 1993-12-31T00:00:00Z | 2022-01-07T00:00:00Z | 0 | 0 | 7 | 0 | 0 | data/curated/risk/financial_stress_usa.csv | - |
| GOLD | metal_gold_paxg_coingecko | OK | 82 | 2026-01-15T08:10:58Z | 2026-01-24T00:00:00Z | 36 | 82 | 7 | 0 | 0 | data/curated/metals/gold_usd.csv | - |
| GS_RATIO | derived_gold_silver_ratio | OK | 72 | 2026-01-15T08:10:58Z | 2026-01-24T00:00:00Z | 32 | 72 | 7 | 0 | 0 | data/curated/derived/metals/gold_silver_ratio.csv | - |
| HY_SPREAD | credit_hy_spread_fred | OK | 7587 | 1996-12-31T00:00:00Z | 2026-01-22T00:00:00Z | 4 | 19 | 7 | 0 | 0 | data/curated/credit/hy_spread_usa.csv | - |
| KOR_CPI | inflation_kor_cpi_ecos | OK | 61 | 2021-01-01T00:00:00Z | 2025-12-01T00:00:00Z | 0 | 0 | 7 | 0 | 0 | data/curated/ecos/inflation/korea_cpi.csv | - |
| KOR_RATE | rates_kor_base_rate_ecos | OK | 61 | 2021-01-01T00:00:00Z | 2025-12-01T00:00:00Z | 0 | 0 | 7 | 0 | 0 | data/curated/ecos/rates/korea_base_rate.csv | - |
| KOSPI | index_kospi_stooq | OK | 180 | 2026-01-15T07:32:40Z | 2026-01-24T04:49:16Z | 132 | 180 | 7 | 0 | 0 | data/curated/indices/kospi.csv | - |
| M2_USA | liquidity_m2_fred | OK | 803 | 1959-01-01T00:00:00Z | 2025-11-01T00:00:00Z | 0 | 0 | 7 | 0 | 0 | data/curated/liquidity/m2_usa.csv | - |
| M_AND_A_CB | struct_dart_cb_bw | OK | 1 | 2026-01-22T18:00:00Z | 2026-01-22T18:00:00Z | 1 | 1 | 3 | 0 | 0 | data/curated/structural/cb_bw.csv | - |
| M_AND_A_DISP | struct_dart_disposal | OK | 2 | 2026-01-22T18:00:00Z | 2026-01-24T18:00:00Z | 2 | 2 | 3 | 0 | 0 | data/curated/structural/disposal.csv | - |
| NASDAQ | index_nasdaq_fred | OK | 10099 | 1986-01-02T00:00:00Z | 2026-01-23T00:00:00Z | 5 | 23 | 7 | 0 | 0 | data/curated/indices/nasdaq.csv | - |
| PCE_USA | inflation_pce_fred | OK | 803 | 1959-01-01T00:00:00Z | 2025-11-01T00:00:00Z | 0 | 0 | 7 | 0 | 0 | data/curated/inflation/pce_usa.csv | - |
| SILVER | metal_silver_kag_coingecko | OK | 82 | 2026-01-15T08:10:58Z | 2026-01-24T00:00:00Z | 36 | 82 | 7 | 0 | 0 | data/curated/metals/silver_usd.csv | - |
| SILVER | metal_silver_kag_coingecko | OK | 82 | 2026-01-15T08:10:58Z | 2026-01-24T00:00:00Z | 36 | 82 | 7 | 0 | 0 | data/curated/metals/silver_usd.csv | - |
| SPX | index_spx_fred | OK | 2596 | 2016-01-19T00:00:00Z | 2026-01-23T00:00:00Z | 33 | 96 | 7 | 0 | 0 | data/curated/indices/spx.csv | - |
| UNRATE | employment_unrate_fred | OK | 935 | 1948-01-01T00:00:00Z | 2025-12-01T00:00:00Z | 0 | 0 | 7 | 0 | 0 | data/curated/employment/unrate_usa.csv | - |
| US02Y | rates_us02y_fred | OK | 12410 | 1976-06-01T00:00:00Z | 2026-01-22T00:00:00Z | 4 | 22 | 7 | 0 | 0 | data/curated/rates/us02y.csv | - |
| US10Y | rates_us10y_fred | OK | 16075 | 1962-01-02T00:00:00Z | 2026-01-22T00:00:00Z | 32 | 95 | 7 | 0 | 0 | data/curated/rates/us10y.csv | - |
| USDKRW_ECOS | fx_usdkrw_ecos | OK | 1236 | 2021-01-18T00:00:00Z | 2026-01-23T00:00:00Z | 5 | 20 | 7 | 0 | 0 | data/curated/ecos/fx/usdkrw.csv | - |
| VIX | risk_vix_fred | OK | 9184 | 1990-01-02T00:00:00Z | 2026-01-22T00:00:00Z | 33 | 96 | 7 | 0 | 0 | data/curated/risk/vix.csv | - |
| WTI | comm_wti_fred | OK | 10085 | 1986-01-02T00:00:00Z | 2026-01-20T00:00:00Z | 2 | 20 | 7 | 0 | 0 | data/curated/commodities/wti.csv | - |
| YIELD_CURVE | derived_yield_curve_10y_2y | OK | 12406 | 1976-06-01T00:00:00Z | 2026-01-22T00:00:00Z | 3 | 18 | 7 | 0 | 0 | data/curated/derived/rates/yield_curve_10y_2y.csv | - |
| BLOCK_DEAL_PROXY | struct_krx_foreigner_flow | SKIPPED | 0 | - | - | 0 | 0 | 0 | 3 | 0 | data/curated/structural/foreigner_flow.csv | - |
| DXY | fx_dxy_index_stooq | SKIPPED | 4 | 2026-01-15T00:00:00Z | 2026-01-18T00:00:00Z | 1 | 4 | 1 | 6 | 0 | data/curated/fx/dxy.csv | - |
| ETHUSD | crypto_eth_usd_spot_coingecko | SKIPPED | 11 | 2026-01-15T00:00:00Z | 2026-01-24T00:00:00Z | 8 | 11 | 1 | 6 | 0 | data/curated/crypto/eth_usd.csv | - |
| PLATINUM | metal_platinum_xptusd_stooq | SKIPPED | 4 | 2026-01-15T00:00:00Z | 2026-01-18T00:00:00Z | 1 | 4 | 1 | 6 | 0 | data/curated/metals/platinum.csv | - |
| RE_PRICE | real_estate_price_index | SKIPPED | 2 | 2026-01-22T00:00:00Z | 2026-01-24T00:00:00Z | 2 | 2 | 0 | 3 | 0 | data/curated/real_estate/price_index.csv | - |
| RE_UNSOLD | real_estate_unsold | SKIPPED | 2 | 2026-01-22T00:00:00Z | 2026-01-24T00:00:00Z | 2 | 2 | 0 | 3 | 0 | data/curated/real_estate/unsold.csv | - |
| RE_VOL | real_estate_volume | SKIPPED | 2 | 2026-01-22T00:00:00Z | 2026-01-24T00:00:00Z | 2 | 2 | 0 | 3 | 0 | data/curated/real_estate/volume.csv | - |
>>>>>>> Stashed changes

## Charts
- Directory: `data/reports/2026/01/24/charts/`

## Notes
- rows/ts는 curated CSV 기준입니다.
- ok_7d/skipped_7d/fail_7d는 최근 7일 health.json(per_dataset) 기록을 집계합니다.
- 파생지표는 데이터 누적 전까지 SKIPPED가 정상일 수 있습니다(soft_fail).
