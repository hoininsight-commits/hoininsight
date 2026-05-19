# src/agents/collectors/sentiment_agent.py

from pathlib import Path
from src.agents.collector.social_prediction_collector import SocialPredictionCollector

class SentimentAgent:
    name = "SENTIMENT"
    sensitivity = "HIGH"
    ttl_minutes = 30

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.collector = SocialPredictionCollector()

    def run(self) -> dict:
        print(f"[{self.name}] 데이터 수집 및 정제, 키워드 추출 시작...")
        try:
            from src.agents.collector import CollectorAgent
            import re
            from collections import Counter
            import requests
            from bs4 import BeautifulSoup
            import json
            
            # 1. 수집기 호출 (순수 원시 데이터만 가져옴)
            collector = CollectorAgent()
            collector.output_dir = self.output_dir
            raw_result = collector.collect_sentiment()
            headlines = raw_result.get("data", {}).get("data", {}).get("news_headlines", [])
            
            # 2. 중복 제거 및 스팸 필터링 (De-duplication & Anti-Spam)
            seen_titles = set()
            unique_headlines = []
            spam_keywords = ["[포토]", "고객충성도", "부문 수상", "대상 수상", "특징주", "[인사]"]
            for h in headlines:
                title = h.get("title", "").strip()
                # 스팸 키워드 포함 기사 패스
                if any(spam in title for spam in spam_keywords):
                    continue
                if title not in seen_titles:
                    seen_titles.add(title)
                    unique_headlines.append(h)
            headlines = unique_headlines
            
            # 3. 빈도수 기반 트렌드 스코어링 + 월가 매체 가중치
            stopwords = set([
                "은", "는", "이", "가", "에", "에서", "로", "으로", "과", "와", "을", "를", "의", "및", "등", "한", "수", "더", "위", "년", "월", "일", "원", "달러", "억", "조", "대해", "대한", "위해", "위한", "기자", "뉴스", "속보", "종합", "특징주", "마감", "포토", "부문", "대상", "수상", "브랜드", "고객충성도",
                "the", "a", "an", "in", "on", "at", "for", "to", "of", "and", "with", "is", "are", "be", "by", "from", "as", "it", "that", "this", "they", "its", "has", "have", "will", "new", "how", "what", "why", "who", "when", "where", "not"
            ])

            word_counts = Counter()
            for h in headlines:
                words = re.findall(r'[a-zA-Z가-힣]+', h["title"].lower())
                valid_words = [w for w in words if w not in stopwords and len(w) > 1]
                word_counts.update(valid_words)

            premium_sources = ["FT Markets", "CNBC Economy", "CNBC Finance", "Yahoo Finance", "Investing.com", "Bloomberg", "Reuters"]
            # IB 리포트 탐지 패턴: 목표주가·등급 변경은 경제사냥꾼의 1순위 트리거
            ib_report_patterns = [
                "raises target", "cuts target", "raises price target", "cuts price target",
                "upgrades to buy", "upgrades to", "downgrades to", "initiates coverage",
                "outperform", "overweight", "underweight", "price target",
                "analyst note", "analyst rating", "analyst raises", "analyst cuts",
                "목표주가 상향", "목표주가 하향", "투자의견 상향", "투자의견 하향",
                "buy rating", "sell rating", "hold rating",
            ]
            # IB 리포트 출처 소스
            ib_sources = ["MarketBeat", "Benzinga Analyst", "Seeking Alpha"]

            for h in headlines:
                words = set(re.findall(r'[a-zA-Z가-힣]+', h["title"].lower()))
                base_score = sum(word_counts[w] for w in words if w not in stopwords and len(w) > 1)

                # 출처 기반 프리미엄 점수 부여
                source = h.get("source", "")
                title_lower = h.get("title", "").lower()
                if any(ps in source for ps in premium_sources):
                    base_score += 100  # 프리미엄 매체

                # IB 리포트 패턴 탐지: 가장 높은 가중치 (경제사냥꾼 1순위 트리거)
                if any(src in source for src in ib_sources) or any(pat in title_lower for pat in ib_report_patterns):
                    base_score += 300
                    h["is_ib_report"] = True

                h["trend_score"] = base_score

            headlines.sort(key=lambda x: (x.get("trend_score", 0), x.get("timestamp", "")), reverse=True)
            print(f"  [{self.name}] 스팸 필터링 및 트렌드 스코어링 완료. (최종 {len(headlines)}개 기사)")

            # 4. 상위 10개 기사 딥 스크래핑
            print(f"  [{self.name}] 상위 10개 핵심 기사 딥 스크래핑 중...")
            for h in headlines[:10]:
                try:
                    url = h.get("link")
                    if not url: continue
                    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
                    resp = requests.get(url, timeout=5, headers=headers)
                    if resp.status_code == 200:
                        soup = BeautifulSoup(resp.content, "html.parser")
                        p_texts = [p.get_text().strip() for p in soup.find_all(["p", "div"]) if len(p.get_text().strip()) > 40]
                        body_text = " ".join(p_texts[:15]) 
                        if body_text:
                            detail_info = re.findall(r'[^.]*?(\d+%|\d+억|\d+조|\d+억\s*달러|\d+%\s*인상|성과급\s*[\d,]+|영업이익\s*[\d,]+)[^.]*\.', body_text)
                            if detail_info:
                                h["summary"] = "[DEEP_DETAIL] " + " ".join(detail_info[:3]) + " | " + h["summary"]
                            else:
                                h["summary"] = body_text[:700] + "..."
                            h["is_deep_scraped"] = True
                except:
                    continue
                    
            # 5. [v2.5] 제미나이 기반 지능형 토픽 사냥 (Gemini-Driven Discovery)
            print(f"  [{self.name}] 🧠 제미나이를 통한 지능형 토픽 분석 및 키워드 추출 중...")
            from src.core.gemini_client import GeminiClient
            client = GeminiClient()
            
            social_trending = self.collector.collect_all([]) 
            
            # 모든 소스 헤드라인 통합 (v2.9 비용 최적화: 80개로 압축)
            all_headlines = []
            for h in headlines[:80]: 
                all_headlines.append(f"[{h.get('source')}] {h.get('title')}")
            
            social_context = []
            for skey in ["polymarket", "hacker_news"]:
                for item in social_trending.get(skey, []):
                    social_context.append(f"[{skey.upper()}_TREND] {item.get('title')}")

            full_context = "\n".join(all_headlines + social_context)

            prompt = f"""
당신은 전 세계 자본의 흐름을 추적하는 최고의 매크로 전략가입니다. 
제공된 뉴스 헤드라인과 소셜 트렌드 데이터(최대 80건)를 분석하여, 오늘 시장에서 가장 '구체적'이고 '새로운' 충격을 주고 있는 핵심 개별 사건 10개를 추출하십시오.

### 🚫 [제외 대상 - 절대로 뽑지 마십시오]
- 매일 반복되는 거대 담론 (Interest Rates, Inflation, Fed, FOMC 등)
- 일반적인 시장 상황 (Stock Market, Wall Street, S&P 500 등)
- 루틴한 실적 발표 (Q1 Earnings, Earnings Call, Quarterly Report 등) - 단, 특정 기업의 파격적 실적/사고는 포함 가능

### 🎯 [우선 선정 대상 — 최우선 순서]
1. **IB 리포트 트리거**: Goldman Sachs, UBS, JP Morgan, Morgan Stanley, 키움, 신한, KB 등 주요 기관의 목표주가 상향/하향, 등급 변경 (예: "UBS raises Samsung target to 95,000") — 이것이 경제사냥꾼 토픽의 1순위 트리거
2. **오늘 처음 발생한 구체적 사건**: 특정 기관 보고서 발표, 기업 실적 서프라이즈, 정책 공시 등
3. **고유 명사가 포함된 신선한 이슈**: 특정 기업의 인수합병, 신기술 발표 등
4. 시장의 심리가 급격히 변하고 있는 구체적인 지점

### 📊 [현재 데이터 풀]
{full_context}

---
위 데이터를 바탕으로 다음 JSON 형식으로만 응답하십시오. (설명 없이 JSON만 반환)
{{
  "title": "Daily Strategic Sentiment Keywords",
  "search_keywords": ["사건1", "사건2", "사건3", "사건4", "사건5", "사건6", "사건7", "사건8", "사건9", "사건10"],
  "rationale": "이 10가지 사건들이 오늘 특히 중요한 이유에 대한 짧은 요약 (150자 이내)"
}}
"""
            search_keywords = ["MARKET TREND", "ECONOMY"]
            rationale = "기본 키워드 사용"
            try:
                # [v2.9.2] 저비용 Flash 모델 기본값 사용 (Tier 3)
                # 모델명을 None으로 설정하여 시스템 기본 Flash 모델(2.5-flash) 사용
                response = client.call_json_controlled(
                    prompt, 
                    agent="WRITER", 
                    tier=3, 
                    model=None 
                )
                if response and "search_keywords" in response:
                    search_keywords = response.get("search_keywords", [])[:10]
                    rationale = response.get("rationale", "선정 이유 없음")
                    print(f"  [{self.name}] 🎯 지능형(저비용) 10대 토픽: {search_keywords}")
                    print(f"  [{self.name}] 💡 선정 이유: {rationale}")
                else:
                    print(f"  ⚠️ [SentimentAgent] 제미나이 응답이 없거나 형식이 올바르지 않습니다. 폴백 가동.")
                    # 명시적 에러를 발생시켜 아래 except 블록으로 보냄
                    raise Exception("Invalid Gemini Response")

            except Exception as e:
                print(f"  ⚠️ [SentimentAgent] 폴백 가동: {e}")
                # 빈도수 기반 상위 키워드 10개 추출
                search_keywords = [w for w, _ in word_counts.most_common(10)]
                rationale = "Gemini 장애로 인한 빈도수 통계 기반 자동 키워드 추출"

            # 6. JSON 파일 덮어쓰기
            raw_result["data"]["news_headlines"] = headlines
            raw_result["data"]["search_keywords"] = search_keywords
            
            output_path = self.output_dir / "sentiment.json"
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(raw_result, f, ensure_ascii=False, indent=2)

            print(f"[{self.name}] ✅ 제미나이 기반 10대 개별 사건 추출 완료")
            return {
                "agent": self.name,
                "process_success": True,
                "data_valid": raw_result["metadata"]["freshness_status"] != "UNKNOWN",
                "freshness_status": raw_result["metadata"]["freshness_status"],
                "result": raw_result,
                "ai_rationale": rationale
            }
        except Exception as e:
            print(f"[{self.name}] ❌ 실패: {e}")
            return {
                "agent": self.name,
                "process_success": False,
                "error": str(e)
            }


if __name__ == "__main__":
    from pathlib import Path
    from src.utils.target_date import get_standard_path_prefix
    out = Path("data/raw") / get_standard_path_prefix()
    out.mkdir(parents=True, exist_ok=True)
    SentimentAgent(out).run()
