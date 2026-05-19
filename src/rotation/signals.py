"""
순환매 신호 5개 계산 모듈 (Gemini 미사용, 순수 규칙 기반)

Signal 1: 시장폭 — advancing > declining × 2 연속 streak
Signal 2: 호재 무반응 — 대장주 KOSPI 대비 지속 언더퍼폼
Signal 3: 외국인 수급 이동 — 반도체 연속 순매도 + 타 업종 연속 순매수
Signal 4: 모멘텀 확장 — 비대장 스테이지 5일 모멘텀 > 20일 모멘텀
Signal 5: 생태계 확장 — 3개 이상 스테이지 동반 양봉
"""

from pathlib import Path
from datetime import datetime, timedelta
import json


# ─── 공통 유틸 ──────────────────────────────────────────────

def _load_recent_breadth(raw_dir: Path, days: int = 7) -> list:
    files = sorted(raw_dir.glob("**/market_breadth_*.json"), reverse=True)
    out = []
    for f in files[:days]:
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
            kospi = d.get("data", {}).get("markets", {}).get("KOSPI", {})
            if kospi:
                out.append(kospi)
        except Exception:
            continue
    return out


def _load_recent_sector_flow(raw_dir: Path, days: int = 7) -> list:
    files = sorted(raw_dir.glob("**/sector_flow_*.json"), reverse=True)
    out = []
    for f in files[:days]:
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
            sectors = d.get("data", {}).get("sectors", [])
            if sectors:
                out.append(sectors)
        except Exception:
            continue
    return out


def _pykrx_date_range(lookback_days: int = 40) -> tuple:
    end = datetime.now().strftime("%Y%m%d")
    start = (datetime.now() - timedelta(days=lookback_days)).strftime("%Y%m%d")
    return start, end


# ─── Signal 1: 시장폭 ──────────────────────────────────────

def compute_signal_1(raw_dir: Path) -> dict:
    """advancing > declining × 2 가 몇 일 연속인지 체크."""
    history = _load_recent_breadth(raw_dir, days=7)

    if not history:
        return {
            "score": 0, "confirmed": False, "status": "NO_DATA",
            "streak": 0, "message": "⚠️ 시장폭 데이터 없음"
        }

    streak = 0
    for h in history:
        adv = h.get("advancing", 0)
        dec = h.get("declining", 1)
        if dec > 0 and adv > dec * 2:
            streak += 1
        else:
            break

    latest = history[0]
    adv = latest.get("advancing", 0)
    dec = latest.get("declining", 1)
    ratio = round(adv / dec, 2) if dec > 0 else 0.0

    confirmed = streak >= 3
    score = min(streak, 3)

    if confirmed:
        status = "CONFIRMED"
    elif streak >= 1:
        status = "WATCH"
    elif ratio > 1.0:
        status = "WEAK"
    else:
        status = "IDLE"

    icon = "✅" if confirmed else ("👀" if streak >= 1 else "⏸")
    return {
        "score": score,
        "confirmed": confirmed,
        "status": status,
        "streak": streak,
        "latest_ratio": ratio,
        "latest_advancing": adv,
        "latest_declining": dec,
        "message": f"{icon} 시장폭 {streak}일 연속 2배+ (상승 {adv} / 하락 {dec}, 비율 {ratio}x)"
    }


# ─── Signal 2: 호재 무반응 ─────────────────────────────────

_FALLBACK_LEAD_TICKERS = {"005930": "삼성전자", "000660": "SK하이닉스"}


def _load_lead_tickers(context_path: Path = None) -> dict:
    """market_context.json leaders에서 동적으로 대장주 목록 로드. 실패 시 폴백."""
    if context_path and context_path.exists():
        try:
            ctx = json.loads(context_path.read_text(encoding="utf-8"))
            leaders = ctx.get("leaders", [])
            if leaders:
                return {l["ticker"]: l["name"] for l in leaders}
        except Exception:
            pass
    return _FALLBACK_LEAD_TICKERS


