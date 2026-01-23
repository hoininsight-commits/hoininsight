from __future__ import annotations
from typing import Any, Dict
from .types import Candidate, NumberItem

class Validator:
    def attach_numbers(self, candidate: Candidate, snapshot: Dict[str, Any]) -> Candidate:
        # snapshot 구조에 맞게 실제 숫자 0~3개 추출 로직을 안티그래피티가 연결
        numbers: list[NumberItem] = []

        # 예시: 지수 변동률
        v = self._try_get(snapshot, ["index", "spx", "pct_change"])
        if v is not None:
            numbers.append(NumberItem(label="S&P500 변화율", value=v, unit="%"))

        # 예시: 10Y 금리 변화
        v = self._try_get(snapshot, ["rates", "us10y", "bps_change"])
        if v is not None:
            numbers.append(NumberItem(label="미국 10년물 금리 변화", value=v, unit="bp"))

        # 최대 3개
        candidate.numbers = numbers[:3]

        # confidence는 "말할 가치" 기반이므로 numbers가 있으면 상향 정도만
        if len(candidate.numbers) >= 2:
            candidate.confidence = "MEDIUM"
        else:
            candidate.confidence = "LOW"

        return candidate

    def _try_get(self, obj: Dict[str, Any], path: list[str]):
        cur: Any = obj
        for p in path:
            if not isinstance(cur, dict) or p not in cur:
                return None
            cur = cur[p]
        return cur
