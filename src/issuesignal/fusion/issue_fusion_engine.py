from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from pathlib import Path

class IssueFusionEngine:
    """
    (IS-86) Issue Fusion & Narrative Candidate Generator.
    Combines IssueSignal, Watchlist, Anomalies, and Schedules to propose
    multi-perspective narrative candidates.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def generate_candidates(self, issue_json: Dict[str, Any], watchlist: Dict[str, Any], statement_candidates: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Generates narrative candidates based on fusion rules.
        
        Inputs:
         - issue_json: Main Issue Signal output (IS-73~)
         - watchlist: Strategic Watchlist (IS-81/82)
         
        Returns:
         - List of candidate dictionaries.
        """
        candidates = []
        today = datetime.now().strftime("%Y-%m-%d")
        ymd_short = datetime.now().strftime("%Y%m%d")
        
        # 1. Load Auxiliary Data (Mocked for MVP as per instructions to not add collectors)
        # In a real scenario, these would be loaded from their respective stores.
        # For IS-86 MVP, we check if files exist, otherwise use safe defaults or "Mock" fusion for demo.
        schedule_data = self._load_schedule()
        anomaly_data = self._load_anomalies()
        
        # Rule 1: Schedule + Structure Fusion (PREVIEW)
        # If there is a major schedule item AND a structural issue in watchlist
        if schedule_data and watchlist.get("watchlist", []):
            top_watch = watchlist["watchlist"][0] if watchlist["watchlist"] else {}
            top_schedule = schedule_data[0] if schedule_data else {}
            
            if top_watch and top_schedule:
                candidates.append({
                    "id": f"NC-{ymd_short}-001",
                    "source_mix": ["schedule", "structure"],
                    "dominant_type": "PREVIEW",
                    "theme": f"예정된 '{top_schedule.get('event', '이벤트')}'와 {top_watch.get('name', '구조적 이슈')}의 충돌 가능성 미리보기",
                    "why_now": "일정이 다가옴에 따라 시장의 구조적 우려가 자극될 시점입니다.",
                    "confidence_level": "HIGH",
                    "promotion_hint": "DAILY_LONG",
                    "status": "CANDIDATE"
                })

        # Rule 2: Anomaly + Watchlist Fusion (SCENARIO)
        # If anomaly detected in a watchlist sector
        if anomaly_data and watchlist.get("watchlist", []):
            # Simplified logic: just take first available for demo fusion
            candidates.append({
                "id": f"NC-{ymd_short}-002",
                "source_mix": ["anomaly", "watchlist"],
                "dominant_type": "SCENARIO",
                "theme": "감지된 이상징후가 기존 관찰 리스트의 핵심 전제를 흔드는 시나리오",
                "why_now": "이상징후가 단순 노이즈가 아닌 구조적 균열의 신호일 수 있습니다.",
                "confidence_level": "MEDIUM",
                "promotion_hint": "WEEKLY_STRUCTURE",
                "status": "CANDIDATE"
            })

        # Rule 3: Single Structure Deep Dive (STRUCTURE)
        # If Watchlist has high priority item
        if watchlist.get("watchlist", []):
            item = watchlist["watchlist"][0]
            candidates.append({
                "id": f"NC-{ymd_short}-003",
                "source_mix": ["structure"],
                "dominant_type": "STRUCTURE",
                "theme": f"{item.get('name', '핵심 이슈')}의 구조적 경로 재점검",
                "why_now": "뉴스가 없을 때야말로 구조를 점검해야 할 최적의 시간입니다.",
                "confidence_level": "HIGH",
                "promotion_hint": "DAILY_SHORT",
                "status": "CANDIDATE"
            })

        # Rule 4: Statement/Document Fusion (INTENT/STRUCTURE)
        if statement_candidates:
            for sc in statement_candidates:
                candidates.append({
                    "id": f"NC-STMT-{sc['id']}",
                    "source_mix": ["statement", sc["source"]],
                    "dominant_type": "FACT",
                    "theme": f"{sc['entity']} ({sc['organization']})의 의도: {sc['why_it_matters_hint']}",
                    "why_now": f"실제 발언('{sc['content'][:50]}...')을 통해 포착된 {sc['detected_signals']} 신호입니다.",
                    "confidence_level": "HIGH",
                    "promotion_hint": "EDITORIAL_VIEW",
                    "status": "CANDIDATE",
                    "entity": sc["entity"],
                    "organization": sc["organization"],
                    "raw_text": sc["content"],
                    "detected_signals": sc["detected_signals"]
                })
        if len(candidates) < 3:
             candidates.append({
                "id": f"NC-{ymd_short}-004",
                "source_mix": ["structure", "statement"],
                "dominant_type": "STRUCTURE",
                "theme": "시장 침묵 속에서 확인해야 할 매크로 펀더멘털",
                "why_now": "변동성 축소 구간은 다음 방향성을 위한 에너지 축적 과정입니다.",
                "confidence_level": "LOW",
                "promotion_hint": "WATCH_ONLY",
                "status": "CANDIDATE"
            })
            
        return candidates

    def _load_schedule(self):
        # Placeholder: In prod, load from data/calendar/
        return [{"event": "FOMC 의사록 공개", "impact": "High"}]

    def _load_anomalies(self):
        # Placeholder: In prod, load from data/anomalies/
        return [{"metric": "Credit Spread", "status": "Widening"}]
