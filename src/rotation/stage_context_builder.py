"""
StageContextBuilder v2.0 — 시총 집중도 + 상관관계 기반 동적 스테이지

알고리즘:
  1. pykrx KOSPI 시총 기준 대장주 자동 탐지 (누적 시총 30%+ 달성하는 상위 종목군)
  2. 대장주 종목이 포함된 업종 → STAGE 1로 자동 지정
  3. 대장주 25일 일별 수익률 시계열 계산
  4. 네이버 79개 업종 상위 20개 추출 (당일 등락률 프리필터, 대장 업종 제외)
  5. 업종별 대표 종목 3개 → 25일 수익률 → 대장주 상관계수 계산
  6. 상관계수 내림차순 → STAGE 2(최고) ~ STAGE 5(최저) 자동 배정
  7. market_context.json에 leaders 정보 포함 저장
"""

import json
import math
import re
import time
from datetime import datetime, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# ── 스테이지 프레임워크 (개념 구조만 고정) ──────────────────
STAGE_FRAMEWORK = [
    {
        "id": "STAGE_1_SPARK", "role": "대장주", "color": "#00f2ff",
        "concept": "KOSPI 시총 집중도 기준 자동 탐지된 시장 주도 종목군",
    },
    {
        "id": "STAGE_2_SKELETON", "role": "직접 수혜", "color": "#00ff88",
        "concept": "대장주와 상관계수 최상위 — 이익이 직접 연결된 섹터",
    },
    {
        "id": "STAGE_3_BODY", "role": "2차 수혜", "color": "#ffea00",
        "concept": "대장주와 중간 상관계수 — 이익 확산이 닿는 실물 섹터",
    },
    {
        "id": "STAGE_4_SOUL", "role": "이익 확산", "color": "#ff8800",
        "concept": "대장주와 낮은 상관계수 — 후행하며 수혜받는 섹터",
    },
    {
        "id": "STAGE_5_TAIL", "role": "낙수 효과", "color": "#ff007a",
        "concept": "대장주와 가장 느슨한 상관계수 — 자금이 마지막으로 도달하는 섹터",
    },
]

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
REBUILD_INTERVAL_HOURS = 6
LEADER_TOP_N = 5        # 시총 상위 N개를 대장주로 선정
PRE_FILTER_TOP_N = 25   # 상관계수 계산 대상 업종 수 (속도 절충)


# ── 1. 대장주 탐지 ──────────────────────────────────────────

def _fetch_kospi_market_cap_ranking(top_n: int = 30) -> list:
    """
    네이버 KOSPI 시총 상위 종목 스크래핑.
    반환: [{"ticker": str, "name": str, "cap_bil": float}]  (cap_bil: 억원)
    """
    url = "https://finance.naver.com/sise/sise_market_sum.naver?sosok=0"
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.encoding = "cp949"
    soup = BeautifulSoup(resp.text, "html.parser")

    table = soup.find("table", class_="type_2")
    if not table:
        return []

    results = []
    for row in table.find_all("tr"):
        cols = row.find_all("td")
        if len(cols) < 7:
            continue
        a = cols[1].find("a")
        if not a:
            continue
        name = a.get_text().strip()
        href = a.get("href", "")
        m = re.search(r"code=(\d+)", href)
        if not m:
            continue
        ticker = m.group(1)

        raw = re.sub(r"[^0-9]", "", cols[6].get_text())
        cap_bil = float(raw) if raw else 0.0

        results.append({"ticker": ticker, "name": name, "cap_bil": cap_bil})
        if len(results) >= top_n:
            break

    return results


def detect_leaders() -> tuple:
    """
    KOSPI 시총 상위 LEADER_TOP_N 종목을 대장주로 선정.
    반환: (leaders_list, top_n_share_pct)
    top_n_share_pct: 상위 N종목이 전체 랭킹 합산 대비 차지하는 비율 (참고용)
    """
    try:
        ranking = _fetch_kospi_market_cap_ranking(top_n=50)
        if not ranking:
            raise ValueError("시총 랭킹 데이터 없음")

        total = sum(r["cap_bil"] for r in ranking)
        if total == 0:
            raise ValueError("시총 합계 0")

        top = ranking[:LEADER_TOP_N]
        top_sum = sum(r["cap_bil"] for r in top)
        concentration = top_sum / total * 100

        leaders = [
            {
                "ticker": r["ticker"],
                "name": r["name"],
                "cap_pct": round(r["cap_bil"] / total * 100, 2),
            }
            for r in top
        ]
        return leaders, round(concentration, 1)

    except Exception as e:
        print(f"  ⚠️ 대장주 탐지 실패: {e} → 폴백 사용")
        return [
            {"ticker": "005930", "name": "삼성전자", "cap_pct": 0},
            {"ticker": "000660", "name": "SK하이닉스", "cap_pct": 0},
        ], 0.0


