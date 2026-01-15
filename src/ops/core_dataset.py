from pathlib import Path
from typing import Dict

def get_core_datasets() -> Dict[str, str]:
    """
    Returns the mapped dataset_ids for the fixed Core Datasets (Ops Upgrade v1).
    Rules:
      - RATES_YIELD: US10Y
      - GLOBAL_INDEX: SPX
      - CRYPTO: BTC
    """
    # Explicit mapping as per Ops Upgrade v1 requirements
    # These IDs must exist in registry/datasets.yml
    return {
        "US10Y": "rates_us10y_yield_ustreasury",
        "SPX": "index_spx_sp500_stooq",
        "BTC": "crypto_btc_usd_spot_coingecko"
    }
