from typing import Dict, Any, Tuple

class OutputDecider:
    """
    IS-34: OUTPUT_DECIDER
    Determines output format and provides editorial reasons in Korean.
    """

    FORMAT_MAP = [
        (90, "대형 영상 (LONG FORM)"),
        (70, "숏츠 (SHORT FORM)"),
        (50, "텍스트 카드 (TEXT ONLY)"),
        (0, "침묵 (SILENT)")
    ]

    def decide(self, urgency_score: int, too_late_reason: str = None) -> Tuple[str, str]:
        """
        Returns (format_ko, reason_ko).
        """
        if too_late_reason:
            return "침묵", f"이미 반영됨으로 침묵: {too_late_reason}"
            
        output_format = "침묵"
        for threshold, name in self.FORMAT_MAP:
            if urgency_score >= threshold:
                output_format = name
                break
        
        # Format reason based on score
        reason = "분석 보유 중"
        if urgency_score >= 90:
            reason = "시간적 압박과 자본 영향력이 매우 높아 대형 기획 영상 적합"
        elif urgency_score >= 70:
            reason = "빠른 전파가 필요한 핵심 정보로 숏츠 브리핑 적합"
        elif urgency_score >= 50:
            reason = "기록 및 공유가 필요한 데이터로 텍스트 카드 발행"
        else:
            reason = "발화 압력이 낮아 내부 데이터로만 유지"
            
        return output_format, reason
