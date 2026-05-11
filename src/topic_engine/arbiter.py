import json
import os
from typing import List, Dict
from pathlib import Path
from src.core.gemini_client import GeminiClient
from src.utils.target_date import get_now_kst, get_target_ymd
from src.agents.collectors.deep_research_agent import DeepResearchAgent

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

        # 2. 전략 사냥꾼 프롬프트 (Market Hunter DNA)
        prompt = f"""
 당신은 글로벌 거시 흐름을 기반으로 **'한국 주식 시장(KOSPI/KOSDAQ)의 다음 급등 테마'**를 찾아내는 독보적인 국내 시장 사냥꾼입니다.
 당신은 단순히 해외 뉴스를 전달하는 사람이 아니라, "미국에서 이 뉴스가 터졌으니, 내일 한국 시장의 이 테마와 이 종목이 미쳐 날뛰겠구나"라고 정확히 짚어내는 실전 고수입니다.
 {exclude_instruction}

 ### 🏹 [사냥꾼의 투트랙(Two-Track) 사냥 지침]
 1. **트랙 A: 글로벌 동조화 (Global Macro)**: 어제 미국/글로벌 시장의 폭등/폭락이나 기술 표준 변경이 한국 증시로 전이되는 '인과관계'를 사냥하십시오. (예: WDC 급등 -> 티엘비 수혜)
 2. **트랙 B: 국내 구조적 특수성 (Domestic Scarcity)**: 글로벌 이슈와 별개로, 국내 시장만의 **'수급 병목(IPO 희소성, 청약 과열)'**이나 **'정부의 거대 정책 자금(펀드 출범, 규제 해제)'**이 만드는 '돈의 길목'을 사냥하십시오. (예: 코스모로보틱스 상장 -> 로봇 섹터 낙수효과)

 **[선정 기준]**
 1. **파괴적 임계점**: 글로벌 이슈든 국내 정책이든, 오늘 당장 돈의 흐름이 **'병목 현상'**을 일으키며 폭발할 지점인가를 최우선으로 봅니다.
 2. **기술적/물리적 필연성**: "왜 지금 이 변화가 올 수밖에 없는가?"를 글로벌 기술 표준이나 국내 인구 구조/정책적 강제성으로 증명하십시오.
 3. **내일의 주인공 (Next Money Spot)**: 이미 불붙은 종목이 아니라, 내일 아침 자금이 몰릴 수밖에 없는 '구조적 입구'를 선점하십시오.

 ### 📊 [현재 시장 및 DART 전수 조사 데이터]
 {full_condensed_data}

 ---

 ### 🚀 [사냥 결과 제출]
 반드시 아래 JSON 형식으로만 제출하십시오. 한국 투자자들이 바로 이해할 수 있는 **'한국형 투자 용어'**를 사용하십시오.

 {{
   "hunting_target_topic": "내일 한국 시장을 뒤흔들 가장 뜨거운 국내 테마/종목 제목",
   "hunting_rationale": "글로벌/거시 이슈가 어떻게 한국의 이 테마로 '돈의 길목'을 만드는가? (논리적 연결 고리)",
   "hard_evidence": "DART 공시 내용, 구체적인 국내 뉴스 헤드라인, 수치 데이터 등 (예: 5월 8일 XX사 수주 공시)",
   "next_money_spot": "구체적으로 어떤 국내 상장사(종목명 명시) 혹은 섹터로 돈이 몰릴 것인지에 대한 사냥꾼의 직관"
 }}
"""

        
        print(f"  🧠 [Arbiter] Hunting with Hunter DNA (Model: 1.5-Pro)...")
        try:
            # [v23.0] 전략 사냥 단계는 통찰력 극대화를 위해 Gemini 1.5 Pro 모델 사용
            response = self.client.call_json_controlled(
                prompt, 
                agent="ARBITER_V2", 
                tier=1, 
                model="gemini-2.5-pro"
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


