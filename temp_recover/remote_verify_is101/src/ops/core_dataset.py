from typing import List

# Core Dataset Policy Definition
# v1: SPX, US10Y, BTC (Legacy)
# v2: SPX, US10Y, BTC, USDKRW, GOLD (Standardized in Ops v1.6)

CORE_DATASETS_V2: List[str] = [
    "index_spx_sp500_stooq",           # S&P 500
    "rates_us10y_yield_ustreasury",    # US 10Y Yield
    "crypto_btc_usd_spot_coingecko",   # Bitcoin
    "fx_usdkrw_spot_open_yfinance",    # USD/KRW (Appended)
    "metal_gold_xauusd_spot_yfinance"  # Gold (Appended)
]

def is_core_dataset(dataset_id: str) -> bool:
    """Check if a dataset_id is part of the V2 Core definition."""
    return dataset_id in CORE_DATASETS_V2
