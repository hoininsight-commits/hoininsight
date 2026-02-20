from typing import List, Dict, Any, Optional

class MisinterpretationEngine:
    """
    IS-42: MISINTERPRETATION_SCENARIO_ENGINE
    Predicts how a signal might be misunderstood and assigns risk levels.
    """

    def analyze_risks(self, topic: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Predicts scenarios and assigns risk levels."""
        scenarios = self._predict_scenarios(topic)
        results = []
        for s in scenarios:
            level = self._classify_risk(s, topic)
            results.append({
                "scenario": s,
                "risk_level": level
            })
        return results

    def _predict_scenarios(self, topic: Dict[str, Any]) -> List[str]:
        """Heuristic-based scenario prediction in Korean."""
        title = topic.get("title", "")
        urgency = topic.get("urgency_score", 0)
        tickers = topic.get("bottleneck_tickers", [])

        pool = []
        # Ticker specific risk
        if tickers:
            pool.append(f"'{tickers[0]}' 종목에 대한 즉각적인 매수 추천으로 오해할 수 있음.")
        
        # Urgency/Timing risk
        if urgency >= 80:
            pool.append("지금 당장 행동하지 않으면 기회를 놓친다는 패닉 매수로 이어질 위험이 있음.")
        
        # General outcome risk
        pool.append("해당 분석 결과가 100% 보장된 수익으로 오해받을 소지가 있음.")
        pool.append("구조적 변화가 아닌 단순한 정치적/이념적 발언으로 해석될 여지가 있음.")

        return pool[:4]

    def _classify_risk(self, scenario: str, topic: Dict[str, Any]) -> str:
        """Classifies risk into 낮음, 중간, 높음."""
        if "매수" in scenario or "추천" in scenario or "수익" in scenario:
            return "높음"
        if "패닉" in scenario or "이념" in scenario:
            return "중간"
        return "낮음"
