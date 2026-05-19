"""
market_context.json 자동 갱신 (Gemini 미사용)

갱신 항목:
  - stages[*].is_current  → 에너지 피크 스테이지
  - stages[*].basis       → 실제 등락률/모멘텀 데이터로 생성한 템플릿 문자열
  - market_mood           → 전략 코드 기반 문구
  - last_updated / rotation_score / strategy
"""

import json
from datetime import datetime
from pathlib import Path

STAGE_ORDER = [
    "STAGE_1_SPARK",
    "STAGE_2_SKELETON",
    "STAGE_3_BODY",
    "STAGE_4_SOUL",
    "STAGE_5_TAIL",
]

TREND_LABEL = {
    "PEAK":    "에너지 피크 구간",
    "RISING":  "상승 추세 진입 중",
    "FALLING": "에너지 이탈 중",
    "STABLE":  "횡보 구간",
}

MOOD_LABEL = {
    "HOLD":           "대장주 집중 구간 (반도체 독주)",
    "WATCH":          "순환매 준비 국면",
    "ROTATE_START":   "Earnings-based Rotation 초기 진입",
    "ROTATE_CONFIRM": "순환매 본격화 확인",
}


def _compute_trends(flow_timeline: list) -> dict:
    """flow_timeline(최근 N일 스테이지 등락률 시계열) → 스테이지별 TREND 문자열."""
    if len(flow_timeline) < 2:
        return {}

    today_vals     = flow_timeline[-1]["values"]
    yesterday_vals = flow_timeline[-2]["values"]
    all_by_stage   = {
        sid: [day["values"].get(sid, 0) for day in flow_timeline]
        for sid in STAGE_ORDER
    }

    trends = {}
    for sid in STAGE_ORDER:
        t_val = today_vals.get(sid, 0)
        y_val = yesterday_vals.get(sid, 0)
        all_vals = all_by_stage.get(sid, [])

        if all_vals and t_val == max(all_vals) and t_val > 2.0:
            trends[sid] = "PEAK"
        elif t_val > y_val:
            trends[sid] = "RISING"
        elif t_val < y_val:
            trends[sid] = "FALLING"
        else:
            trends[sid] = "STABLE"

    return trends


def _build_basis(stage_id: str, change_today, s4_info: dict, trend: str) -> str:
    """스테이지 basis 문자열을 실제 데이터로 생성."""
    parts = []

    if change_today is not None:
        parts.append(f"오늘 평균 등락률 {change_today:+.1f}%")

    avg_5d  = s4_info.get("avg_5d")
    avg_20d = s4_info.get("avg_20d")
    if avg_5d is not None and avg_20d is not None:
        direction = "↑ 모멘텀 가속" if avg_5d > avg_20d else "↓ 모멘텀 둔화"
        parts.append(f"5일 평균 {avg_5d:+.1f}% / 20일 {avg_20d:+.1f}% ({direction})")

    if trend and trend in TREND_LABEL:
        parts.append(TREND_LABEL[trend])

    return ". ".join(parts) + "." if parts else ""


def auto_update(context_path: Path, evaluation: dict, signals: dict, flow_timeline: list) -> None:
    """
    market_context.json을 규칙 기반으로 자동 갱신.

    context_path  : data/monitoring/market_context.json 경로
    evaluation    : confirmation_engine.evaluate() 결과
    signals       : signals.py 각 compute_signal_*() 결과 모음
    flow_timeline : RotationRadar.get_flow_timeline() 결과
    """
    if not context_path.exists():
        print(f"  ⚠️ context_path 없음: {context_path}")
        return

    context = json.loads(context_path.read_text(encoding="utf-8"))
    stages  = context.get("stages", {})

    current_stage = evaluation.get("current_stage")
    strategy      = evaluation.get("strategy", "HOLD")
    stage_changes = signals.get("signal_5", {}).get("stage_changes", {})
    s4_stage_data = signals.get("signal_4", {}).get("stage_data", {})
    trends        = _compute_trends(flow_timeline)

    for stage_id in stages:
        change_today = stage_changes.get(stage_id)
        s4_info      = s4_stage_data.get(stage_id, {})
        trend        = trends.get(stage_id, "STABLE")

        basis = _build_basis(stage_id, change_today, s4_info, trend)
        if basis:
            context["stages"][stage_id]["basis"] = basis

        context["stages"][stage_id]["is_current"] = (stage_id == current_stage)

    context["market_mood"]      = MOOD_LABEL.get(strategy, context.get("market_mood", "Normal"))
    context["last_updated"]     = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    context["rotation_score"]   = evaluation.get("raw_score", 0)
    context["strategy"]         = strategy
    context["next_stage"]       = evaluation.get("next_stage")
    context["confirmed_signals"] = evaluation.get("confirmed_signals", 0)

    context_path.write_text(
        json.dumps(context, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"  ✅ market_context.json 갱신 완료: {strategy} (스코어 {evaluation.get('raw_score', 0)}/19)")
