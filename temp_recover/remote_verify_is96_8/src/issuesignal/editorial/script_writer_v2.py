from typing import Dict, List, Any, Optional

class ScriptWriterV2:
    """
    (IS-84) EconomicHunter Script Writer v2.
    Generates Tone-Driven scripts (Long-form, Shorts, Text Card)
    based on IS-83 Tone/Mode metadata.
    """
    
    def __init__(self, base_dir=None):
        self.base_dir = base_dir
        
    def generate_package(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates content package (Scripts V2) for a candidate.
        
        Input candidate keys expected:
         - tone_type (WARNING, PREVIEW, STRUCTURAL, SCENARIO)
         - script_mode (ALERT, HEADS_UP, EXPLANATION, WHAT_IF)
         - editorial_title (or title)
         - opening_sentence (IS-73) - Optional
         - why_now (or reason)
         - evidence_bundle (optional)
        """
        tone = candidate.get("tone_type", "STRUCTURAL")
        mode = candidate.get("script_mode", "EXPLANATION")
        title = candidate.get("editorial_title") or candidate.get("title", "Untitled Topic")
        
        # 1. Opening Composite (IS-73 + Tone Rule)
        base_opening = candidate.get("opening_sentence", "").strip()
        tone_opening = self._get_tone_opening(tone)
        
        full_opening = base_opening
        if tone_opening:
            if full_opening:
                full_opening += "\n" + tone_opening
            else:
                full_opening = tone_opening

        # 2. 5-Step Structure Generation
        steps = self._build_5_steps(candidate, tone, mode, full_opening)
        
        # 3. Assemble Long Form
        long_form = self._assemble_long_form(steps, mode)
        
        # 4. Assemble Shorts (3 variations)
        shorts = self._assemble_shorts(steps, mode)
        
        # 5. Text Card
        text_card = self._assemble_text_card(steps, mode)
        
        # 6. Disclaimer
        disclaimer = "본 내용은 확정된 투자 판단이 아닌 구조적 관찰입니다."
        
        return {
            "version": "v2",
            "tone_type": tone,
            "script_mode": mode,
            "long_form_script": long_form,
            "shorts_scripts": shorts,
            "text_card": text_card,
            "disclaimer_line": disclaimer
        }

    def _get_tone_opening(self, tone: str) -> str:
        if tone == "WARNING":
            return "지금 시장에서 가장 위험한 신호는 이것입니다."
        elif tone == "PREVIEW":
            return "이번 주 시장에서 반드시 체크해야 할 일정은 이것입니다."
        elif tone == "STRUCTURAL":
            return "지금 시장에서는 조용하지만 중요한 변화가 일어나고 있습니다."
        elif tone == "SCENARIO":
            return "만약 이 흐름이 이어진다면, 시장은 전혀 다른 방향으로 움직일 수 있습니다."
        return ""

    def _build_5_steps(self, c: Dict, tone: str, mode: str, opening: str) -> Dict[str, str]:
        """Generates content for each of the 5 steps."""
        # This is a template-based generator. 
        # In a real system, this might use LLM or sophisticated slot filling.
        # For IS-84 MVP, we use robust templates using available metadata.
        
        reason = c.get("reason") or c.get("why_now", "")
        category = c.get("category", "")
        
        # 1. Definition (Opening)
        step1 = opening
        
        # 2. Surface View
        step2 = f"대부분은 이 이슈를 '{category}' 관점에서 단순히 바라봅니다."
        
        # 3. Misconception
        step3 = "하지만 진짜 중요한 포인트는 겉으로 보이는 뉴스 헤드라인이 아닙니다."
        
        # 4. Structural Force (Core logic based on Tone)
        step4 = ""
        if tone == "WARNING":
            step4 = f"구조적으로 볼 때, '{reason}'라는 리스크가 시장의 약한 고리를 건드리고 있기 때문입니다."
        elif tone == "PREVIEW":
            step4 = f"이 일정은 단순한 이벤트가 아니라, '{reason}'라는 변화를 확인하는 중요한 분기점이기 때문입니다."
        elif tone == "SCENARIO":
            step4 = f"조건은 명확합니다. '{reason}' 현상이 심화되면 우리가 알던 공식은 깨지게 됩니다."
        else: # STRUCTURAL
            step4 = f"이것은 일시적 현상이 아니라, '{reason}'에 의해 자본의 흐름이 근본적으로 바뀌고 있다는 증거입니다."
            
        # 5. Conclusion (Actionable Check)
        step5 = "따라서 지금 우리는 가격이 아니라, 이 구조적 변화가 어디까지 이어질지 냉정하게 지켜봐야 합니다."
        
        return {
            "1_define": step1,
            "2_surface": step2,
            "3_misconception": step3,
            "4_structure": step4,
            "5_conclusion": step5
        }

    def _assemble_long_form(self, steps: Dict, mode: str) -> str:
        # Simple concatenation with paragraph breaks
        return f"""{steps['1_define']}

{steps['2_surface']}
{steps['3_misconception']}

{steps['4_structure']}

{steps['5_conclusion']}"""

    def _assemble_shorts(self, steps: Dict, mode: str) -> List[str]:
        # Generate 3 variations
        s1 = f"{steps['1_define']} {steps['5_conclusion']}" # Hook + Action
        s2 = f"{steps['3_misconception']} 사실은 {steps['4_structure']}" # Insight focus
        s3 = f"{steps['1_define']} 왜냐하면 {steps['4_structure']}" # Logic focus
        return [s1, s2, s3]
        
    def _assemble_text_card(self, steps: Dict, mode: str) -> str:
        return f"""[KEY POINT]
{steps['1_define']}

[STRUCTURE]
{steps['4_structure']}

[CHECK]
{steps['5_conclusion']}"""
