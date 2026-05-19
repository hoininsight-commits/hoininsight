import json
from typing import List, Dict
from ddgs import DDGS
from src.core.gemini_client import GeminiClient

class DeepResearchAgent:
    """
    [v21.0] Autonomous Deep Research Layer
    Dynamically generates search queries from raw data, searches the web, 
    and synthesizes structural context (moats, K-stock links) without hardcoded playbooks.
    """

    def __init__(self):
        self.gemini = GeminiClient()
        self.ddgs = DDGS()

    def generate_queries(self, raw_context: str) -> List[str]:
        """
        1. 읽어들인 데이터에서 가장 중요한 매크로/테크 이벤트를 추출하고,
        2. 해당 이벤트와 연결될 수 있는 '한국 수혜주', '구조적 해자(독점)', '핵심 부품' 등을
           찾기 위한 최적의 구글링(DuckDuckGo) 검색어 3개를 생성합니다.
        """
        prompt = f"""
        당신은 최고의 리서치 애널리스트입니다. 아래 오늘 수집된 데이터를 읽고 가장 강력한 파급력을 가질 수 있는 이벤트 1개를 선정하세요.
        그런 다음, 해당 이벤트가 **한국 증시(K-Stock)**의 특정 종목, 독점 기술, 납품 이력 등과 어떻게 연결될지 심층 분석하기 위한 **한글 검색어(Query) 딱 3개**만 생성하세요.

        [오늘의 데이터]
        {raw_context[:3000]}  # 너무 길면 짤릴 수 있으므로 앞부분 위주로

        [검색어 작성 가이드]
        - 현상의 표면 너머, **'기존 시스템의 물리적/구조적 한계(Bottleneck)', '이 변화가 필연적인 기술적 이유', '가짜 수혜주를 걸러내기 위한 실적/수주 팩트'** 등을 파헤치는 키워드를 포함하세요.
        - 단순 '테마' 검색이 아닌, 이 거대한 산업 전환의 **'최종 승자(Mastermind)'**와 **'적자 상태인 허구의 테마주'**를 대조할 수 있는 검색어를 만드세요.
        - **중요**: 사냥꾼의 권위를 뒷받침할 **'구체적인 기술 표준, 글로벌 빅테크의 독점 계약 규모, 공장 신설 투자액, 공급 부족(Shortage) 데이터'** 등을 찾을 수 있는 키워드를 포함하세요.
        - 예: "가상자산 과세 도입 인도 시장 거래량 폭락 수치", "한국은행 코인 투자자 통계 조세 사각지대", "금투세 폐지와 코인 과세 형평성 논란 주식 시장 영향"

        반드시 아래 JSON 형식으로만 반환하세요:
        {{
            "target_event": "선정된 글로벌 이벤트",
            "queries": ["검색어1", "검색어2", "검색어3"]
        }}
        """

        try:
            res = self.gemini.call_json_controlled(prompt, agent="DEEP_RESEARCHER", tier=3, model="gemini-flash-latest")
            if res and isinstance(res, dict) and "queries" in res:
                return res["queries"]
            return []
        except Exception as e:
            print(f"  ❌ [DeepResearch] Query Generation Error: {e}")
            return []

    def execute_search(self, query: str, max_results: int = 3) -> List[Dict]:
        """DuckDuckGo를 통해 웹 검색 수행"""
        print(f"  🔍 [DeepResearch] Searching: {query}")
        results = []
        try:
            for r in self.ddgs.text(query, max_results=max_results):
                results.append(r)
        except Exception as e:
            print(f"  ⚠️ [DeepResearch] Search error for '{query}': {e}")
        return results

    def synthesize_context(self, target_event: str, search_results: List[Dict]) -> str:
        """
        검색된 문서 조각들을 모아서 하나의 '사냥꾼의 수첩(맥락)'으로 압축합니다.
        """
        if not search_results:
            return ""

        snippets = []
        for r in search_results:
            title = r.get("title", "")
            body = r.get("body", "")
            snippets.append(f"- [{title}] {body}")
        
        snippets_text = "\n".join(snippets)

        prompt = f"""
        당신은 금융 리서치 요약 전문가입니다. 아래는 '{target_event}'와 관련하여 수집된 웹 검색 결과입니다.
        이를 바탕으로, 경제사냥꾼이 참고할 만한 **'산업적 필연성(왜 이 변화가 거부할 수 없는가)'**과 **'가짜 테마주의 함정(실적 없는 종목의 위험성)'**을 300자 이내의 단일 문단으로 차갑게 압축하세요. 
        단순 종목 나열이 아닌 '물리적 한계와 극복'이라는 인과관계를 숫자로 증명하세요.

        [수집된 웹 검색 결과]
        {snippets_text}

        결과물은 오직 요약된 텍스트만 출력하세요. (JSON 아님)
        """

        try:
            summary = self.gemini.call_controlled(prompt, agent="DEEP_RESEARCHER", tier=3, model="gemini-flash-latest")
            return summary.strip()
        except Exception as e:
            print(f"  ❌ [DeepResearch] Synthesis Error: {e}")
            return ""

    def conduct_research(self, raw_context: str) -> str:
        """
        전체 파이프라인 엔트리 포인트.
        raw_context -> 쿼리 생성 -> 검색 -> 요약 -> 반환
        """
        print("  🧠 [DeepResearch] Starting autonomous deep research...")
        
        queries = self.generate_queries(raw_context)
        if not queries:
            print("  ⚠️ [DeepResearch] No queries generated. Skipping deep research.")
            return ""

        all_results = []
        for q in queries:
            results = self.execute_search(q, max_results=3)
            all_results.extend(results)

        if not all_results:
            print("  ⚠️ [DeepResearch] No search results found.")
            return ""

        target_event = "오늘의 핵심 테마"  # Context에서 추출하면 좋지만 심플하게
        
        print("  📝 [DeepResearch] Synthesizing structural context...")
        final_context = self.synthesize_context(target_event, all_results)
        
        print("  ✅ [DeepResearch] Research completed.")
        return final_context

if __name__ == "__main__":
    # Test
    agent = DeepResearchAgent()
    dummy_context = "오늘 일론 머스크가 테네시 멤피스에 세계 최대 규모의 슈퍼컴퓨터 '콜로서스'를 짓고 데이터센터 투자를 확대한다고 발표했다."
    res = agent.conduct_research(dummy_context)
    print("\n[RESULT]")
    print(res)
