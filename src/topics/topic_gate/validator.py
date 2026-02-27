from __future__ import annotations
from typing import Any, Dict
from .types import Candidate, NumberItem

class Validator:
    def attach_numbers(self, candidate: Candidate, snapshot: Dict[str, Any], events: list[Any] | None = None) -> Candidate:
        # snapshot 혹은 events로부터 실제 숫자 0~3개 추출
        numbers: list[NumberItem] = []
        events = events or []
        
        # 1) Snapshot 기반 기존 로직
        datasets = snapshot.get("datasets", [])
        def get_snap_val(key_fragment):
            for d in datasets:
                if key_fragment in d.get("dataset_id", "") and d.get("status_today") == "OK":
                   return "Check Chart"
            return None

        if "index" in candidate.category or "rotation" in candidate.category:
             if get_snap_val("index_spx"):
                 numbers.append(NumberItem(label="S&P500 Status", value="Active", unit=""))
         
        if "macro" in candidate.category or "policy" in candidate.category:
             if get_snap_val("rates_us10y"):
                 numbers.append(NumberItem(label="US 10Y Rate", value="Active", unit=""))

        # 2) Event 기반 신규 로직 (evidence 추출)
        for ref in candidate.evidence_refs:
            if ref.startswith("events:"):
                parts = ref.split(":")
                if len(parts) >= 3:
                    e_type, e_id = parts[1], parts[2]
                    # Find matching event
                    target_ev = next((e for e in events if getattr(e, "event_id", "") == e_id), None)
                    if target_ev:
                        # Extract first evidence metric
                        try:
                            # Support both object and dict (for compatibility)
                            if hasattr(target_ev, "evidence") and target_ev.evidence:
                                evid = target_ev.evidence[0]
                                numbers.append(NumberItem(
                                    label=evid.label,
                                    value=str(evid.value),
                                    unit=evid.unit
                                ))
                            elif isinstance(target_ev, dict) and target_ev.get("evidence"):
                                evid = target_ev["evidence"][0]
                                numbers.append(NumberItem(
                                    label=evid.get("label", "Value"),
                                    value=str(evid.get("value")),
                                    unit=evid.get("unit", "")
                                ))
                        except (IndexError, AttributeError, KeyError):
                            pass

        # 최대 3개
        candidate.numbers = numbers[:3]
        
        # confidence는 "말할 가치" 기반이므로 numbers가 있으면 상향 정도만
        if len(candidate.numbers) >= 2:
            candidate.confidence = "MEDIUM"
        elif len(candidate.numbers) >= 1:
            candidate.confidence = "LOW"
        else:
            candidate.confidence = "UNCERTAIN"
        
        return candidate

    def _try_get(self, obj: Dict[str, Any], path: list[str]):
        cur: Any = obj
        for p in path:
            if not isinstance(cur, dict) or p not in cur:
                return None
            cur = cur[p]
        return cur
