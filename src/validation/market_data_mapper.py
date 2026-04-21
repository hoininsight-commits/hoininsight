# src/validation/market_data_mapper.py
import json
from pathlib import Path
from datetime import datetime
from src.validation.market_thresholds import THRESHOLDS, ASSET_TYPE_MAP

# 내부 보조 함수: 실제 시장 데이터 로드
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
            f_data = stats.get(field, {})
            return {"current": f_data.get("current", 0), "change": f_data.get("change_1d", 0)}
        elif filename == "fred.json":
            return {"current": data.get(field, 0), "change": 0}
    except: return None
    return None

def load_market_intelligence(signal_topic, base_dir, today):
    asset_type = "stocks"
    for key, val in ASSET_TYPE_MAP.items():
        if key in signal_topic:
            asset_type = val
            break
    actual = _fetch_raw_market_data(signal_topic, base_dir, today)
    return actual, asset_type

# Reality Score v2 (지능형 판정)
def calculate_reality_score_v2(analysis_data, actual_data, asset_type="stocks"):
    if not actual_data or not analysis_data: return 0
    
    claim = analysis_data.get("topic_core_claim", "")
    change = actual_data.get("change", 0)
    
    score = 0
    # 1. 방향성 (2점)
    dir_ok = False
    if "상승" in claim or "강체" in claim or "롱" in claim: dir_ok = change > 0
    elif "하락" in claim or "약세" in claim or "숏" in claim: dir_ok = change < 0
    if dir_ok: score += 2
    
    # 2. 트렌드 (1점) - 임시 (추후 MA 연동)
    score += 1 
    
    # 3. 강도 (2점)
    threshold = THRESHOLDS.get(asset_type, 0.005)
    if abs(change) > threshold: score += 2
    
    return score

# 최종 의사결정 v3 (다중 인자 지원)
def final_decision_v3(q_score, v_score, reality_score, trust):
    # Tier 3 (Early Signal): 현실 데이터가 아직 반영되지 않았거나 미비한 경우
    if reality_score <= 1: return "DROP" 
    
    # Tier 1 (High Confidence): 품질과 현실 데이터가 모두 완벽한 경우
    if reality_score >= 4 and q_score >= 90 and trust == "HIGH_TRUST":
        return "USE"
    
    # Tier 2 (Conditional): 품질은 좋으나 현실 데이터 검증이 필요하거나 중간 단계인 경우
    return "REVIEW"

def log_forward_prediction(topic, claim, base_dir):
    log_path = Path(base_dir) / "data/validation/forward_validation.json"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    prediction = "상승" if any(k in claim for k in ["상승", "강세", "롱"]) else "하락" if any(k in claim for k in ["하락", "약세", "숏"]) else "중립"
    entry = {"topic": topic, "claim": claim, "prediction": prediction, "timestamp": datetime.now().isoformat(), "status": "PENDING"}
    history = []
    if log_path.exists():
        try: history = json.loads(log_path.read_text())
        except: pass
    history.append(entry)
    log_path.write_text(json.dumps(history[-100:], indent=2, ensure_ascii=False))
