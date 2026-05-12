import json
import os
from typing import List, Dict
from pathlib import Path
from src.core.gemini_client import GeminiClient
from src.utils.target_date import get_now_kst, get_target_ymd
from src.agents.collectors.deep_research_agent import DeepResearchAgent

from src.utils.dna_manager import DNAManager

class TopicArbiter:
    """[v21.0] AGNOSTIC STRATEGIC ARBITER - Economic Hunter DNA Integration"""

    def __init__(self):
        self.client = GeminiClient()
        self.dna_manager = DNAManager()

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

        base_condensed_data = "\n".join(raw_context)

        # [v21.1] 자율 심층 리서치 레이어 (Autonomous Deep Research)
        researcher = DeepResearchAgent()
        deep_context = researcher.conduct_research(base_condensed_data)
        
        if deep_context:
            print(f"  🧠 [Arbiter] Deep Research Context injected.")
            full_condensed_data = f"{base_condensed_data}\n\n### [DEEP RESEARCH CONTEXT (구조적 연결 고리 및 수혜주 정보)]\n{deep_context}\n"
        else:
            full_condensed_data = base_condensed_data

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

        # [v25.0] DNA Patch Injection
        dna_patches = self.dna_manager.get_latest_dna_patch(limit=3)
        self.dna_manager.log_patch_application("ARBITER")

        # 2. 전략 사냥꾼 프롬프트 (Market Hunter DNA)
        prompt = f"""
  {dna_patches}
  당신은 글로벌 거시 데이터와 국내 공시(DART)를 전수 조사하여, 시장이 아직 눈치채지 못한 **'돈의 다음 행선지'**를 포착하는 자율 사냥꾼입니다.
  특정 테마(반도체, 조선 등)에 대한 고정관념을 완전히 버리고, 오직 데이터가 가리키는 **'인과관계의 끝단'**을 추적하십시오.
  {exclude_instruction}

  ### 🏹 [사냥꾼의 3대 전략 렌즈 (The 3 Strategic Lenses)]
  다음 3가지 관점 중 하나 이상의 강력한 시그널이 포착될 때만 토픽으로 선정하십시오.

  1. **필연적 연쇄 반응 (Structural Chain)**: 
     - "A가 터졌으니, 논리적으로 B가 뒤따를 수밖에 없다"는 기술적/물리적 필연성을 추적하십시오.
     - (예: 전력 소모 폭증 -> 구리선 한계 -> 광통신 전환의 필연성)
  2. **거대 자본의 입구 (Capital Inflow Scarcity)**: 
     - 정책 자금, IPO 청약 과열, 특정 섹터로의 수급 쏠림 등 '돈의 길목'이 좁아지며 폭발적 에너지가 모이는 지점을 사냥하십시오.
     - (예: 정부 펀드 150조의 최종 수혜처, 상장 가뭄 속 특정 로봇주로의 자금 집중)
  3. **글로벌 거인의 뒷모습 (Giant's Footsteps)**: 
     - 엔비디아, 메타, 애플 등 글로벌 빅테크나 거물 투자자들이 '실제로 돈을 쓰고 있는(투자/계약)' 구체적인 행보를 사냥하십시오.
     - (예: 빅테크의 특정 부품사 지분 투자, 미 국방부의 한국 시설 실사 등)

  **[사냥 원칙 (Hunting Rules)]**
  1. **고정 테마 금지**: "요즘은 이게 유행이니까"라는 식의 접근은 사냥꾼의 자격 미달입니다. 데이터가 증명하지 못하는 유행은 거부하십시오.
  2. **이면의 본질(Paradox & Truth)**: 표면적인 뉴스 뒤에 숨겨진 '진짜 의도'나 '수급의 병목'을 찌르십시오.
  3. **내일 아침의 선점**: 이미 모두가 알고 있는 결과가 아니라, 내일 아침 개장과 동시에 자금이 쏟아져 들어올 '구조적 입구'를 찾아내십시오.

  ### 📊 [현재 시장 및 DART 전수 조사 데이터]
  {full_condensed_data}

  **[오늘의 특수 사냥 지침 (Market Crash Priority)]**
  - 오늘 코스피/코스닥 지수가 동반 하락했습니다. 단순히 '하락했다'는 사실을 넘어, **이 하락을 유발한 진짜 배후(병목, 금리, 지정학 등)와 대중의 투매 속에서 조용히 매집되고 있는 '진짜 피난처(Safe Haven)'**를 찾아내십시오. 
  - "모두가 울고 있을 때, 웃고 있는 단 하나"를 찾는 것이 오늘의 사냥 목표입니다.

  ### 🚀 [사냥 결과 제출]
  반드시 아래 JSON 형식으로만 제출하십시오.

  {{
    "hunting_target_topic": "내일 한국 시장을 뒤흔들 가장 뜨거운 전략적 토픽 제목 (사냥꾼의 톤 유지)",
    "hunting_rationale": "위 3가지 렌즈 중 어떤 논리로 이 토픽이 선정되었는가? (데이터 간의 인과관계 증명)",
    "hard_evidence": "DART 공시, 수치 데이터, 글로벌 뉴스 등 사냥의 근거가 된 핵심 팩트",
    "next_money_spot": "내일 아침 돈이 몰릴 수밖에 없는 구체적인 섹터 설명",
    "target_stocks": [
      {{
        "name": "종목명",
        "rationale": "이 종목이 왜 이번 토픽의 직접적인 수혜주인가? (공시/데이터 근거)"
      }}
    ]
  }}
"""

        
        print(f"  🧠 [Arbiter] Hunting with Hunter DNA (Model: 1.5-Pro)...")
        try:
            # [COST_OPTIMIZATION] 1차 사냥은 가성비 좋은 Gemini 1.5 Flash 사용 (비용 95% 절감)
            response = self.client.call_json_controlled(
                prompt, 
                agent="ARBITER_V2", 
                tier=3, # Tier 1(Pro) -> Tier 3(Flash)로 하향
                model="gemini-1.5-flash"
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


