import json
import os
from typing import List, Dict
from pathlib import Path
from src.core.gemini_client import GeminiClient

class TopicArbiter:
    """[v13.0] Dynamic Topic Arbiter - LLM-based Selection Intelligence"""

    def __init__(self):
        self.client = GeminiClient()

    def select_best(self, candidates: List[Dict], market_axis: Dict) -> Dict:
        """
        Gemini를 사용하여 수많은 후보 중 가장 '사냥할 가치가 있는' 토픽을 선정
        """
        if not candidates:
            return {"MAIN": None, "SECONDARY": [], "EARLY": []}

        # 1. 후보군 텍스트 요약 (v15.0 Strategist Upgrade)
        candidate_summary = []
        for i, cand in enumerate(candidates):
            source = cand.get("source", "UNKNOWN")
            score = cand.get("final_score", 0)
            # [STRATEGIST] 소스와 디테일을 포함하여 판단 근거 강화
            candidate_summary.append(f"[{i}] [S:{source}] [Score:{score:.2f}] {cand.get('event')}")

        candidate_list_str = "\n".join(candidate_summary)
        
        # 2. 사냥꾼 철학 주입 (Regime Change, Bottleneck, Policy Intent)
        prompt = f"""
너는 '경제사냥꾼' 채널의 전략 기획실장이다. 아래 후보군 중 '3일 뒤 시장을 지배할' 가장 가치 있는 토픽을 선정하라.

[CANDIDATES]
{candidate_list_str}

[SELECTION PHILOSOPHY]
1. **Regime Change (체제 변화)**: 연준 인선, 정부 정책 기조 변화 등 '판의 규칙'이 바뀌는 토픽을 최우선하라.
2. **Industrial Bottleneck (산업의 급소)**: 파업, 공급망 붕괴, 에너지 부족 등 실물 경제의 병목 현상을 포착하라.
3. **Policy Intent (정책적 의도)**: 백악관이나 국가 기관의 장기 예산 집행 계획을 단순 뉴스보다 높게 평가하라.
4. **Early Signal (예측 시장)**: Polymarket 등 예측 시장의 급격한 확률 변동은 3일 뒤의 헤드라인이 될 확률이 높다.

[OUTPUT JSON FORMAT]
{{
  "main_index": (int), 
  "secondary_indices": [int, int], 
  "rationale": "왜 이 토픽이 현재 가장 중요한가? (현상 너머의 본질)", 
  "hunter_insight": "이 이슈가 3일 뒤 시장에 어떤 충격을 줄 것인가? (예측적 관점)"
}}

반드시 JSON으로만 응답하라.
"""
        # 디버그용 프롬프트 기록
        log_dir = Path("data/logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        (log_dir / "arbiter_prompt.txt").write_text(prompt, encoding="utf-8")

        print(f"  🧠 [Arbiter] Selecting from {len(candidates)} candidates (Simplified)...")
        try:
            # Tier 3 (Flash)로 전환하여 형식 준수율 상향
            response = self.client.call_json_controlled(prompt, agent="ARBITER", tier=3)
            
            if not response:
                # 일반 call_json으로 재시도
                print("  ⚠️ [Arbiter] Controlled call failed, trying standard call_json...")
                response = self.client.call_json(prompt)

            main_idx = response.get("main_index")
            sec_indices = response.get("secondary_indices", [])
            
            # 인덱스 유효성 검사
            if main_idx is None or main_idx >= len(candidates):
                main_idx = 0 # Fallback to first

            main_cand = candidates[main_idx]
            main_cand["arbiter_rationale"] = response.get("rationale")
            main_cand["hunter_insight"] = response.get("hunter_insight")
            main_cand["tier"] = "MAIN/TIER_1"
            main_cand["tier_reason"] = "arbiter_selected"
            
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
            return None