def compute_signal_2(context_path: Path = None) -> dict:
    """대장주가 KOSPI 대비 5일 / 10일 연속 언더퍼폼 → 프라이스드인 판정."""
    try:
        from pykrx import stock

        start, end = _pykrx_date_range(40)

        # KODEX 200 (069500)을 KOSPI 프록시로 사용
        # (pykrx get_index_ohlcv_by_date 버전 호환 이슈 우회)
        kospi_df = stock.get_market_ohlcv_by_date(start, end, "069500")
        if kospi_df.empty:
            return {"score": 0, "confirmed": False, "status": "NO_DATA",
                    "message": "⚠️ KOSPI 데이터 없음"}

        kospi_5d = kospi_df["등락률"].tail(5).mean()
        kospi_10d = kospi_df["등락률"].tail(10).mean()

        lead_5d_vals, lead_10d_vals = [], []
        per_stock = {}

        lead_tickers = _load_lead_tickers(context_path)
        for ticker, name in lead_tickers.items():
            df = stock.get_market_ohlcv_by_date(start, end, ticker)
            if df.empty:
                continue
            s5 = df["등락률"].tail(5).mean()
            s10 = df["등락률"].tail(10).mean()
            lead_5d_vals.append(s5)
            lead_10d_vals.append(s10)
            per_stock[name] = {"avg_5d": round(s5, 2), "avg_10d": round(s10, 2)}

        if not lead_5d_vals:
            return {"score": 0, "confirmed": False, "status": "NO_DATA",
                    "message": "⚠️ 대장주 데이터 없음"}

        avg_5d = sum(lead_5d_vals) / len(lead_5d_vals)
        avg_10d = sum(lead_10d_vals) / len(lead_10d_vals)
        diff_5d = avg_5d - kospi_5d
        diff_10d = avg_10d - kospi_10d

        # 5일 -2% 이상 언더퍼폼 AND 10일도 -1% 이상 → 프라이스드인 확인
        confirmed = diff_5d < -2.0 and diff_10d < -1.0
        score = 1 if (confirmed or diff_5d < -1.0) else 0

        if confirmed:
            status = "PRICE_IN"
        elif diff_5d < -1.0:
            status = "DIVERGING"
        else:
            status = "NORMAL"

        icon = "✅" if confirmed else ("👀" if diff_5d < -1.0 else "⏸")
        return {
            "score": score,
            "confirmed": confirmed,
            "status": status,
            "lead_avg_5d": round(avg_5d, 2),
            "kospi_5d": round(kospi_5d, 2),
            "underperform_5d": round(diff_5d, 2),
            "underperform_10d": round(diff_10d, 2),
            "per_stock": per_stock,
            "message": (
                f"{icon} 대장주 5일 {avg_5d:+.1f}% vs KOSPI {kospi_5d:+.1f}% "
                f"(차이 {diff_5d:+.1f}%)"
            )
        }

    except Exception as e:
        return {"score": 0, "confirmed": False, "status": "ERROR",
                "error": str(e), "message": f"❌ Signal2 오류: {e}"}


# ─── Signal 3: 외국인 수급 이동 ────────────────────────────

SEMI_KEYWORDS = ["반도체", "전기전자", "IT", "삼성"]

def compute_signal_3(raw_dir: Path) -> dict:
    """반도체 외인 N일 연속 순매도 AND 타 업종 동시 연속 순매수."""
    history = _load_recent_sector_flow(raw_dir, days=7)

    if not history:
        return {"score": 0, "confirmed": False, "status": "NO_DATA",
                "message": "⚠️ 수급 데이터 없음"}

    semi_sell_streak = 0
    alt_streak: dict[str, int] = {}

    for day_sectors in history:
        semi_net = sum(
            s.get("foreigner", 0) for s in day_sectors
            if any(kw in s.get("sector", "") for kw in SEMI_KEYWORDS)
        )

        if semi_net < 0:
            semi_sell_streak += 1
        else:
            break  # 연속성 끊김

        for s in day_sectors:
            name = s.get("sector", "")
            if s.get("foreigner", 0) > 0 and not any(kw in name for kw in SEMI_KEYWORDS):
                alt_streak[name] = alt_streak.get(name, 0) + 1

    # 3일 이상 연속 순매수인 업종만 이동 확인
    confirmed_sectors = {k: v for k, v in alt_streak.items() if v >= 3}
    confirmed = semi_sell_streak >= 3 and bool(confirmed_sectors)
    score = min(semi_sell_streak, 3) if semi_sell_streak >= 2 else 0

    if confirmed:
        status = "MIGRATION_CONFIRMED"
    elif semi_sell_streak >= 2:
        status = "MIGRATION_WATCH"
    else:
        status = "IDLE"

    icon = "✅" if confirmed else ("👀" if semi_sell_streak >= 2 else "⏸")
    return {
        "score": score,
        "confirmed": confirmed,
        "status": status,
        "semi_sell_streak": semi_sell_streak,
        "target_sectors": confirmed_sectors,
        "message": (
            f"{icon} 반도체 외인 순매도 {semi_sell_streak}일 연속 / "
            f"이동 업종: {list(confirmed_sectors.keys()) or '없음'}"
        )
    }


