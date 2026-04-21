# src/validation/market_thresholds.py
# Market Asset-Specific Thresholds (지시서 #085)

THRESHOLDS = {
    "rates": 0.0005,    # 금리 (0.05% 변화 시 유의미)
    "stocks": 0.005,    # 주식 (0.5% 변화 시 유의미)
    "crypto": 0.01      # 코인 (1% 변화 시 유의미)
}

ASSET_TYPE_MAP = {
    "금리": "rates",
    "채권": "rates",
    "지수": "stocks",
    "주식": "stocks",
    "나스닥": "stocks",
    "S&P": "stocks",
    "코인": "crypto",
    "비트코인": "crypto"
}
