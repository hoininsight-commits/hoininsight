# src/validation/market_data_mapper.py
import json
from pathlib import Path
from datetime import datetime
from src.validation.market_thresholds import THRESHOLDS, ASSET_TYPE_MAP

# 내부 보조 함수: 실제 시장 데이터 로드 (기존 load_actual_market_data 로직 통합)
def _fetch_raw_market_data(signal_topic, base_dir, today):
    MARKET_DATA_MAP = {
        "금리": ("fred.json", "us10y_fred"),
        "주식": ("market.json", "sp500"),
        "나스닥": ("market.json", "nasdaq"),
        "달러": ("market.json", "dxy_index"),
        "유가": ("market.json", "wti_oil"),
    }
    
    target = None
    for key, val in MARKET_DATA_MAP.items():
        if key in signal_topic:
            target = val
            break
    
    if not target: return None

    filename, field = target
    raw_path = Path(base_dir) / f"data/raw/{today}/{filename}"
    if not raw_path.exists(): return None

    try:
        data = json.loads(raw_path.read_text())
        if filename == "market.json":
            stats = data.get("data", {}).get("multi_period_stats", {})
            return {"current": stats.get(field, {}).get("current", 0), "change": stats.get(field, {}).get("change_1d", 0)}
        elif filename == "fred.json":
            return {"current": data.get(field, 0), "change": 0}
    except: return None
    return None

# Task 3 — 트렌드 계산 (Moving Average)
def calculate_trend(data_list, window=3):
    if not data_list or len(data_list) == 0: return 0
    recent = data_list[-window:]
    return sum(recent) / len(recent)

# Task 4 — 방향성 검증 개선 (Trend 기반)
def validate_trend_direction(claim, history_data):
    if not history_data or len(history_data) < 6: return None
    prev_ma = calculate_trend(history_data[-6:-3])
    curr_ma = calculate_trend(history_data[-3:])
    if "상승" in claim or "강세" in claim: return curr_ma > prev_ma
    if "하락" in claim or "약세" in claim: return curr_ma < prev_ma
    return None

# Task 5 — 자산별 강도 검증 v2
def validate_magnitude_v2(actual_data, asset_type):
    if not actual_data: return 0
    change = actual_data.get("change", 0)
    threshold = THRESHOLDS.get(asset_type, 0.005)
    return 1 if abs(change) > threshold else 0

# Task 6 — Reality Score v2 산출 (0~5점)
def calculate_reality_score_v2(direction_ok, trend_ok, magnitude_ok):
    score = 0
    if direction_ok: score += 2
    if trend_ok: score += 2
    if magnitude_ok: score += 1
    return score

# Task 7 — 미래 성과 추적 (Logging)
def log_forward_prediction(topic, claim, base_dir):
    log_path = Path(base_dir) / "data/validation/forward_validation.json"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    prediction = "상승" if "상승" in claim or "강세" in claim else "하락" if "하락" in claim or "약세" in claim else "중립"
    entry = {"topic": topic, "claim": claim, "prediction": prediction, "timestamp": datetime.now().isoformat(), "status": "PENDING"}
    history = []
    if log_path.exists():
        try: history = json.loads(log_path.read_text())
        except: pass
    history.append(entry)
    log_path.write_text(json.dumps(history[-100:], indent=2, ensure_ascii=False))

# Task 2 & 3 보강 — 지능형 로드 인터페이스
def load_market_intelligence(signal_topic, base_dir, today):
    asset_type = "stocks"
    for key, val in ASSET_TYPE_MAP.items():
        if key in signal_topic:
            asset_type = val
            break
    actual = _fetch_raw_market_data(signal_topic, base_dir, today)
    return actual, asset_type

# Task 9 — 최종 의사결정 v2
def final_decision_v2(quality_action, reality_score):
    if reality_score <= 1: return "DROP"
    if reality_score >= 4 and quality_action == "USE": return "USE"
    return "REVIEW"
