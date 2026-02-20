from typing import Dict, Optional

class SectorMap:
    """
    Maps asset identifiers (tickers, dataset_ids) to broader Sectors and Themes.
    Used by NarrativeEngine to group independent signals into a cohesive story.
    """
    
    # Static mapping for known assets in the Hoin ecosystem
    _ASSET_MAP = {
        # Equities
        "sp500": {"sector": "주식 (Equity)", "theme": "미국 시장 (Broad Market)"},
        "nasdaq100": {"sector": "주식 (Equity)", "theme": "기술/성장주 (Tech/Growth)"},
        "kospi": {"sector": "주식 (Equity)", "theme": "이머징/한국 (Emerging/Korea)"},
        
        # Volatility
        "vix": {"sector": "변동성 (Volatility)", "theme": "위험 심리 (Risk Sentiment)"},
        
        # Rates
        "us_10y_yield": {"sector": "금리 (Rates)", "theme": "장기 금리 (Long Duration)"},
        "us10y": {"sector": "금리 (Rates)", "theme": "장기 금리 (Long Duration)"},
        "us_2y_yield": {"sector": "금리 (Rates)", "theme": "통화 정책 대리 (Monetary Policy Proxy)"},
        "fedfunds": {"sector": "금리 (Rates)", "theme": "중앙은행 정책 (Central Bank Policy)"},
        "fed_funds_rate": {"sector": "금리 (Rates)", "theme": "중앙은행 정책 (Central Bank Policy)"},
        
        # Credit
        "hy_spread": {"sector": "크레딧 (Credit)", "theme": "위험 선호 (Risk Appetite)"},
        "financial_stress": {"sector": "크레딧 (Credit)", "theme": "시스템 리스크 (Systemic Risk)"},
        "dart_cb": {"sector": "크레딧 (Credit)", "theme": "기업 자금조달 (Korea)"},
        
        # Commodities
        "gold_usd": {"sector": "원자재 (Commodity)", "theme": "안전 자산 / 인플레 헷지"},
        "xauusd": {"sector": "원자재 (Commodity)", "theme": "안전 자산 / 인플레 헷지"},
        "silver_usd": {"sector": "원자재 (Commodity)", "theme": "산업재 / 귀금속"},
        "xagusd": {"sector": "원자재 (Commodity)", "theme": "산업재 / 귀금속"},
        "wti": {"sector": "원자재 (Commodity)", "theme": "에너지 (Energy)"},
        "gold_silver_ratio": {"sector": "원자재 (Commodity)", "theme": "경기/인플레 시그널"},
        
        # Crypto
        "btc_usd": {"sector": "크립토 (Crypto)", "theme": "디지털 골드 / 위험 자산"},
        
        # FX
        "usdkrw": {"sector": "환율 (FX)", "theme": "수출 경쟁력 / 원화 가치"},
        "dxy": {"sector": "환율 (FX)", "theme": "달러 강세 (USD Strength)"},
        
        # Macro / Inflation
        "cpi": {"sector": "매크로 (Macro)", "theme": "인플레이션 (Inflation)"},
        "pce": {"sector": "매크로 (Macro)", "theme": "분기 인플레이션 (PCE)"},
        "m2": {"sector": "매크로 (Macro)", "theme": "유동성 (Liquidity)"},
        
        # Mock / Future Assets (for testing Narrative Logic)
        "xbi": {"sector": "주식 (Equity)", "theme": "바이오 (Biotech)"},
        "xlv": {"sector": "주식 (Equity)", "theme": "헬스케어 (Healthcare)"},
        "ibb": {"sector": "주식 (Equity)", "theme": "바이오 (Biotech)"},
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
        return {"sector": "미분류 (Unmapped)", "theme": "일반 (General)"}

    @classmethod
    def get_sector(cls, asset_id: str) -> str:
        return cls.get_info(asset_id)["sector"]

    @classmethod
    def get_theme(cls, asset_id: str) -> str:
        return cls.get_info(asset_id)["theme"]
