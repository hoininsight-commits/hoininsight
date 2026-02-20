import re
from typing import Dict, Any

class HumanLanguageRewriter:
    """
    Step 93: Human Language Rewrite Layer
    Translates technical engine terms into natural, intuitive Korean phrases.
    Focuses on reducing cognitive load for the operator.
    """

    TERM_MAPPING = {
        "NEW": "처음 감지된 새로운 흐름",
        "ESCALATING": "점점 힘이 실리는 중",
        "SUSTAINED": "같은 흐름이 유지 중",
        "DEGRADING": "힘이 빠지기 시작",
        "Narrative Drift": "보던 관점이 조금 달라짐",
        "Structural Persistence": "같은 구조가 반복됨",
        "Risk Exposure": "리스크 노출 국면",
        "Structural Constraint": "구조적 제약 발생",
        "Capital Reallocation": "자본 재배치 움직임",
        "Policy / Schedule Lock": "정책 및 일정 확정",
        "Supply Bottleneck": "공급망 병목 현상"
    }

    FORBIDDEN_WORDS = [r"매수", r"수익", r"투자", r"추천", r"가격", r"폭등", r"폭락"]

    @classmethod
    def rewrite_status(cls, technical_status: str, days: int) -> str:
        """
        Rewrites strings like 'ESCALATING 2일차' into human phrases.
        """
        base = technical_status.split()[0] if technical_status else "NEW"
        human_phrase = cls.TERM_MAPPING.get(base, "새로운 국면 진입")
        
        if days > 1:
            if base == "SUSTAINED":
                return f"며칠째 이어지는 흐름 / {days}일째 유지 중"
            elif base == "ESCALATING":
                return f"반복 관찰 중 / 오늘 더 강해졌습니다 ({days}일째)"
            else:
                return f"{human_phrase} ({days}일째)"
        
        return human_phrase

    @classmethod
    def rewrite_drift(cls, drift_data: Dict[str, Any]) -> str:
        """
        Rewrites drift labels into more natural language.
        """
        if not drift_data.get("detected"):
            return "안정적인 구조가 반복되고 있습니다."
        
        prev = cls.TERM_MAPPING.get(drift_data.get("from"), "이전 관점")
        curr = cls.TERM_MAPPING.get(drift_data.get("to"), "현재 관점")
        return f"분석 관점이 조금 달라졌습니다: {prev} → {curr}"

    @classmethod
    def sanitize(cls, text: str) -> str:
        """
        Ensures no forbidden or sensationalist words are present.
        """
        sanitized = text
        for pattern in cls.FORBIDDEN_WORDS:
            sanitized = re.sub(pattern, "[검열됨]", sanitized)
        return sanitized

if __name__ == "__main__":
    # Test
    print(HumanLanguageRewriter.rewrite_status("ESCALATING 2일차", 2))
    print(HumanLanguageRewriter.rewrite_drift({"detected": True, "from": "Risk Exposure", "to": "Structural Constraint"}))
