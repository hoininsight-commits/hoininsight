import json
import os
from typing import List, Dict
from pathlib import Path
from src.core.gemini_client import GeminiClient

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
        
        # 2. 사냥꾼의 전략적 안목 주입 (DNA Upgrade)
        prompt = f"""
당신은 전설적인 금융 유튜버 '경제사냥꾼'의 전략기획실장입니다. 
수많은 소음(Noise) 속에서 오늘 당장 사냥해야 할 단 하나의 '급소'를 찾아내십시오.

[CANDIDATES - 오늘 포착된 후보군]
{candidate_list_str}

[사냥꾼의 토픽 선정 원칙]
1. **[CRITICAL] Today Only**: 오늘(**2026-04-26**) 발생한 사건에 압도적인 가중치를 두십시오. 3일 전 뉴스는 이미 시장에 반영된 '죽은 고기'입니다.
2. **Weekend/Sunday Logic**: 오늘이 일요일(휴장일)임을 명심하십시오. 현재 지표는 금요일 데이터입니다. 따라서 "반응이 없다"고 하지 말고, **"내일 개장 시 폭발할 잠재력"**이 가장 큰 이슈를 고르십시오.
3. **Bottleneck & Regime**: 단순한 등락이 아니라, 공급망의 병목, 정책의 거대한 전환, 체제의 붕괴 등 '판이 바뀌는' 뉴스를 사냥하십시오.
4. **Account Impact**: 시청자의 계좌를 실질적으로 녹이거나 불릴 수 있는 '돈 냄새' 나는 토픽이어야 합니다.

[OUTPUT JSON FORMAT]
{{
  "main_index": (int), 
  "secondary_indices": [int, int], 
  "rationale": "왜 이 토픽이 오늘 최고의 사냥감인가? (이면의 본질 분석)", 
  "hunter_insight": "내일(월요일) 시장이 열리자마자 어떤 충격이 몰아칠 것인가? (예측적 관점)"
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
