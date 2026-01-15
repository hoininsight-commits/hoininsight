# Core Dataset Policy

## Policy Versions
- **Core v1**: SPX, US10Y, BTC (Legacy)
- **Core v2**: SPX, US10Y, BTC, USDKRW, GOLD (Current, Ops v1.6)

## Status Determination Rule
- **SUCCESS**: All Core v2 datasets are `OK`.
- **PARTIAL**: All Core v2 are `OK`, but Derived datasets have failures.
- **FAIL**: Any Core v2 dataset is `FAIL`.

## Reference
Defined in `src/ops/core_dataset.py`.
