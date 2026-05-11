import json
from typing import List, Dict
from duckduckgo_search import DDGS
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
        - 반드시 "특정 기업명" 혹은 "한국 관련주", "수혜주", "독점 기술", "납품" 등의 키워드를 포함하세요.
        - 예: "xAI 슈퍼컴퓨터 배전반 납품 한국 기업", "머스크 데이터센터 전력기기 관련주"

        반드시 아래 JSON 형식으로만 반환하세요:
        {{
            "target_event": "선정된 글로벌 이벤트",
            "queries": ["검색어1", "검색어2", "검색어3"]
        }}
        """

        try:
            res = self.gemini.call_json_controlled(prompt, agent="DEEP_RESEARCHER", tier=1, model="gemini-2.5-pro")
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
        이를 바탕으로, 경제사냥꾼이 참고할 만한 **'구조적 연결 고리(수혜주, 독점력, 향후 일정 등)'**를 300자 이내의 단일 문단으로 강력하게 압축하세요.

        [수집된 웹 검색 결과]
        {snippets_text}

        결과물은 오직 요약된 텍스트만 출력하세요. (JSON 아님)
        """

        try:
            summary = self.gemini.call_controlled(prompt, agent="DEEP_RESEARCHER", tier=1, model="gemini-2.5-pro")
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
