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

        # [COST SAVVY] 오늘 이미 발송된 토픽 로드
        published_topics = []
        log_path = Path("data/history/content_log.json")
        if log_path.exists():
            try:
                log = json.loads(log_path.read_text(encoding="utf-8"))
                today_str = get_target_ymd() # YYYY-MM-DD
                for entry in log.get("contents", []):
                    if entry.get("date") == today_str and entry.get("publish_status") == "SUCCESS":
                        published_topics.append(entry.get("title", ""))
            except: pass
            
        if published_topics:
            print(f"  [FILTER] 오늘 이미 발송된 토픽 {len(published_topics)}개 감지. 중복 선정 방지 가동.")
            
        exclude_instruction = f"\n**[중요] 아래 토픽들은 오늘 이미 다루었으므로 절대 다시 선정하지 마십시오:**\n" + "\n".join([f"- {t}" for t in published_topics]) if published_topics else ""

        # 2. 전략 사냥꾼 프롬프트 (Market Hunter DNA)
        prompt = f"""
당신은 전 세계의 하드 데이터와 소셜 트렌드를 결합하여 **'다음 돈이 쏠릴 길목'**을 찾아내는 노련한 시장 사냥꾼입니다.
당신은 단순히 지표를 읽는 전문가가 아니라, "1차 수혜주가 올랐으니 이제 2차, 3차는 이놈이다"라고 수익의 순서를 짚어내는 실전 투자 전문가입니다.
{exclude_instruction}

### 🎯 [사냥 및 토픽 선정 지침]
제공된 모든 데이터(Social, News, FRED, Market, DART 등)를 샅샅이 뒤져서, **지금 당장 시청자가 돈을 들고 뛰어들거나 반드시 피해야 할 '돈의 흐름'**을 포착하십시오.

**[사냥꾼의 핵심 로직]**
1. **이상징후 (Anomaly)**: "데이터는 좋다는데 왜 주가는 떨어지지?" 혹은 "별 뉴스 없는데 왜 이 거래량이 터지지?" 같은 상식 밖의 움직임을 찾아라.
2. **모순 (Mismatch)**: 뉴스 헤드라인과 실제 숫자가 따로 노는 지점을 공략해라.
3. **글로벌 권위 (Authority)**: 연준(Fed), 엔비디아, 워런 버핏 등 시장을 움직이는 거인들의 발언 속에 숨은 진짜 의도를 파악해라.

**[선정 기준]**
1. **돈의 이동 경로 (Money Flow)**: 특정 뉴스가 어떤 섹터나 종목으로 자금을 이동시키고 있는가? (예: 엔비디아 -> 냉각 -> 유리 기판)
2. **순환매의 길목 (Sector Rotation)**: 이미 오른 놈 말고, 그 다음 차례가 올 수밖에 없는 논리적 '순서'가 있는 토픽인가?
3. **직관적 기회 (Actionable Opportunity)**: 설명을 들었을 때 "아, 그래서 이 종목을 봐야 하는구나"라고 초보자도 무릎을 탁 칠 만큼 명확한 기회인가?

### 📊 [현재 시장 데이터 전수 조사]
{full_condensed_data}

---

### 🚀 [사냥 결과 제출]
반드시 아래 JSON 형식으로만 제출하십시오. **절대 어려운 학술 용어나 거시 경제 용어(매크로)로 도배하지 마십시오.** 오직 '돈'과 '수익'의 관점에서, 동네 형이 설명해 주듯 직관적으로 응답하십시오.

{{
  "hunting_target_topic": "지금 돈이 몰리고 있는(혹은 몰릴) 가장 뜨거운 사냥감(토픽) 제목",
  "hunting_rationale": "왜 이 토픽이 '다음 수익의 길목'인가? 자금이 이동하는 순서와 논리적 근거 (예: A가 터졌으니 이제 B가 갈 차례)",
  "hard_evidence": "이 사냥을 뒷받침하는 구체적인 숫자나 공시 데이터 (FRED, DART 등 인용)",
  "next_money_spot": "이 이슈로 인해 구체적으로 어떤 섹터나 종목군으로 돈이 흘러갈 것인지에 대한 직관적 예측"
}}
"""

        
        print(f"  🧠 [Arbiter] Hunting with Hunter DNA (Model: 1.5-Pro)...")
        try:
            # [v23.0] 전략 사냥 단계는 통찰력 극대화를 위해 Gemini 1.5 Pro 모델 사용
            response = self.client.call_json_controlled(
                prompt, 
                agent="ARBITER_V2", 
                tier=1, 
                model="gemini-1.5-pro-latest"
            )
            
            if not response or "hunting_target_topic" not in response:
                print("  ⚠️ [Arbiter] Failed to capture a strategic topic. Using fallback.")
                return {"MAIN": None}

            # 3. 결과 래핑 (ContentEngine 호환성 유지)
            main_topic = {
                "topic": response.get("hunting_target_topic"),
                "event": response.get("hunting_target_topic"),
                "arbiter_rationale": response.get("hunting_rationale"),
                "hunter_insight": response.get("next_money_spot"),
                "data_chain": response.get("hard_evidence"),
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


