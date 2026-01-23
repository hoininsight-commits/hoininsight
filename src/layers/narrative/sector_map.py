from typing import Dict, Optional

class SectorMap:
    """
    Maps asset identifiers (tickers, dataset_ids) to broader Sectors and Themes.
    Used by NarrativeEngine to group independent signals into a cohesive story.
    """
    
    # Static mapping for known assets in the Hoin ecosystem
    _ASSET_MAP = {
        # Equities
        "sp500": {"sector": "Equity", "theme": "Broad Market (US)"},
        "nasdaq100": {"sector": "Equity", "theme": "Tech / Growth"},
        "kospi": {"sector": "Equity", "theme": "Emerging Market / Korea"},
        
        # Volatility
        "vix": {"sector": "Volatility", "theme": "Risk Sentiment"},
        
        # Rates
        "us_10y_yield": {"sector": "Rates", "theme": "Long Duration"},
        "us10y": {"sector": "Rates", "theme": "Long Duration"},
        "us_2y_yield": {"sector": "Rates", "theme": "Monetary Policy Proxy"},
        "fedfunds": {"sector": "Rates", "theme": "Central Bank Policy"},
        "fed_funds_rate": {"sector": "Rates", "theme": "Central Bank Policy"},
        
        # Credit
        "hy_spread": {"sector": "Credit", "theme": "Risk Appetite"},
        "financial_stress": {"sector": "Credit", "theme": "Systemic Risk"},
        "dart_cb": {"sector": "Credit", "theme": "Corporate Issuance (Korea)"},
        
        # Commodities
        "gold_usd": {"sector": "Commodity", "theme": "Safe Haven / Inflation Hedge"},
        "xauusd": {"sector": "Commodity", "theme": "Safe Haven / Inflation Hedge"},
        "silver_usd": {"sector": "Commodity", "theme": "Industrial / Precious"},
        "xagusd": {"sector": "Commodity", "theme": "Industrial / Precious"},
        "wti": {"sector": "Commodity", "theme": "Energy"},
        "gold_silver_ratio": {"sector": "Commodity", "theme": "Risk/Inflation Signal"},
        
        # Crypto
        "btc_usd": {"sector": "Crypto", "theme": "Digital Gold / Risk"},
        
        # FX
        "usdkrw": {"sector": "FX", "theme": "Export Competitiveness"},
        "dxy": {"sector": "FX", "theme": "USD Strength"},
        
        # Macro / Inflation
        "cpi": {"sector": "Macro", "theme": "Inflation"},
        "pce": {"sector": "Macro", "theme": "Inflation"},
        "m2": {"sector": "Macro", "theme": "Liquidity"},
        
        # Mock / Future Assets (for testing Narrative Logic)
        "xbi": {"sector": "Equity", "theme": "Biotech"},
        "xlv": {"sector": "Equity", "theme": "Healthcare"},
        "ibb": {"sector": "Equity", "theme": "Biotech"},
    }

    @classmethod
    def get_info(cls, asset_id: str) -> Dict[str, str]:
        """
        Returns a dict with 'sector' and 'theme' for a given asset_id.
        Matches partial keys if exact match not found (e.g. 'fred/market/sp500' matches 'sp500').
        """
        # 1. Exact match
        if asset_id in cls._ASSET_MAP:
            return cls._ASSET_MAP[asset_id]
        
        # 2. Key contained in asset_id (e.g. 'sp500' in 'market_sp500_fred')
        normalized_id = asset_id.lower().replace(".csv", "").replace(".json", "")
        for key, info in cls._ASSET_MAP.items():
            if key in normalized_id:
                return info
                
        # 3. Fallback
        return {"sector": "Unmapped", "theme": "General"}

    @classmethod
    def get_sector(cls, asset_id: str) -> str:
        return cls.get_info(asset_id)["sector"]

    @classmethod
    def get_theme(cls, asset_id: str) -> str:
        return cls.get_info(asset_id)["theme"]
