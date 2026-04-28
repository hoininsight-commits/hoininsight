import json
import os
from typing import List, Dict
from pathlib import Path
from src.core.gemini_client import GeminiClient
from src.utils.target_date import get_now_kst, get_target_ymd

class TopicArbiter:
    """[v15.1] Dynamic Topic Arbiter - Economic Hunter Strategist Upgrade"""

    def __init__(self):
        self.client = GeminiClient()

    def select_best(self, candidates: List[Dict], market_axis: Dict) -> Dict:
        """
        Gemini를 사용하여 수많은 후보 중 가장 '사냥할 가치가 있는' 오늘 최고의 토픽을 선정
        """
        if not candidates:
            return {"MAIN": None, "SECONDARY": [], "EARLY": []}

        # 1. 후보군 텍스트 요약
        candidate_summary = []
        for i, cand in enumerate(candidates):
            source = cand.get("source", "UNKNOWN")
            event = cand.get("event", "")
            candidate_summary.append(f"[{i}] [S:{source}] {event}")

        candidate_list_str = "\n".join(candidate_summary)
        
        # 현재 날짜 및 요일 정보 (KST 보정 v15.2)
        now = get_now_kst()
        today_str = get_target_ymd()
        weekdays = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
        weekday_str = weekdays[now.weekday()]
        is_weekend = now.weekday() >= 5
        
        # 2. 사냥꾼의 전략적 안목 주입 (DNA Upgrade)
        prompt = f"""
당신은 전설적인 금융 유튜버 '경제사냥꾼'의 전략기획실장입니다. 
수많은 소음(Noise) 속에서 오늘 당장 사냥해야 할 단 하나의 '급소'를 찾아내십시오.

[CANDIDATES - 오늘 포착된 후보군]
{candidate_list_str}

45: [사냥꾼의 토픽 선정 원칙]
46: 1. **Absolute Autonomy**: 특정 국가(국내/국외), 업종, 테마에 대한 어떠한 선입견도 갖지 마십시오. 오늘 포착된 모든 후보군 중 **'절대적인 시장 파급력'**과 **'실질적인 투자 시그널'**이 가장 강력한 단 하나를 스스로 결정하십시오.
47: 2. **Signal vs Noise**: 단순히 빈번하게 노출되는 뉴스(소음)와 시장의 판을 바꾸는 핵심 변수(시그널)를 엄격히 구분하십시오. 최근 반복적으로 노출되었으나 새로운 진전이 없는 토픽은 과감히 배제하고, 가장 치명적인 '급소'를 사냥하십시오.
48: 3. **Data Loyalty**: 외부의 가이드라인이 아닌, 오직 주어진 {today_str}의 날것의 데이터와 시장 지표(Market Axis)에만 근거하여 판단하십시오.

[OUTPUT JSON FORMAT]
{{
  "main_index": (int), 
  "secondary_indices": [int, int], 
  "rationale": "왜 이 토픽이 오늘 최고의 사냥감인가? (이면의 본질 분석)", 
  "hunter_insight": "앞으로 시장에 어떤 충격 혹은 기회가 몰아칠 것인가? (예측적 관점)"
}}

반드시 JSON으로만 응답하라.
"""
        # 디버그용 프롬프트 기록
        log_dir = Path("data/logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        (log_dir / "arbiter_prompt.txt").write_text(prompt, encoding="utf-8")

        print(f"  🧠 [Arbiter] Selecting from {len(candidates)} candidates (DNA v15.1)...")
        try:
            # Tier 3 (Flash)로 전환하여 형식 준수율 상향
            response = self.client.call_json_controlled(prompt, agent="ARBITER", tier=3)
            
            if not response:
                print("  ⚠️ [Arbiter] Controlled call failed, trying standard call_json...")
                response = self.client.call_json(prompt)

            main_idx = response.get("main_index", 0)
            sec_indices = response.get("secondary_indices", [])
            
            if main_idx >= len(candidates):
                main_idx = 0

            main_cand = candidates[main_idx]
            main_cand["arbiter_rationale"] = response.get("rationale")
            main_cand["hunter_insight"] = response.get("hunter_insight")
            main_cand["tier"] = "MAIN/TIER_1"
            
            print(f"  🏆 Arbiter Winner: {main_cand['event']}")

            secondary = [candidates[i] for i in sec_indices if i < len(candidates)]
            for s in secondary: s["tier"] = "SECONDARY/TIER_2"

            return {
                "MAIN": main_cand,
                "SECONDARY": secondary,
                "EARLY": [c for i, c in enumerate(candidates) if i not in ([main_idx] + sec_indices)][:3]
            }

        except Exception as e:
            print(f"  ❌ [Arbiter] Runtime Error: {e}")
            return {"MAIN": candidates[0], "SECONDARY": [], "EARLY": []}

    def _apply_intent_boost(self, text: str) -> float:
        """권위자 키워드 감지 시 가중치 반환"""
        authority_keywords = ["백악관", "NSC", "연준", "Fed", "파월", "옐런", "국방부", "공시", "DART", "정부 정책"]
        for kw in authority_keywords:
            if kw in text:
                return 2.0
        return 1.0
