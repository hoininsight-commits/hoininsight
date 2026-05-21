"""
순환매 신호 5개 계산 모듈 (Gemini 미사용, 순수 규칙 기반)

Signal 1: 시장폭 — advancing > declining × 2 연속 streak
Signal 2: 호재 무반응 — 대장주 KOSPI 대비 지속 언더퍼폼
Signal 3: 외국인 수급 이동 — 반도체 연속 순매도 + 타 업종 연속 순매수
Signal 4: 이익 추정치 상향 — 네이버 리서치 대장주 목표주가 상향 리포트 탐지
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


# ─── Signal 4: 이익 추정치 상향 ────────────────────────────

LEAD_STAGE = "STAGE_1_SPARK"

_NAVER_RESEARCH_URL = (
    "https://finance.naver.com/research/company_list.naver"
    "?searchType=itemCode&itemCode={ticker}"
)
_NAVER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}
# 제목에 이 키워드가 있으면 상향 리포트로 간주
_UPGRADE_KEYWORDS = ["상향", "목표 상향", "TP 상향", "목표가 상향", "투자의견 상향", "Up"]
# 제목에 이 키워드가 있으면 하향/중립으로 제외
_DOWNGRADE_KEYWORDS = ["하향", "중립", "HOLD", "SELL", "매도"]


def _fetch_research_reports(ticker: str, days: int = 7) -> list[dict]:
    """네이버 증권 리서치 리포트 스크래핑 (최근 N일)"""
    import requests
    from bs4 import BeautifulSoup

    cutoff = datetime.now() - timedelta(days=days)
    url = _NAVER_RESEARCH_URL.format(ticker=ticker)

    try:
        resp = requests.get(url, headers=_NAVER_HEADERS, timeout=10)
        resp.encoding = "euc-kr"
        soup = BeautifulSoup(resp.text, "html.parser")

        table = soup.find("table", class_="type_1")
        if not table:
            return []

        reports = []
        for row in table.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) < 5:
                continue

            title_tag = cols[1].find("a")
            date_td = cols[4]
            if not title_tag or not date_td:
                continue

            title = title_tag.get_text().strip()
            date_str = date_td.get_text().strip()  # 형식: "26.05.21"

            try:
                report_date = datetime.strptime("20" + date_str, "%Y.%m.%d")
            except ValueError:
                continue

            if report_date < cutoff:
                break  # 날짜 내림차순 정렬이므로 이후는 모두 오래된 것

            reports.append({"title": title, "date": date_str})

        return reports

    except Exception:
        return []


def _classify_report(title: str) -> str:
    """리포트 제목 → 'upgrade' / 'downgrade' / 'neutral'"""
    if any(kw in title for kw in _DOWNGRADE_KEYWORDS):
        return "downgrade"
    if any(kw in title for kw in _UPGRADE_KEYWORDS):
        return "upgrade"
    return "neutral"


def compute_signal_4(context_path: Path = None) -> dict:
    """
    네이버 증권 리서치에서 대장주 목표주가 상향 리포트를 탐지해
    이익 추정치 개선 신호를 계산한다.

    confirmed 조건: 대장주 중 2종목 이상 최근 7일 내 상향 리포트 보유
    score: 상향 리포트 확인 종목 수 (최대 3)
    """
    lead_tickers = _load_lead_tickers(context_path)

    per_stock: dict[str, dict] = {}
    upgrade_stock_count = 0
    all_upgrade_reports: list[dict] = []

    for ticker, name in lead_tickers.items():
        reports = _fetch_research_reports(ticker, days=7)
        if not reports:
            per_stock[name] = {"total": 0, "upgrades": 0, "reports": []}
            continue

        classified = [{"title": r["title"], "date": r["date"],
                        "type": _classify_report(r["title"])} for r in reports]
        upgrades = [r for r in classified if r["type"] == "upgrade"]

        per_stock[name] = {
            "total": len(classified),
            "upgrades": len(upgrades),
            "reports": classified[:5],  # 최신 5개만 보관
        }

        if upgrades:
            upgrade_stock_count += 1
            all_upgrade_reports.extend(
                {"ticker": ticker, "name": name, **r} for r in upgrades
            )

    if not per_stock:
        return {
            "score": 0, "confirmed": False, "status": "NO_DATA",
            "message": "⚠️ 리서치 데이터 없음",
            "per_stock": {},
            "upgrade_reports": [],
        }

    confirmed = upgrade_stock_count >= 2
    score = min(upgrade_stock_count, 3)

    if confirmed:
        status = "UPGRADE_CONFIRMED"
    elif upgrade_stock_count == 1:
        status = "UPGRADE_WATCH"
    else:
        status = "NO_UPGRADE"

    icon = "✅" if confirmed else ("👀" if upgrade_stock_count == 1 else "⏸")
    stocks_with_upgrade = [n for n, d in per_stock.items() if d["upgrades"] > 0]

    return {
        "score": score,
        "confirmed": confirmed,
        "status": status,
        "upgrade_stock_count": upgrade_stock_count,
        "per_stock": per_stock,
        "upgrade_reports": all_upgrade_reports[:10],
        "message": (
            f"{icon} 목표주가 상향 {upgrade_stock_count}개 종목: "
            f"{stocks_with_upgrade or '없음'}"
        ),
    }


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
