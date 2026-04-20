# src/validation/outcome_tracker.py
import json
from pathlib import Path
from datetime import datetime
from src.validation.result_classifier import classify_result

LOG_PATH = Path("data/validation/outcome_log.json")

def record_outcome(signal, decision, market_data):
    """오늘의 결정을 PENDING 상태로 기록"""
    log = []
    if LOG_PATH.exists():
        try:
            log = json.loads(LOG_PATH.read_text())
        except:
            log = []

    entry = {
        "date": signal.get("date", datetime.now().strftime("%Y-%m-%d")),
        "topic": signal.get("topic", "Unknown"),
        "action": decision.get("action", "HOLD"),
        "confidence": decision.get("confidence", 0.0),
        "target_asset": decision.get("asset", "KOSPI"),
        "entry_price": market_data.get("entry", 0),
        "exit_price": None,
        "result": "PENDING",
        "return_pct": 0.0,
        "failure_type": None
    }
    
    log.append(entry)
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text(json.dumps(log, ensure_ascii=False, indent=2))
    return entry

def update_pending_outcomes(current_market_data):
    """PENDING 상태인 이전 기록들을 현재 시장가 데이터로 업데이트"""
    if not LOG_PATH.exists():
        return []

    log = json.loads(LOG_PATH.read_text())
    updated_count = 0
    
    for entry in log:
        if entry["result"] == "PENDING":
            # 단순화를 위해 진입가 대비 현재가를 출구가로 가정 (실제 배포시는 일정 기간 경과 후 측정)
            asset = entry["target_asset"]
            current_price = current_market_data.get(asset, current_market_data.get("current", 0))
            
            if entry["entry_price"] > 0 and current_price > 0:
                entry["exit_price"] = current_price
                return_pct = ((current_price - entry["entry_price"]) / entry["entry_price"]) * 100
                entry["return_pct"] = round(return_pct, 2)
                entry["result"] = classify_result(entry["action"], return_pct)
                updated_count += 1

    if updated_count > 0:
        LOG_PATH.write_text(json.dumps(log, ensure_ascii=False, indent=2))
    
    return log
