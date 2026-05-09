
import json
import re
from typing import Dict, List, Optional

class ScriptQualityGate:
    """[TASK #091] SCRIPT QUALITY GATE
    생성된 스크립트의 품질을 5개 항목으로 평가하고 PASS/HOLD/DROP 결정
    """
    
    def __init__(self):
        from src.core.gemini_client import GeminiClient
        self.gemini = GeminiClient()
        
    def evaluate(self, content: Dict) -> Dict:
        """스크립트 평가 및 최종 상태 결정 (Dual-Stage 적용)"""
        script = content.get("script", "")
        
        # [STAGE 1] Deterministic Evaluation (필수 구조 체크)
        det_report = self._evaluate_deterministically(content)
        
        # [STAGE 2] Gemini Evaluation (TIER 3 - 선택적 품질 평가)
        prompt = self._build_evaluation_prompt(content)
        gemini_eval = {}
        try:
            # TIER 3 호출 (실패 시 즉각 fallback)
            res = self.gemini.call_json_controlled(prompt, agent="QUALITY_GATE", tier=3)
            if res:
                gemini_eval = res
            else:
                print("  ⚠️ Quality Gate Stage 2 (Gemini) 응답 없음. Deterministic 점수 사용.")
        except Exception as e:
            print(f"  ⚠️ Quality Gate Stage 2 (Gemini) 실패: {e}. Deterministic 점수 사용.")

        # 점수 병합
        report = {
            "hook_score": gemini_eval.get("hook_score", det_report["hook_score"]),
            "why_now_score": gemini_eval.get("why_now_score", det_report["why_now_score"]),
            "scenario_score": gemini_eval.get("scenario_score", det_report["scenario_score"]),
            "theme_score": gemini_eval.get("theme_score", det_report["theme_score"]),
            "action_score": gemini_eval.get("action_score", det_report["action_score"]),
        }
        
        total_score = sum(report.values()) / len(report)
        report["total_score"] = round(total_score, 1)
        
        # 최종 상태 결정
        status = "PASS"
        if total_score >= 4.0: status = "PASS"
        elif total_score >= 3.0: status = "HOLD"
        else: status = "DROP"
        
        # 하드 규칙 적용 (결정론적 검사 결과가 DROP이면 강제 DROP)
        if det_report["status"] == "DROP":
            status = "DROP"
            report["drop_reason"] = det_report["drop_reason"]
        else:
            report["drop_reason"] = None

        report["status"] = status
        return report

    def _evaluate_deterministically(self, content: Dict) -> Dict:
        """[v18.8 Update] 결정론적 지표 검사 (사냥꾼의 8단계 DNA 대응)"""
        script = content.get("script", "")
        script_lower = script.lower()
        
        scores = {
            "hook_score": 3,
            "why_now_score": 3,
            "scenario_score": 3,
            "theme_score": 3,
            "action_score": 3,
            "status": "PASS",
            "drop_reason": None
        }

        # 1. HOOK 체크 (시장 데이터 숫자로 시작하거나 ? 포함)
        lines = [l.strip() for l in script.split('\n') if l.strip()]
        first_line = lines[0].lower() if lines else ""
        
        # [BANNED PHRASE CHECK - ROBOT DETECTOR]
        robot_phrases = [
            "왜 지금 시장은", "상황에 주목하고 있을까", "포착되었다", "관측된다", 
            "증명된 사실", "이례적인 움직임", "수급 쏠림", "디커플링 현상",
            "주요 거시 지표", "결정적 수급 변화"
        ]
        robot_count = sum(1 for rp in robot_phrases if rp in script)
        if robot_count >= 2:
            scores["status"] = "DROP"
            scores["drop_reason"] = f"Robot signature detected ({robot_count} phrases found)"
            return scores

        # 1. HOOK 체크 (사냥꾼 페르소나 강화)
        lines = [l.strip() for l in script.split('\n') if l.strip()]
        first_line = lines[0].lower() if lines else ""
        
        # [HUNTER PERSONA MARKERS]
        hunter_markers = ["야,", "너,", "형이", "말해봐", "샴페인", "손가락", "밤잠", "길목", "냄새"]
        persona_score = sum(2 for hm in hunter_markers if hm in script)
        
        banned_hooks = ["이상한 점이 느껴지지 않아", "이상한 점이 느껴되지 않아", "이상한 점을 느끼껴지지 않아"]
        if any(bh in script for bh in banned_hooks):
            scores["hook_score"] = 1
            scores["status"] = "DROP"
            scores["drop_reason"] = "Banned cliché found in hook"
        elif any(hm in first_line for hm in ["야,", "너,", "형이", "솔직히"]):
            scores["hook_score"] = 5
        elif "[hook]" in script_lower or re.search(r'\d+', first_line) or "?" in first_line:
            scores["hook_score"] = 4
        else:
            scores["hook_score"] = 2

        # 2. EVIDENCE/NUMBERS 체크 (숫자로 증명)
        has_numbers = len(re.findall(r'\d+', script)) >= 3
        if has_numbers:
            scores["why_now_score"] = 5
        elif "숫자로 증명" in script_lower:
            scores["why_now_score"] = 2 # 말로만 숫자로 증명한다고 하면 감점
        else:
            scores["why_now_score"] = 1

        # 3. WHY/CAUSALITY 체크 (수익의 계보, 세 가지 포인트 등)
        if any(x in script_lower for x in ["세 가지", "3가지", "계보", "돈의 흐름", "수익"]):
            scores["scenario_score"] = 5
        elif any(x in script_lower for x in ["[why]", "인과관계", "이유", "비즈니스"]):
            scores["scenario_score"] = 3
        else:
            scores["scenario_score"] = 1

        # 4. ACTION/TARGET 체크 (행동 지침 및 종목명)
        action_indicators = ["대응", "타점", "매수", "사냥", "움직여", "명령", "결론", "길목"]
        if any(x in script_lower for x in action_indicators):
            scores["action_score"] = 5
        else:
            scores["action_score"] = 1
            scores["status"] = "DROP"
            scores["drop_reason"] = "ACTION/TARGET missing or invalid"

        # 최종 점수 보정 (페르소나 점수 반영)
        if persona_score < 4 and scores["status"] == "PASS":
             scores["status"] = "HOLD" # 페르소나가 약하면 HOLD로 격하
             scores["drop_reason"] = "Weak Hunter Persona"

        return scores

        return scores

    def _build_evaluation_prompt(self, content: Dict) -> str:
        return f"""
        당신은 유튜브 콘텐츠의 품질을 엄격하게 심사하는 '스크립트 게이트키퍼'입니다. 
        다음 생성된 스크립트를 5개 항목(각 5점 만점)으로 평가하세요.
        
        [콘텐츠 정보]
        타이틀: {content.get('title')}
        타입: {content.get('type')}
        액션: {content.get('action')}
        스크립트 전문:
        {content.get('script')}
        
        [평가 기준]
        1. HOOK (초반 흡입력): 질문/모순으로 시작하는가? (5: 궁금증 유발, 3: 일반적, 1: 뉴스 요약)
        2. WHY NOW (설명력): 숫자와 변화가 포함되어 타이밍이 명확한가? (5: 숫자+변화 명확, 3: 일부 포함, 1: 추상적)
        3. SCENARIO (품질): 시나리오 중 하나를 명확히 선택하여 결론을 내는가? (5: 명확한 선택, 3: 존재만 함, 1: 없음)
        4. THEME/STOCK (연결성): 섹터/종목과 이벤트가 합리적으로 연결되는가? (5: 명확, 3: 섹터만, 1: 없음)
        5. ACTION (행동유도): 무엇을 해야하는지 조건과 행동이 명확한가? (5: 조건+행동 명확, 3: 모호, 1: 없음)
        
        결과는 반드시 다음 JSON 형식으로만 응답하세요:
        {{
            "hook_score": int,
            "why_now_score": int,
            "scenario_score": int,
            "theme_score": int,
            "action_score": int,
            "explanation": "간단한 평가 요약"
        }}
        """