# ─── Signal 4: 모멘텀 확장 ─────────────────────────────────

LEAD_STAGE = "STAGE_1_SPARK"

def compute_signal_4(stages: dict) -> dict:
    """비대장 스테이지의 5일 모멘텀이 20일 모멘텀을 상회하면 자금 유입 가속."""
    try:
        import pandas as pd
        from pykrx import stock

        start, end = _pykrx_date_range(40)

        expanding = []
        stage_data = {}

        for stage_id, info in stages.items():
            if stage_id == LEAD_STAGE:
                continue

            tickers = info.get("tickers", [])
            series_list = []

            for ticker in tickers:
                try:
                    df = stock.get_market_ohlcv_by_date(start, end, ticker)
                    if not df.empty:
                        series_list.append(df["등락률"])
                except Exception:
                    continue

            if not series_list:
                stage_data[stage_id] = {"status": "NO_DATA"}
                continue

            combined = pd.concat(series_list, axis=1).mean(axis=1)
            avg_5d = float(combined.tail(5).mean())
            avg_20d = float(combined.tail(20).mean())

            # 최근 5일이 20일 평균보다 강하고 절대값도 양봉 → 자금 유입 가속
            is_expanding = avg_5d > avg_20d and avg_5d > 0.3

            if is_expanding:
                expanding.append(stage_id)

            stage_data[stage_id] = {
                "avg_5d": round(avg_5d, 2),
                "avg_20d": round(avg_20d, 2),
                "expanding": is_expanding
            }

        confirmed = len(expanding) >= 2
        score = min(len(expanding), 3)

        icon = "✅" if confirmed else "⏸"
        return {
            "score": score,
            "confirmed": confirmed,
            "status": "EXPANDING" if confirmed else "IDLE",
            "expanding_stages": expanding,
            "stage_data": stage_data,
            "message": f"{icon} {len(expanding)}개 스테이지 모멘텀 확장: {expanding}"
        }

    except Exception as e:
        return {"score": 0, "confirmed": False, "status": "ERROR",
                "error": str(e), "message": f"❌ Signal4 오류: {e}"}


# ─── Signal 5: 생태계 확장 ─────────────────────────────────

def compute_signal_5(stages: dict) -> dict:
    """당일 비대장 스테이지 3개 이상이 평균 +0.5% 이상 → 생태계 동반 상승."""
    try:
        from pykrx import stock

        today = datetime.now().strftime("%Y%m%d")
        positive = []
        stage_changes = {}

        for stage_id, info in stages.items():
            if stage_id == LEAD_STAGE:
                continue

            tickers = info.get("tickers", [])
            changes = []

            for ticker in tickers:
                try:
                    df = stock.get_market_ohlcv_by_date(today, today, ticker)
                    if not df.empty:
                        changes.append(float(df["등락률"].iloc[0]))
                except Exception:
                    continue

            if changes:
                avg = sum(changes) / len(changes)
                stage_changes[stage_id] = round(avg, 2)
                if avg > 0.5:
                    positive.append(stage_id)

        confirmed = len(positive) >= 3
        score = min(len(positive), 3)

        icon = "✅" if confirmed else ("👀" if len(positive) >= 2 else "⏸")
        return {
            "score": score,
            "confirmed": confirmed,
            "status": "ECOSYSTEM_EXPANDING" if confirmed else "IDLE",
            "positive_stages": positive,
            "stage_changes": stage_changes,
            "message": f"{icon} {len(positive)}개 생태계 스테이지 동반 상승: {positive}"
        }

    except Exception as e:
        return {"score": 0, "confirmed": False, "status": "ERROR",
                "error": str(e), "message": f"❌ Signal5 오류: {e}"}
