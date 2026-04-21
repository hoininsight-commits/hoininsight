import json
from pathlib import Path
from datetime import datetime, timedelta

def generate_dummy_data():
    log_path = Path("data/validation/outcome_log.json")
    state_path = Path("data/validation/decision_state.json")
    
    # 1. outcome_log.json - 최근 10일치 (7일 성공, 3일 실패)
    history = []
    base_date = datetime.now() - timedelta(days=10)
    
    for i in range(10):
        date = (base_date + timedelta(days=i)).strftime("%Y-%m-%d")
        # 3, 7, 9일은 실패로 가정
        is_fail = i in [3, 7, 9]
        
        history.append({
            "date": date,
            "topic": f"Dummy Topic {i}",
            "action": "BUY" if i % 2 == 0 else "WATCH",
            "confidence": 0.65 + (i * 0.02),
            "target_asset": "KOSPI",
            "entry_price": 2500 + i,
            "exit_price": 2520 + (i if not is_fail else -30),
            "result": "FAIL" if is_fail else "SUCCESS",
            "return_pct": 1.2 if not is_fail else -1.5,
            "failure_type": "FLOW_MISREAD" if is_fail else None
        })
    
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(json.dumps(history, ensure_ascii=False, indent=2))
    print(f"Created dummy history at {log_path}")

    # 2. daily_validation.json - 오늘자 리포트 미리 생성
    daily_report = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "success_rate": 0.70,
        "fail_rate": 0.30,
        "neutral_rate": 0.00,
        "top_failure_reason": "FLOW_MISREAD"
    }
    report_path = Path("data/validation/daily_validation.json")
    report_path.write_text(json.dumps(daily_report, ensure_ascii=False, indent=2))
    print(f"Created daily report at {report_path}")

    # 3. 가중치 초기 상태 (실패 반영 전)
    initial_weights = {
        "flow": 0.35,
        "price": 0.25,
        "event": 0.25,
        "consistency": 0.15
    }
    state_path.write_text(json.dumps({"weights": initial_weights}, indent=2))
    print(f"Initialized weights at {state_path}")

if __name__ == "__main__":
    generate_dummy_data()
