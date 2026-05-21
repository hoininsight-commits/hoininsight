"""
5개 신호 종합 판정 + 스테이지 이동 감지

점수 체계:
  Signal 1 (시장폭)          × 2  → 최대 6점
  Signal 2 (호재 무반응)     × 1  → 최대 1점
  Signal 3 (수급 이동)       × 2  → 최대 6점
  Signal 4 (이익 추정치 상향) × 1  → 최대 3점
  Signal 5 (생태계 확장)     × 1  → 최대 3점
  합계 최대 19점

전략 맵:
  0~3   → HOLD          대장주 유지, 관망
  4~7   → WATCH         이군 섹터 소량 추가 준비
  8~12  → ROTATE_START  반도체 70%+ 유지 + 순환매 섹터 추가
  13~   → ROTATE_CONFIRM 순환매 본격화 확인, 비중 확대
"""

STAGE_ORDER = [
    "STAGE_1_SPARK",
    "STAGE_2_SKELETON",
    "STAGE_3_BODY",
    "STAGE_4_SOUL",
    "STAGE_5_TAIL",
]

STRATEGY_MAP = [
    (0,  3,  "HOLD",           "대장주 유지, 관망"),
    (4,  7,  "WATCH",          "이군 섹터 소량 추가 준비"),
    (8,  12, "ROTATE_START",   "반도체 70%+ 유지 + 순환매 섹터 추가"),
    (13, 99, "ROTATE_CONFIRM", "순환매 본격화 확인, 비중 확대"),
]

WEIGHTS = {
    "signal_1": 2,
    "signal_2": 1,
    "signal_3": 2,
    "signal_4": 1,
    "signal_5": 1,
}


def _strategy_for_score(score: int) -> tuple:
    for lo, hi, code, kor in STRATEGY_MAP:
        if lo <= score <= hi:
            return code, kor
    return "HOLD", "대장주 유지, 관망"


def _peak_stage(stage_changes: dict):
    if not stage_changes:
        return None
    best = max(stage_changes, key=stage_changes.get)
    return best if stage_changes[best] > 0 else None


def _next_stage(current):
    if current is None or current not in STAGE_ORDER:
        return None
    idx = STAGE_ORDER.index(current)
    return STAGE_ORDER[idx + 1] if idx + 1 < len(STAGE_ORDER) else None


def evaluate(signals: dict, stages: dict) -> dict:
    """
    signals: {signal_1: {...}, signal_2: {...}, ...}  (signals.py 출력)
    stages:  market_context.json의 stages dict
    반환:    종합 판정 결과 dict
    """
    raw_score = sum(
        signals.get(k, {}).get("score", 0) * w
        for k, w in WEIGHTS.items()
    )

    confirmed_count = sum(
        1 for k in WEIGHTS if signals.get(k, {}).get("confirmed", False)
    )

    strategy, strategy_kor = _strategy_for_score(raw_score)

    # 현재 에너지 피크 스테이지 (Signal 5 당일 등락률 기반)
    stage_changes = signals.get("signal_5", {}).get("stage_changes", {})

    # 당일 등락률 기준으로 피크 스테이지 결정 (Signal 5만 사용)
    combined_map = stage_changes

    current_stage = _peak_stage(combined_map)
    next_stg = _next_stage(current_stage)

    # 각 스테이지 활성 여부 (당일 +0.5% 이상 or DART 신호 있음)
    active_stages = signals.get("signal_5", {}).get("positive_stages", [])

    # 확인 신호: Signal 1이 CONFIRMED (3일 연속 2배+)
    breadth_confirmed = signals.get("signal_1", {}).get("confirmed", False)

    summary_lines = [f"[{k.upper()}] {signals[k]['message']}"
                     for k in WEIGHTS if k in signals and "message" in signals[k]]

    return {
        "raw_score": raw_score,
        "confirmed_signals": confirmed_count,
        "strategy": strategy,
        "strategy_kor": strategy_kor,
        "rotation_active": strategy in ("ROTATE_START", "ROTATE_CONFIRM"),
        "breadth_confirmed": breadth_confirmed,
        "current_stage": current_stage,
        "next_stage": next_stg,
        "active_stages": active_stages,
        "summary": summary_lines,
    }