# ── 2. 대장주 수익률 시계열 ─────────────────────────────────

def get_leader_returns(leaders: list, lookback_days: int = 60):
    """대장주 평균 일별 등락률 시계열 반환 (pandas Series)."""
    try:
        import pandas as pd
        from pykrx import stock

        end = datetime.now().strftime("%Y%m%d")
        start = (datetime.now() - timedelta(days=lookback_days)).strftime("%Y%m%d")

        series = []
        for ldr in leaders:
            df = stock.get_market_ohlcv_by_date(start, end, ldr["ticker"])
            if not df.empty:
                series.append(df["등락률"])

        if not series:
            return pd.Series(dtype=float)
        return pd.concat(series, axis=1).mean(axis=1)

    except Exception as e:
        import pandas as pd
        print(f"  ⚠️ 대장주 수익률 계산 실패: {e}")
        return pd.Series(dtype=float)


# ── 3. 네이버 업종 리스트 ──────────────────────────────────

def fetch_sector_list() -> list:
    """네이버 업종 리스트 (등락률 내림차순)."""
    url = "https://finance.naver.com/sise/sise_group.naver?type=upjong"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.encoding = "cp949"
        soup = BeautifulSoup(resp.text, "html.parser")
        table = soup.find("table", class_="type_1")
        if not table:
            return []

        results = []
        for row in table.find_all("tr"):
            cols = row.find_all("td")
            if not cols:
                continue
            name_tag = cols[0].find("a")
            if not name_tag:
                continue
            name = name_tag.get_text().strip()
            href = name_tag.get("href", "")
            m = re.search(r"no=(\d+)", href)
            sector_no = m.group(1) if m else None
            change = 0.0
            if len(cols) > 1:
                raw = re.sub(r"[^0-9.\-+]", "", cols[1].get_text())
                try:
                    change = float(raw)
                except ValueError:
                    pass
            results.append({"sector": name, "change": change, "no": sector_no})

        return sorted(results, key=lambda x: x["change"], reverse=True)
    except Exception as e:
        print(f"  ❌ 업종 리스트 수집 오류: {e}")
        return []


# ── 4. 업종 상세 → 대표 종목 ───────────────────────────────

def fetch_sector_tickers(sector_no: str, top_n: int = 5) -> list:
    """네이버 업종 상세에서 상위 종목 추출."""
    if not sector_no:
        return []
    url = f"https://finance.naver.com/sise/sise_group_detail.naver?type=upjong&no={sector_no}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.encoding = "cp949"
        soup = BeautifulSoup(resp.text, "html.parser")
        table = soup.find("table", class_="type_5")
        if not table:
            return []

        tickers = []
        for row in table.find_all("tr"):
            cols = row.find_all("td")
            if not cols:
                continue
            a = cols[0].find("a")
            if not a:
                continue
            name = a.get_text().strip().replace(" *", "").strip()
            href = a.get("href", "")
            m = re.search(r"code=([A-Z0-9]{6})", href)
            if not m:
                continue
            ticker = m.group(1)
            change = 0.0
            if len(cols) > 3:
                raw = re.sub(r"[^0-9.\-+]", "", cols[3].get_text())
                try:
                    change = float(raw)
                except ValueError:
                    pass
            tickers.append({"ticker": ticker, "name": name, "change": change})
            if len(tickers) >= top_n:
                break
        return tickers
    except Exception as e:
        print(f"    ❌ 업종 상세 오류 (no={sector_no}): {e}")
        return []


# ── 5. 상관계수 기반 업종 랭킹 ────────────────────────────

