import json
import os
from typing import List, Dict
from pathlib import Path
from src.core.gemini_client import GeminiClient
from src.utils.target_date import get_now_kst, get_target_ymd

class TopicArbiter:
    """[v21.0] AGNOSTIC STRATEGIC ARBITER - Economic Hunter DNA Integration"""

    def __init__(self):
        self.client = GeminiClient()

    def select_topic_from_raw(self, raw_dir: Path) -> Dict:
        """
        [v21.0] 로우 데이터 폴더 전체를 전수 조사하여 가장 강력한 연결 고리를 가진 토픽 사냥
        """
        if not raw_dir.exists():
            print(f"  ⚠️ [Arbiter] Raw directory not found: {raw_dir}")
            return {"MAIN": None}

        # 1. 모든 로우 데이터 취합 및 고농축 압축 (v22.0 Data Condenser 적용)
        from src.utils.data_condenser import DataCondenser
        condenser = DataCondenser()
        
        raw_context = []
        for file_path in raw_dir.glob("*.json"):
            try:
                raw_json = json.loads(file_path.read_text(encoding='utf-8'))
                condensed_text = condenser.condense(raw_json)
                raw_context.append(f"### [DATA_SOURCE: {file_path.name}]\n{condensed_text}\n")
            except Exception as e:
                print(f"  ⚠️ [Arbiter] Skip {file_path.name}: {e}")

        if not raw_context:
            return {"MAIN": None}

        full_condensed_data = "\n".join(raw_context)

        # 2. 전략 지능형 프롬프트 (Macro Strategist)
        prompt = f"""
당신은 글로벌 자본의 흐름과 거시경제의 미래를 예측하는 최고 수준의 매크로 전략가입니다.
당신에게는 현재의 주요 이슈가 담긴 '소셜 데이터'와 실물 경제의 움직임을 보여주는 '하드 데이터(거시 지표, 시장 가격, 기업 공시)'가 제공됩니다.

### 🎯 [수행 임무 및 분석 프로세스]
당신은 제공된 데이터를 바탕으로, **현재 그리고 향후 거시경제에 가장 거대한 충격과 자본 이동을 가져올 단 하나의 핵심 토픽**을 도출해야 합니다.

**[1단계: 핵심 어젠다 포착 (Social Data 활용)]**
- 제공된 소셜 데이터를 분석하여, 단순한 가십이나 단기적 감정(공포/환희)이 아닌, **'향후 글로벌 경제 구조나 거대 자본의 이동을 근본적으로 뒤흔들 가장 파괴력 있는 이슈'**를 하나 찾아내십시오.

**[2단계: 파급력의 과학적 증명 (Hard Data 활용)]**
- 1단계에서 포착한 이슈를 나머지 하드 데이터(FRED, Market, DART 등)를 활용하여 정밀하게 해독하십시오.
- 이 이슈가 구체적으로 **어떤 경제적 메커니즘**을 통해 실물 경제(공급망, 금리, 물가 등)와 자본 시장에 충격을 줄 것인지 데이터로 증명하십시오.

### 📊 [현재 시장 데이터]
{full_condensed_data}

---

### 🚀 전체 내용 분석 
[시스템에서 분석 할 경우 전체 분석 내용 파일로 저장]
분석내용... 
---

### 🚀 [거시경제 파급력 분석 보고서]
위의 분석 프로세스를 거친 후, 아래 JSON 형식으로 상세한 결과를 제출하십시오.

{{
  "macro_economic_topic": "현재와 미래의 거시경제에 가장 거대한 파급력을 미칠 핵심 토픽",
  "topic_selection_reason": "소셜 데이터에서 이 이슈를 포착한 이유와, 이것이 왜 다른 이슈들보다 경제적으로 훨씬 더 중대한 의미를 갖는지에 대한 설명",
  "hard_data_proof": "이 토픽의 파괴력을 증명하는 구체적인 거시 지표, 시장 데이터, 혹은 기업 공시의 크로스체크 결과",
  "future_economic_impact": "이 토픽이 향후 자본 시장의 수급과 실물 경제의 구조에 어떤 구체적이고 연쇄적인 충격을 가져올 것인지에 대한 심층 전망"
}}
"""
        
        print(f"  🧠 [Arbiter] Hunting from {len(raw_context)} condensed sources (Model: 1.5-Flash)...")
        try:
            # [v22.0] 비용 최적화: 사냥 단계는 2.5-Flash 모델 사용 (v22.0 데이터 고농축 적용으로 토큰 절감)
            response = self.client.call_json_controlled(
                prompt, 
                agent="ARBITER_V2", 
                tier=2, 
                model="gemini-2.5-flash"
            )
            
            if not response or "macro_economic_topic" not in response:
                print("  ⚠️ [Arbiter] Failed to capture a strategic topic. Using fallback.")
                return {"MAIN": None}

            # 3. 결과 래핑 (ContentEngine 호환성 유지)
            main_topic = {
                "topic": response.get("macro_economic_topic"),
                "event": response.get("macro_economic_topic"),
                "arbiter_rationale": response.get("topic_selection_reason"),
                "hunter_insight": response.get("future_economic_impact"),
                "data_chain": response.get("hard_data_proof"),
                "tier": "MAIN/TIER_1",
                "source": "STRATEGIC_HUNT"
            }

            return {"MAIN": main_topic}

        except Exception as e:
            print(f"  ❌ [Arbiter] Hunting Error: {e}")
            return {"MAIN": None}

    def select_best(self, candidates: List[Dict], market_axis: Dict) -> Dict:
        """Legacy support for candidate-based selection"""
        # ... (이전 로직과 유사하게 유지하되, 내부적으로 select_topic_from_raw 호출 가능)
        return {"MAIN": candidates[0] if candidates else None, "SECONDARY": [], "EARLY": []}


