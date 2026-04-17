# src/agents/consensus_collector.py

import os
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path


class ConsensusCollector:
    """
    경제지표 예상치 vs 실제치 수집기
    Finnhub Economic Calendar API 사용 (무료)
    """

    FINNHUB_URL = "https://finnhub.io/api/v1/calendar/economic"

    # 우리가 관심 있는 고임팩트 지표만 필터링
    TARGET_EVENTS = [
        "CPI", "Consumer Price Index",
        "PPI", "Producer Price Index",
        "NFP", "Nonfarm Payroll", "Non-Farm",
        "GDP",
        "FOMC", "Fed", "Interest Rate",
        "PCE",
        "Unemployment",
        "Retail Sales",
        "PMI",
    ]

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.api_key = os.environ.get("FINNHUB_API_KEY", "")

    def collect(self) -> dict:
        """오늘 ~ 7일 후 예정 지표 + 최근 3일 발표 지표 수집"""
        print("📅 컨센서스 레이어 수집 시작...")

        today = datetime.now()
        date_from = (today - timedelta(days=3)).strftime("%Y-%m-%d")
        date_to = (today + timedelta(days=7)).strftime("%Y-%m-%d")

        if not self.api_key:
            print("  ⚠️ FINNHUB_API_KEY 없음 — 컨센서스 수집 스킵")
            return self._empty_result()

        try:
            response = requests.get(
                self.FINNHUB_URL,
                params={
                    "from": date_from,
                    "to": date_to,
                    "token": self.api_key
                },
                timeout=10
            )
            response.raise_for_status()
            raw = response.json()
        except Exception as e:
            print(f"  ❌ Finnhub API 호출 실패: {e}")
            return self._empty_result()

        events = raw.get("economicCalendar", [])

        # 고임팩트 + 미국 지표만 필터
        filtered = self._filter_events(events)

        # 서프라이즈 스코어 계산
        processed = self._calc_surprise(filtered)

        result = {
            "date": today.strftime("%Y-%m-%d"),
            "collected_at": datetime.now().isoformat(),
            "period": {"from": date_from, "to": date_to},
            "events": processed,
            "top_surprise": self._get_top_surprise(processed)
        }

        output_path = self.output_dir / "consensus.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"  ✅ consensus.json 저장 완료 ({len(processed)}개 이벤트)")
        return result

    def _filter_events(self, events: list) -> list:
        """고임팩트 미국 지표만 필터링"""
        filtered = []
        for e in events:
            country = e.get("country", "").upper()
            event_name = e.get("event", "")
            impact = e.get("impact", "")

            # 미국 + 고임팩트만
            if country != "US":
                continue
            if impact not in ["high", "3"]:
                continue

            # 관심 지표 키워드 매칭
            if any(kw.lower() in event_name.lower() for kw in self.TARGET_EVENTS):
                filtered.append(e)

        return filtered

    def _calc_surprise(self, events: list) -> list:
        """서프라이즈 스코어 계산 — 핵심 공식"""
        processed = []
        for e in events:
            actual = e.get("actual")
            estimate = e.get("estimate")

            surprise_score = None
            surprise_label = "PENDING"  # 아직 발표 안 됨

            if actual is not None and estimate is not None:
                try:
                    a = float(actual)
                    est = float(estimate)
                    if est != 0:
                        # 서프라이즈 = (실제 - 예상) / |예상| * 100
                        surprise_score = round((a - est) / abs(est) * 100, 2)

                        if abs(surprise_score) >= 20:
                            surprise_label = "SHOCK"      # 강한 충격
                        elif abs(surprise_score) >= 10:
                            surprise_label = "SURPRISE"   # 유의미한 괴리
                        elif abs(surprise_score) >= 5:
                            surprise_label = "MISS"       # 소폭 괴리
                        else:
                            surprise_label = "IN_LINE"    # 예상치 부합
                    else:
                        surprise_label = "NO_ESTIMATE"
                except (ValueError, TypeError):
                    surprise_label = "PARSE_ERROR"

            processed.append({
                "event": e.get("event"),
                "time": e.get("time"),
                "country": e.get("country"),
                "actual": actual,
                "estimate": estimate,
                "prev": e.get("prev"),
                "impact": e.get("impact"),
                "surprise_score": surprise_score,
                "surprise_label": surprise_label,
            })

        # 서프라이즈 강도 순으로 정렬
        processed.sort(
            key=lambda x: abs(x["surprise_score"]) if x["surprise_score"] else 0,
            reverse=True
        )
        return processed

    def _get_top_surprise(self, events: list):
        """가장 강한 서프라이즈 이벤트 1개 반환 — DETECTOR에 전달용"""
        for e in events:
            if e["surprise_label"] in ["SHOCK", "SURPRISE"]:
                return e
        return None

    def _empty_result(self) -> dict:
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "collected_at": datetime.now().isoformat(),
            "events": [],
            "top_surprise": None
        }
