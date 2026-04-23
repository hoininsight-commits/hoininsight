
import json
from src.core.gemini_client import GeminiClient

class WhyGenerator:
    """[NEW] Why Hypothesis Layer: 증거 기반 시장 분석 가설 생성기"""

    def __init__(self):
        self.gemini = GeminiClient()

    def generate_hypothesis(self, evidence_bundle: dict) -> dict:
        system_prompt = """You are a macro market analyst.

 1. Only use the provided data.
 2. Do NOT use external knowledge.
 3. Do NOT assume unknown causes.
 4. Do NOT state definitive causes.
 5. Provide the most plausible explanation based on evidence.
 6. Mention contradictions if any.
 7. Understand Korean Market Speak & Slang: Recognize that terms like '삼전' (Samsung Electronics), '닉스' (SK Hynix), '국장' (KR Market), '미장' (US Market), and '전차' (Samsung Electronics + Hyundai Motors) are valid entities. Analyze them contextually within the narrative cycle."""

        user_prompt = f"""Below is market evidence.

[AXIS]
{evidence_bundle['axis']}

[MARKET REACTION]
{json.dumps(evidence_bundle['market_reaction'], ensure_ascii=False)}

[EVENTS]
{json.dumps(evidence_bundle['related_events'], ensure_ascii=False)}

[EVENT-MARKET LINK]
{json.dumps(evidence_bundle.get('event_market_link', []), ensure_ascii=False)}

[SUPPORTING SIGNALS]
{json.dumps(evidence_bundle['supporting_assets'], ensure_ascii=False)}

[CONTRADICTIONS]
{json.dumps(evidence_bundle['contradictions'], ensure_ascii=False)}

Task:

1. Identify the most plausible reason for the market movement.
2. Explain the mechanism (cause → effect chain).
3. Do NOT assume certainty.
4. If no supporting event exists, explicitly state that the cause cannot be determined from the data.
5. Use the event_market_link as the primary basis for constructing the mechanism.

Output format:

- Why Hypothesis:
- Mechanism:
- Confidence: (High / Medium / Low)
- Evidence Links: (List of event_market_link used)"""

        # [REPLAY FALLBACK] Quota hit 혹은 오류 시 검증 중단을 막기 위한 Mock 응답 (LLM 호출 불가 상황 대비)
        try:
            # call_controlled는 Control Layer가 적용된 텍스트 호출 엔진임 (v1.3)
            # system_prompt를 user_prompt 앞에 붙여서 전달 (call_controlled는 단일 prompt 인자 선호)
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            res = self.gemini.call_controlled(full_prompt, agent="WHY_GENERATOR", tier=3)
            
            if not res:
                return None
                
            return self._parse_response(res)
        except Exception as e:
            print(f"  ⚠️ WhyGenerator Error: {e}")
            return None

    def _parse_response(self, text: str) -> dict:
        # [DEBUG] 원문 로그 저장
        try:
            from pathlib import Path
            Path("data/debug/last_why_raw.txt").write_text(text, encoding='utf-8')
        except: pass

        lines = text.strip().split('\n')
        result = {
            "why_hypothesis": "Unknown",
            "mechanism": "Unknown",
            "confidence": "Low"
        }
        
        current_key = None
        for line in lines:
            clean_line = line.strip().replace("**", "").replace("__", "")
            
            # Robust matching for Why Hypothesis
            if any(clean_line.lower().startswith(p) for p in ["- why hypothesis:", "why hypothesis:", "1. why hypothesis:"]):
                # Remove prefix
                val = clean_line
                for p in ["- why hypothesis:", "why hypothesis:", "1. why hypothesis:"]:
                    if val.lower().startswith(p):
                        val = val[len(p):].strip()
                        break
                result["why_hypothesis"] = val
                current_key = "why_hypothesis"
                
            # Robust matching for Mechanism
            elif any(clean_line.lower().startswith(p) for p in ["- mechanism:", "mechanism:", "2. mechanism:"]):
                val = clean_line
                for p in ["- mechanism:", "mechanism:", "2. mechanism:"]:
                    if val.lower().startswith(p):
                        val = val[len(p):].strip()
                        break
                result["mechanism"] = val
                current_key = "mechanism"
                
            # Robust matching for Confidence
            elif any(clean_line.lower().startswith(p) for p in ["- confidence:", "confidence:", "3. confidence:"]):
                val = clean_line
                for p in ["- confidence:", "confidence:", "3. confidence:"]:
                    if val.lower().startswith(p):
                        val = val[len(p):].strip().replace("(", "").replace(")", "")
                        break
                result["confidence"] = val
                current_key = "confidence"
                
            elif current_key and clean_line and not any(clean_line.lower().startswith(p) for p in ["-", "1.", "2.", "3."]):
                result[current_key] += " " + clean_line
                
        return result

    def _mock_response(self) -> dict:
        return {
            "why_hypothesis": "Insufficient data to form a definitive hypothesis.",
            "mechanism": "The market reaction matches the detected axis, but causal events are not clearly linked in the evidence bundle.",
            "confidence": "Low"
        }
