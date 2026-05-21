"""
Rotation Radar v5.0 — 순수 규칙 기반 (Gemini 미사용)

실행: python scripts/rotation_radar.py
출력: data/monitoring/rotation_radar.json
      data/monitoring/market_context.json (자동 갱신)
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _sanitize(obj):
    """NaN/Infinity → None (JSON 스펙에 없는 float 값 제거)"""
    import math
    if isinstance(obj, float):
        return None if (math.isnan(obj) or math.isinf(obj)) else obj
    if isinstance(obj, dict):
        return {k: _sanitize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize(v) for v in obj]
    return obj

from src.rotation import signals as sig
from src.rotation import confirmation_engine as engine
from src.rotation import context_manager as ctx_mgr
from src.rotation.stage_context_builder import StageContextBuilder
from src.utils.paths import RAW_DIR

CONTEXT_PATH = ROOT / "data" / "monitoring" / "market_context.json"
OUTPUT_PATH  = ROOT / "data" / "monitoring" / "rotation_radar.json"
DOCS_OUTPUT_PATH = ROOT / "docs" / "data" / "monitoring" / "rotation_radar.json"


# ─── pykrx 기반 스테이지 타임라인 ──────────────────────────

def get_flow_timeline(stages_config: dict, days: int = 15) -> list:
    print("🌊 타임라인 분석 중...")
    try:
        import pandas as pd
        from pykrx import stock

        end   = datetime.now().strftime("%Y%m%d")
        start = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")

        stage_series = {}
        for sid, info in stages_config.items():
            tickers = info.get("tickers", [])
            series_list = []
            for t in tickers:
                try:
                    df = stock.get_market_ohlcv_by_date(start, end, t)
                    if not df.empty:
                        series_list.append(df["등락률"])
                except Exception:
                    continue
            if series_list:
                import pandas as _pd
                stage_series[sid] = _pd.concat(series_list, axis=1).mean(axis=1)

        if not stage_series:
            return []

        import pandas as _pd
        df_flow = _pd.DataFrame(stage_series).tail(days).fillna(0)
        return [
            {"date": d.strftime("%m/%d"), "values": row.to_dict()}
            for d, row in df_flow.iterrows()
        ]
    except Exception as e:
        print(f"  ❌ 타임라인 오류: {e}")
        return []


# ─── DART 실적 신호 (선택적) ───────────────────────────────

def get_dart_signals(stages_config: dict, days: int = 3) -> dict:
    import os
    api_key = os.environ.get("OPENDART_API_KEY") or os.environ.get("DART_API_KEY")
    if not api_key:
        return {}

    print(f"📡 DART 신호 분석 중 (최근 {days}일)...")
    try:
        import OpenDartReader
        dart  = OpenDartReader(api_key)
        end   = datetime.now().strftime("%Y%m%d")
        start = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")

        df = dart.list(start=start, end=end)
        if df is None or df.empty:
            return {}

        target = df[df["report_nm"].str.contains(
            "공급계약|시설투자|수주|투자결정|전략적제휴|업무협약|자기주식|합병|분할|MOU",
            na=False
        )]
        result = {}

        for _, row in target.iterrows():
            title   = row["report_nm"]
            company = row["corp_name"]

            for stage_id, info in stages_config.items():
                if any(
                    kw.lower() in title.lower() or kw.lower() in company.lower()
                    for kw in info.get("keywords", [])
                ):
                    result.setdefault(stage_id, []).append({
                        "company": company,
                        "title":   title,
                        "date":    row["rcept_dt"],
                        "link":    f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={row['rcept_no']}"
                    })
        return result

    except Exception as e:
        print(f"  ❌ DART 오류: {e}")
        return {}


# ─── 스테이지별 당일 종목 현황 ─────────────────────────────

def get_tracking_data(stages_config: dict) -> dict:
    try:
        from pykrx import stock
        today = datetime.now().strftime("%Y%m%d")
        result = {}

        for sid, info in stages_config.items():
            stocks_info = []
            for t in info.get("tickers", []):
                try:
                    name = stock.get_market_ticker_name(t)
                    df   = stock.get_market_ohlcv_by_date(today, today, t)
                    chg  = float(df["등락률"].iloc[0]) if not df.empty else 0.0
                    stocks_info.append({"name": name, "ticker": t, "change": chg})
                except Exception:
                    continue
            result[sid] = stocks_info

        return result
    except Exception as e:
        print(f"  ❌ 종목 현황 오류: {e}")
        return {}


# ─── 스테이지 색상 ──────────────────────────────────────────

def _stage_color(stage_id: str) -> str:
    return {
        "STAGE_1_SPARK":    "#00f2ff",
        "STAGE_2_SKELETON": "#00ff88",
        "STAGE_3_BODY":     "#ffea00",
        "STAGE_4_SOUL":     "#ff8800",
        "STAGE_5_TAIL":     "#ff007a",
    }.get(stage_id, "#ffffff")


# ─── 메인 실행 ─────────────────────────────────────────────

def run():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # ── 스테이지 컨텍스트 자동 빌드 (6시간마다 or force) ──
    force = "--force" in sys.argv
    StageContextBuilder(CONTEXT_PATH).build(force=force)  # noqa: kospi only

    if not CONTEXT_PATH.exists():
        print(f"❌ market_context.json 생성 실패: {CONTEXT_PATH}")
        return

    context       = json.loads(CONTEXT_PATH.read_text(encoding="utf-8"))
    stages_config = context.get("stages", {})

    # ── 신호 5개 계산 ──
    print("🔍 순환매 신호 분석 중...")
    computed_signals = {
        "signal_1": sig.compute_signal_1(RAW_DIR),
        "signal_2": sig.compute_signal_2(CONTEXT_PATH),
        "signal_3": sig.compute_signal_3(RAW_DIR),
        "signal_4": sig.compute_signal_4(CONTEXT_PATH),
        "signal_5": sig.compute_signal_5(stages_config),
    }

    for v in computed_signals.values():
        print(f"  {v.get('message', '')}")

    # ── 종합 판정 ──
    evaluation = engine.evaluate(computed_signals, stages_config)
    print(f"\n📊 순환매 스코어: {evaluation['raw_score']}/19  전략: {evaluation['strategy_kor']}")

    # ── 타임라인 + DART ──
    flow_timeline = get_flow_timeline(stages_config)
    dart_signals  = get_dart_signals(stages_config)
    tracking_data = get_tracking_data(stages_config)

    # ── 스테이지별 출력 구성 ──
    stage_changes = computed_signals["signal_5"].get("stage_changes", {})

    def _avg_change(sid):
        stocks = tracking_data.get(sid, [])
        if not stocks:
            return stage_changes.get(sid, 0.0)
        return sum(s["change"] for s in stocks) / len(stocks)

    stages_out = {}
    s4_upgrade_reports = computed_signals["signal_4"].get("upgrade_reports", [])
    s4_per_stock = computed_signals["signal_4"].get("per_stock", {})

    for sid, info in stages_config.items():
        avg_chg = _avg_change(sid)

        stages_out[sid] = {
            "name":             info["name"],
            "desc":             info.get("desc", ""),
            "basis":            info.get("basis", ""),
            "color":            _stage_color(sid),
            "is_current":       sid == evaluation.get("current_stage"),
            "active":           sid in evaluation.get("active_stages", []) or bool(dart_signals.get(sid)),
            "dart_signals":     dart_signals.get(sid, []),
            "tracking_stocks":  tracking_data.get(sid, []),
            "avg_change_today": round(avg_chg, 2),
        }

    # Signal 4 리포트 정보는 stages 아닌 signal_detail에 그대로 노출됨

    # ── 최종 JSON 저장 ──
    analysis = {
        "last_updated":      datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "market_mood":       context.get("market_mood", "Normal"),
        "rotation_score":    evaluation["raw_score"],
        "strategy":          evaluation["strategy"],
        "strategy_kor":      evaluation["strategy_kor"],
        "rotation_active":   evaluation["rotation_active"],
        "breadth_confirmed": evaluation["breadth_confirmed"],
        "current_stage":     evaluation.get("current_stage"),
        "next_stage":        evaluation.get("next_stage"),
        "confirmed_signals": evaluation["confirmed_signals"],
        "signals": {
            k: {
                "score":     v.get("score", 0),
                "confirmed": v.get("confirmed", False),
                "status":    v.get("status", ""),
                "message":   v.get("message", ""),
            }
            for k, v in computed_signals.items()
        },
        "signal_detail": computed_signals,
        "flow_timeline": flow_timeline,
        "stages":        stages_out,
        "summary":       evaluation.get("summary", []),
    }

    sanitized = json.dumps(_sanitize(analysis), ensure_ascii=False, indent=2, default=str)
    OUTPUT_PATH.write_text(sanitized, encoding="utf-8")
    DOCS_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOCS_OUTPUT_PATH.write_text(sanitized, encoding="utf-8")
    print(f"✅ rotation_radar.json 저장: {OUTPUT_PATH}")
    print(f"✅ rotation_radar.json 동기화: {DOCS_OUTPUT_PATH}")

    # ── market_context.json 자동 갱신 ──
    ctx_mgr.auto_update(CONTEXT_PATH, evaluation, computed_signals, flow_timeline)


if __name__ == "__main__":
    run()