def rank_sectors_by_correlation(sector_list: list, leader_returns, leader_ticker_set: set) -> list:
    """
    업종별 대장주 수익률 상관계수 계산 → 내림차순 정렬.
    대장주 종목이 포함된 업종은 자동 제외 (STAGE 1으로 이미 배정).
    """
    try:
        import pandas as pd
        from pykrx import stock

        end = datetime.now().strftime("%Y%m%d")
        start = (datetime.now() - timedelta(days=60)).strftime("%Y%m%d")

        # 양봉 업종 우선 + 등락률 절댓값 기준 상위 PRE_FILTER_TOP_N개로 프리필터
        # 오늘 하락했더라도 절댓값이 크면 포함 (강한 수급 이동 가능성)
        positive = [s for s in sector_list if s["change"] > 0]
        negative = [s for s in sector_list if s["change"] <= 0]
        candidates = (
            sorted(positive, key=lambda x: x["change"], reverse=True) +
            sorted(negative, key=lambda x: abs(x["change"]), reverse=True)
        )[:PRE_FILTER_TOP_N]

        results = []
        for s in candidates:
            if not s.get("no"):
                continue

            tickers = fetch_sector_tickers(s["no"], top_n=3)
            time.sleep(0.2)

            # 대장주 종목이 이 업종에 포함되면 STAGE 1 업종 → 스킵
            if any(t["ticker"] in leader_ticker_set for t in tickers):
                print(f"  ⏭ {s['sector']} — 대장주 포함 업종, STAGE 1으로 지정")
                continue

            sector_series = []
            for t in tickers:
                try:
                    df = stock.get_market_ohlcv_by_date(start, end, t["ticker"])
                    if not df.empty:
                        sector_series.append(df["등락률"])
                except Exception:
                    continue

            if not sector_series:
                continue

            sector_avg = pd.concat(sector_series, axis=1).mean(axis=1)

            raw_5d = sector_avg.tail(5).dropna().mean()
            raw_20d = sector_avg.tail(20).dropna().mean()
            mom_5d = float(raw_5d) if not math.isnan(float(raw_5d)) else 0.0
            mom_20d = float(raw_20d) if not math.isnan(float(raw_20d)) else 0.0

            combined = pd.concat([leader_returns, sector_avg], axis=1).dropna()
            corr = 0.0
            if len(combined) >= 5:
                c = combined.iloc[:, 0].corr(combined.iloc[:, 1])
                if isinstance(c, float) and not math.isnan(c):
                    corr = round(c, 3)

            results.append({
                **s,
                "corr_to_leader": corr,
                "momentum_5d": round(mom_5d, 2),
                "momentum_20d": round(mom_20d, 2),
                "_preview_tickers": tickers,
            })

        return sorted(results, key=lambda x: x["corr_to_leader"], reverse=True)

    except Exception as e:
        print(f"  ❌ 상관계수 랭킹 오류: {e}")
        return []


# ── 6. 스테이지 엔트리 생성 ───────────────────────────────

def build_stage_entry(framework: dict, sector_info: dict, tickers: list) -> dict:
    sector_name = sector_info.get("sector", "")
    role = framework["role"]
    ticker_names = [t["name"] for t in tickers]
    ticker_codes = [t["ticker"] for t in tickers]

    name = f"{role} — {sector_name}"
    desc = " / ".join(ticker_names[:4]) if ticker_names else sector_name
    keywords = [sector_name] + ticker_names[:4]

    change_today = sector_info.get("change", 0.0)
    mom_5d = sector_info.get("momentum_5d", 0.0)
    corr = sector_info.get("corr_to_leader", 0.0)

    basis_parts = [f"오늘 업종 등락률 {change_today:+.2f}%"]
    if mom_5d:
        basis_parts.append(f"5일 모멘텀 {mom_5d:+.1f}%")
    if corr:
        basis_parts.append(f"대장주 상관계수 {corr:.2f}")
    basis = ". ".join(basis_parts) + "."

    return {
        "name": name,
        "desc": desc,
        "basis": basis,
        "keywords": keywords,
        "tickers": ticker_codes,
        "color": framework["color"],
        "is_current": False,
        "concept": framework["concept"],
        "_sector_no": sector_info.get("no"),
        "_corr_to_leader": corr,
        "_momentum_5d": mom_5d,
    }


# ── 메인 빌더 ─────────────────────────────────────────────

