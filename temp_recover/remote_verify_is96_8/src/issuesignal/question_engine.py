from typing import List, Dict, Any, Optional

class AudienceQuestionEngine:
    """
    IS-41: AUDIENCE_QUESTION_ANTICIPATION_CONTROL_ENGINE
    Predicts and controls audience post-signal questions.
    """

    STRATEGY_MAP = {
        "ANSWER_NOW": "즉답",
        "HOLD": "보고 보류",
        "SILENT": "침묵 유지",
        "DEFER": "브릿지"
    }

    def process_signal(self, topic: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Main entry point for question anticipation and control.
        """
        questions = self._predict_questions(topic)
        strategies = []
        for q in questions:
            strategy = self._classify_and_strategize(q, topic)
            strategies.append(strategy)
        return strategies

    def _predict_questions(self, topic: Dict[str, Any]) -> List[str]:
        """Predicts 3-5 audience questions based on topic type and urgency."""
        title = topic.get("title", "")
        urgency = topic.get("urgency_score", 0)
        
        pool = []
        if "금리" in title or "정책" in title:
            pool = [
                "다음 금리 결정 시점은 언제인가?",
                "이번 발표가 시장에 즉각적인 영향을 주는가?",
                "반대 의견을 낸 위원은 누구인가?",
                "금리 인하 가능성은 완전히 사라졌는가?"
            ]
        elif "실적" in title:
            pool = [
                "EPS 서프라이즈의 지속 가능성은?",
                "가이던스 하향 조정의 진짜 이유는?",
                "경쟁사 대비 점유율 하락은 사실인가?",
                "지금 진입해도 늦지 않았는가?"
            ]
        else:
            pool = [
                "이 현상의 실질적인 수혜 티커는 무엇인가?",
                "단기 변동성인가 아니면 구조적 변화인가?",
                "지금 당장 대응해야 하는가?",
                "데이터가 반전될 가능성은 없는가?"
            ]

        # Pick 3 based on urgency (higher urgency -> more aggressive questions)
        if urgency >= 80:
            return pool[:4]
        return pool[:3]

    def _classify_and_strategize(self, q_text: str, topic: Dict[str, Any]) -> Dict[str, Any]:
        """Classifies the question and generates the controlled response strategy."""
        
        # Classification Logic
        classification = "ANSWER_NOW"
        reason = "일반적인 정보 확인 질문"
        
        if "티커" in q_text or "기업" in q_text:
            classification = "SILENT"
            reason = "미공개 민감 정보 추출 시도"
        elif "늦지 않았" in q_text or "진입" in q_text:
            classification = "HOLD"
            reason = "감정적/포모(FOMO)성 질문"
        elif "다음" in q_text or "지속" in q_text:
            classification = "DEFER"
            reason = "구조적 확장성 질문"
        
        # Strategy Generation (Applying IS-39 Voice Rules: Declarative, Certain)
        response = ""
        if classification == "ANSWER_NOW":
            response = "데이터가 가리키는 방향은 명확하다. 관찰된 수치만이 유일한 진실이다."
        elif classification == "HOLD":
            response = "추가 데이터 확인이 필요하다. 지금은 자본의 이동 방향을 지켜봐야 한다."
        elif classification == "DEFER":
            response = "다음 발화에서 이 지점을 다룬다. 구조적 연결 고리는 이미 확보됐다."
        elif classification == "SILENT":
            response = "(무대응)"

        return {
            "question": q_text,
            "classification": self.STRATEGY_MAP.get(classification, "미분류"),
            "strategy": response,
            "internal_reason": reason
        }
