from typing import Dict, Any, Optional

class UrgencyAmplifierEngine:
    """
    (IS-85) Urgency Amplifier Layer.
    Adds explicit time-pressure and "Why-Now" urgency to the narrative.
    """
    def __init__(self, base_dir=None):
        self.base_dir = base_dir

    def generate(self, candidate: Dict[str, Any], tone: str = "WARNING") -> str:
        """
        Generates an urgency sentence based on content type and tone.
        
        Input:
         - candidate (Dict): Must contain 'content_type'.
         - tone (str): WARNING, ALERT, Heads-up (defaulting to Warning if unknown).
         
        Output:
         - A string sentence.
        """
        content_type = candidate.get("content_type", "FACT")
        
        # Base Templates based on Content Type
        if content_type == "FACT":
            return "이 변화는 이미 수치로 확인됐고, 시장은 지금 반응 단계에 들어갔습니다."
            
        elif content_type == "STRUCTURE":
            return "이 구조는 아직 뉴스가 아니지만, 시장은 항상 결과보다 먼저 움직입니다."
            
        elif content_type == "PREVIEW":
            return "이 일정은 결과가 나오기 전에 포지션이 갈리는 구간입니다."
            
        elif content_type == "SCENARIO":
            return "지금은 방향이 정해지기 전 마지막 관찰 구간입니다."
            
        # Fallback
        return "지금이 아니면 의미가 줄어드는 시점입니다."