class StageContextBuilder:
    def __init__(self, context_path: Path, interval_hours: int = REBUILD_INTERVAL_HOURS):
        self.context_path = context_path
        self.interval_hours = interval_hours

    def _needs_rebuild(self) -> bool:
        if not self.context_path.exists():
            return True
        try:
            ctx = json.loads(self.context_path.read_text(encoding="utf-8"))
            last = ctx.get("last_auto_built")
            if not last:
                return True
            dt = datetime.strptime(last, "%Y-%m-%d %H:%M:%S")
            return (datetime.now() - dt).total_seconds() > self.interval_hours * 3600
        except Exception:
            return True

    def build(self, force: bool = False) -> bool:
        if not force and not self._needs_rebuild():
            elapsed = self._elapsed_hours()
            print(f"  ⏭ 컨텍스트 빌드 스킵 (마지막 빌드 {elapsed:.1f}시간 전)")
            return False

        print("🏗 스테이지 컨텍스트 자동 빌드 시작...")

        # ── STAGE 1: 대장주 탐지 ──
        print(f"  🔍 KOSPI 시총 상위 {LEADER_TOP_N}종목 기준 대장주 탐지 중...")
        leaders, concentration = detect_leaders()
        leader_ticker_set = {l["ticker"] for l in leaders}
        leader_names = [l["name"] for l in leaders]
        print(f"  ✅ 대장주 {len(leaders)}종목 (집중도 {concentration:.1f}%): {', '.join(leader_names)}")

        # ── 대장주 수익률 시계열 ──
        print("  📈 대장주 수익률 시계열 계산 중...")
        leader_returns = get_leader_returns(leaders)
        if leader_returns.empty:
            print("  ❌ 대장주 수익률 계산 실패 — 빌드 중단")
            return False

        # ── 네이버 업종 리스트 ──
        print("  🌐 네이버 업종 데이터 수집 중...")
        sectors = fetch_sector_list()
        if not sectors:
            print("  ❌ 업종 데이터 수집 실패 — 빌드 중단")
            return False

        # ── STAGE 2~5: 상관계수 기반 랭킹 ──
        print(f"  📊 상위 {PRE_FILTER_TOP_N}개 업종 상관계수 계산 중...")
        ranked = rank_sectors_by_correlation(sectors, leader_returns, leader_ticker_set)
        if len(ranked) < 4:
            print(f"  ❌ 유효 업종 부족 ({len(ranked)}개) — 빌드 중단")
            return False

        # ── 스테이지 조합 ──
        stages = {}

        # STAGE 1: 대장주
        leader_names_str = " / ".join(leader_names[:5])
        stages["STAGE_1_SPARK"] = {
            "name": f"대장주 — {leader_names_str}",
            "desc": leader_names_str,
            "basis": f"KOSPI 시총 집중도 상위 종목군 (합산 {concentration:.1f}%). {len(leaders)}개 종목 자동 선정.",
            "keywords": leader_names,
            "tickers": list(leader_ticker_set),
            "color": STAGE_FRAMEWORK[0]["color"],
            "is_current": False,
            "concept": STAGE_FRAMEWORK[0]["concept"],
            "_concentration_pct": concentration,
            "_leaders": leaders,
        }

        # STAGE 2~5: 상관계수 순 배정
        for i, framework in enumerate(STAGE_FRAMEWORK[1:]):
            if i >= len(ranked):
                break
            sector_info = ranked[i]
            tickers = sector_info.get("_preview_tickers") or []
            if not tickers and sector_info.get("no"):
                tickers = fetch_sector_tickers(sector_info["no"], top_n=5)
                time.sleep(0.2)

            entry = build_stage_entry(framework, sector_info, tickers)
            print(
                f"  [{i+2}/5] {framework['role']} ← {sector_info['sector']} "
                f"(상관계수 {sector_info['corr_to_leader']:.2f}, "
                f"5일모멘텀 {sector_info['momentum_5d']:+.1f}%)"
            )
            stages[framework["id"]] = entry

        # ── 기존 컨텍스트 보존값 ──
        existing = {}
        if self.context_path.exists():
            try:
                existing = json.loads(self.context_path.read_text(encoding="utf-8"))
            except Exception:
                pass

        context = {
            "last_auto_built": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_updated": existing.get("last_updated", ""),
            "market_mood": existing.get("market_mood", "자동 생성"),
            "rotation_score": existing.get("rotation_score", 0),
            "strategy": existing.get("strategy", "HOLD"),
            "leaders": leaders,
            "leader_concentration_pct": concentration,
            "stages": stages,
        }

        self.context_path.parent.mkdir(parents=True, exist_ok=True)
        self.context_path.write_text(
            json.dumps(context, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        print(f"  ✅ market_context.json 자동 빌드 완료 ({len(stages)}개 스테이지)")
        return True

    def _elapsed_hours(self) -> float:
        try:
            ctx = json.loads(self.context_path.read_text(encoding="utf-8"))
            last = ctx.get("last_auto_built", "")
            dt = datetime.strptime(last, "%Y-%m-%d %H:%M:%S")
            return (datetime.now() - dt).total_seconds() / 3600
        except Exception:
            return 999.0


if __name__ == "__main__":
    from src.utils.paths import DATA_DIR
    path = DATA_DIR / "monitoring" / "market_context.json"
    StageContextBuilder(path).build(force=True)
