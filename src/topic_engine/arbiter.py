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
        
        # 2. 사냥꾼의 전략적 안목 주입 (v18.8 'Story DNA' Upgrade)
        prompt = f"""
당신은 전설적인 금융 유튜버 '경제사냥꾼'의 전략기획실장입니다. 
지금 이 순간, 대중의 아드레날린을 폭발시키고 실질적인 '돈의 흐름'을 바꿀 수 있는 단 하나의 **'사냥감(Topic)'**을 선정하십시오.

[CANDIDATES - 오늘 포착된 데이터]
{candidate_list_str}

[사냥꾼의 토픽 선정 원칙 - HUNTER'S INSTINCT]
1. **Adrenaline & Narrative**: 단순히 지표가 변했다는 뉴스(국채 금리, 유가 등)보다 **'인물의 움직임(젠슨황, 이재용, 머스크 등)'**이나 **'이례적인 사건(단독, 최초, 비밀 회동)'**처럼 대중이 열광할 서사가 있는 토픽에 압도적인 우선순위를 두십시오.
2. **Relatability (Skin in the Game)**: 투자자들이 "이건 내 돈과 직결된다"고 즉각적으로 느낄 수 있는, 피부에 와닿는 주제를 고르십시오. 너무 먼 나라의 거시 경제보다는 '지금 당장 한국 시장의 수급'을 뒤흔들 주제가 좋습니다.
3. **The Mismatch**: 시장의 기대와 실제 행동이 충돌하는 지점(예: 역대급 실적인데 파업, 재벌 총수의 갑작스러운 자사주 매입)을 포착하십시오. 거기가 바로 사냥꾼이 수익을 내는 '급소'입니다.
4. **Thumbnail Test**: 선정하려는 토픽이 "유튜브 썸네일로 만들어졌을 때 클릭하지 않고는 못 배길 정도인가?"를 스스로 자문하십시오.

[OUTPUT JSON FORMAT]
{{
  "main_index": (int), 
  "secondary_indices": [int, int], 
  "rationale": "왜 이 토픽이 오늘 최고의 '사냥감'인가? (서사와 아드레날린 관점 분석)", 
  "hunter_insight": "이 서사가 시장의 수급을 어떻게 이동시킬 것인가? (사냥꾼의 예리한 예측)"
}}

반드시 JSON으로만 응답하십시오.
"""
        # 디버그용 프롬프트 기록
        log_dir = Path("data/logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        (log_dir / "arbiter_prompt.txt").write_text(prompt, encoding="utf-8")

        print(f"  🧠 [Arbiter] Selecting from {len(candidates)} candidates (v18.8 - Hunter Instinct)...")
        try:
            response = self.client.call_json_controlled(prompt, agent="ARBITER", tier=3)
            
            if not response:
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
        """사냥꾼의 본능을 자극하는 키워드 감지 시 가중치 폭발"""
        hunter_keywords = [
            "젠슨황", "이재용", "머스크", "샘올트먼", "이부진", "삼성전자", "엔비디아",
            "단독", "최초", "비밀", "포착", "매집", "폭발", "충격", "공시", "DART",
            "파업", "인수", "합병", "M&A", "주주환원", "자사주", "기회"
        ]
        for kw in hunter_keywords:
            if kw in text:
                return 2.5  # 가중치를 2.0에서 2.5로 상향
        return 1.0

