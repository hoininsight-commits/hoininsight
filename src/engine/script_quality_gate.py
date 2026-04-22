
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
        """스크립트 평가 및 최종 상태 결정"""
        script = content.get("script", "")
        title = content.get("title", "")
        
        # 1. LLM Evaluation (Gemini를 이용한 정성적/정량적 평가)
        prompt = self._build_evaluation_prompt(content)
        
        try:
            eval_res = self.gemini.call_json_controlled(prompt, agent="FACT_CHECKER")
            if not isinstance(eval_res, dict):
                raise Exception("Invalid evaluation response")
        except:
            # Fallback if LLM fails
            eval_res = {
                "hook_score": 1, "why_now_score": 1, "scenario_score": 1,
                "theme_score": 1, "action_score": 1, "reason": "Evaluation Failed"
            }

        # 2. Add Total Score & Status
        scores = [
            eval_res.get("hook_score", 1),
            eval_res.get("why_now_score", 1),
            eval_res.get("scenario_score", 1),
            eval_res.get("theme_score", 1),
            eval_res.get("action_score", 1)
        ]
        total_score = sum(scores) / len(scores)
        
        # 3. Apply Hard Rules (강제 규칙)
        status = "PASS"
        if total_score >= 4.0: status = "PASS"
        elif total_score >= 3.0: status = "HOLD"
        else: status = "DROP"
        
        drop_reason = None
        
        # [Rule 1] WHY NOW에 숫자 없음
        if not re.search(r'\d+', content.get("script", "").split("---")[-1]): # 스크립트 본문 체크
            status = "DROP"
            drop_reason = "WHY NOW lacks numeric evidence"
            
        # [Rule 2] HOOK이 뉴스 요약으로 시작 (뉴스 톤인지 체크)
        first_line = script.strip().split('\n')[0].lower()
        news_indicators = ["뉴욕증시는", "코스피는", "오늘", "보도에 따르면", "에 따르면"]
        if any(ind in first_line for ind in news_indicators):
            status = "DROP"
            drop_reason = "HOOK starts with news summary"
            
        # [Rule 3] ACTION 없음
        if not content.get("action") or content.get("action") == "N/A":
            status = "DROP"
            drop_reason = "ACTION is missing"

        report = {
            "hook_score": eval_res.get("hook_score", 0),
            "why_now_score": eval_res.get("why_now_score", 0),
            "scenario_score": eval_res.get("scenario_score", 0),
            "theme_score": eval_res.get("theme_score", 0),
            "action_score": eval_res.get("action_score", 0),
            "total_score": round(total_score, 1),
            "status": status,
            "drop_reason": drop_reason
        }
        
        return report

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
