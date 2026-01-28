import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from src.utils.human_language_rewriter import HumanLanguageRewriter

class JudgmentContinuityEngine:
    """
    Step 91-92: Human Judgment Continuity & Narrative Drift Engine.
    Analyzes snapshot history to determine topic persistence and interpretation shifts.
    """

    INTERPRETATION_AXES = [
        "Risk Exposure",
        "Structural Constraint",
        "Capital Reallocation",
        "Policy / Schedule Lock",
        "Supply Bottleneck"
    ]

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.memory_dir = base_dir / "data" / "snapshots" / "memory"
        self.logger = logging.getLogger("JudgmentContinuityEngine")

    def analyze_continuity(self, today_topic: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for Step 91-92 logic.
        """
        if not today_topic:
            return {}

        today_title = today_topic.get("title", "").strip().lower()
        today_date = today_topic.get("date", datetime.utcnow().strftime("%Y-%m-%d"))
        
        # 1. Load History (Last 30 days)
        history = self._load_history(today_date, lookback=30)
        
        # 2. Match Topics (Simple title match for continuity)
        topic_history = [s for s in history if s.get("top_signal", {}).get("title", "").strip().lower() == today_title]
        
        # 3. Judgment Stack (Step 91)
        stack = self._compute_judgment_stack(today_topic, topic_history, today_date)
        
        # 4. Narrative Drift (Step 92)
        axis = self._classify_axis(today_topic)
        drift = self._detect_drift(today_topic, topic_history, axis)
        
        return {
            "judgment_stack": stack,
            "interpretation_axis": axis,
            "narrative_drift": drift
        }

    def _load_history(self, today_date: str, lookback: int = 30) -> List[Dict[str, Any]]:
        history = []
        today_dt = datetime.strptime(today_date, "%Y-%m-%d")
        
        for i in range(1, lookback + 1):
            prev_date = (today_dt - timedelta(days=i)).strftime("%Y-%m-%d")
            file_path = self.memory_dir / f"{prev_date}.json"
            if file_path.exists():
                try:
                    data = json.loads(file_path.read_text(encoding="utf-8"))
                    history.append(data)
                except Exception:
                    pass
        return history

    def _compute_judgment_stack(self, today: Dict[str, Any], history: List[Dict[str, Any]], today_date: str) -> Dict[str, Any]:
        if not history:
            return {
                "first_detected": today_date,
                "days_active": 1,
                "recurrence": False,
                "judgment_state": "NEW",
                "last_state_change": today_date
            }
        
        first_detected = history[-1].get("date", today_date)
        days_active = len(history) + 1
        
        # Determine State
        prev_intensity = history[0].get("top_signal", {}).get("intensity", "")
        curr_intensity = today.get("badges", {}).get("intensity", "")
        
        state = "SUSTAINED"
        if curr_intensity == "STRIKE" and prev_intensity != "STRIKE":
            state = "ESCALATING"
        elif days_active >= 3:
            state = "SUSTAINED"
        
        # Simplified Korean label for Dashboard
        state_labels = {
            "NEW": "NEW",
            "ESCALATING": "↗ Escalating",
            "SUSTAINED": "유지",
            "DEGRADING": "↘ Degrading"
        }
        
        return {
            "first_detected": first_detected,
            "days_active": days_active,
            "recurrence": True,
            "judgment_state": state,
            "state_label": HumanLanguageRewriter.rewrite_status(state, days_active),
            "last_state_change": today_date,
            "memory_summary": self._generate_memory_summary(state, days_active)
        }

    def _generate_memory_summary(self, state: str, days: int) -> List[str]:
        """
        Step 93: Generates 2-3 short human-readable sentences for the Memory View.
        """
        if days == 1:
            return ["오늘 처음 포착된 새로운 구조적 흐름입니다.", "기존 데이터와의 연결 고리를 분석 중입니다."]
        
        sentences = []
        if state == "ESCALATING":
            sentences = [
                "이 판단은 최근 며칠 동안 반복해서 등장하며 세력이 강해지고 있습니다.",
                "어제보다 오늘 시장의 구조적 반응이 더 또렷해졌습니다.",
                "판단의 무게중심이 한층 더 실리고 있습니다."
            ]
        elif state == "SUSTAINED":
            sentences = [
                "최근 계속 관찰되고 있는 안정적인 흐름입니다.",
                "강해지지는 않았지만 꺾였다는 신호도 발견되지 않았습니다.",
                "아직 기존 판단의 유효성 안에 머물러 있습니다."
            ]
        elif state == "DEGRADING":
            sentences = [
                "오랫동안 유지되던 흐름에서 조금씩 힘이 빠지고 있습니다.",
                "구조적 압력이 정점을 지나 분산되는 신호가 포착되었습니다.",
                "기존 판단의 수정을 준비해야 하는 국면입니다."
            ]
        else:
            sentences = [
                "최근 며칠 동안 비슷한 구조가 반복해서 관찰되고 있습니다.",
                "판단의 일관성이 유지되고 있는 구간입니다."
            ]
        return sentences

    def _classify_axis(self, topic: Dict[str, Any]) -> str:
        """
        Deterministic classification into one dominant axis.
        """
        title = topic.get("title", "").lower()
        trigger = topic.get("why_now", {}).get("type", "")
        
        if "supply" in title or "chain" in title:
            return "Supply Bottleneck"
        if "policy" in title or "fed" in title or "rate" in title:
            return "Policy / Schedule Lock"
        if "risk" in title or "shocks" in title:
            return "Risk Exposure"
        if "constraint" in title or "bottleneck" in title:
            return "Structural Constraint"
        
        return "Structural Constraint" # Fallback

    def _detect_drift(self, today: Dict[str, Any], history: List[Dict[str, Any]], current_axis: str) -> Dict[str, Any]:
        if not history:
            return {"detected": False, "label": "Narrative Stable (New Topic)"}
        
        prev_top = history[0].get("top_signal", {})
        # Since history snapshots might not have interpretation_axis yet (pre-Step 92), 
        # we re-classify the previous one briefly for comparison.
        prev_axis = self._classify_axis(prev_top)
        
        drift_detected = prev_axis != current_axis
        
        return {
            "detected": drift_detected,
            "from": prev_axis,
            "to": current_axis,
            "label": f"↔ 해석 변화: {prev_axis} → {current_axis}" if drift_detected else "Narrative Stable (Recurring Structure)"
        }
