import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
from src.core.filters import SignalFilters
from src.core.gemini_client import GeminiClient
from src.agents.extensions.detector_extensions import DetectorEnricher
from src.agents.extensions.flow_overlay import FlowOverlay

class DetectorAgent:
    """이상징후 탐지자 — 숫자와 뉴스 맥락을 결합하여 시장의 신호를 포착함 (v7.1 News Integration)"""

    def __init__(self):
        self.base_dir = Path(os.getenv("HOIN_BASE_DIR", Path(__file__).resolve().parents[2]))
        self.today = datetime.now().strftime("%Y%m%d")
        self.raw_dir = self.base_dir / f"data/raw/{self.today}"
        self.signal_dir = self.base_dir / f"data/signals/{self.today}"
        self.signal_dir.mkdir(parents=True, exist_ok=True)
        self.filters = SignalFilters()
        self.gemini = GeminiClient()
        self.enricher = DetectorEnricher(self.base_dir, self.today)

    def load_all_data(self) -> dict:
        """모든 수집 데이터 및 90일 히스토리 로드"""
        all_data = {}
        files = ["market", "macro", "sentiment", "fred", "ecos", "dart", "consensus", "cot"]
        for name in files:
            p = self.raw_dir / f"{name}.json"
            if p.exists():
                try:
                    all_data[name] = json.loads(p.read_text())
                    print(f"  ✅ {name}.json 로드")
                except Exception as e:
                    print(f"  ❌ {name}.json 로드 실패: {e}")
        
        # 90일 히스토리 로드 (추세 분석용)
        hist_p = self.base_dir / "data/raw/history/market_90d.json"
        if hist_p.exists():
            try:
                all_data["history_90d"] = json.loads(hist_p.read_text()).get("history_90d", {})
            except: pass

        return all_data

    def build_data_summary(self, all_data: dict) -> str:
        """AI에게 줄 데이터 요약 생성"""
        market_block = all_data.get("market", {})
        market = market_block.get("data", {})
        stats  = market.get("multi_period_stats", {})
        fred   = all_data.get("fred", {}).get("data", {})
        ecos   = all_data.get("ecos", {}).get("data", {})
        sentiment = all_data.get("sentiment", {}).get("data", {})
        headlines = sentiment.get("news_headlines", [])
        
        stats_lines = []
        for key, s in stats.items():
            if not s: continue
            stats_lines.append(
                f"{key}: 현재={s.get('current')} "
                f"| 20일Z-score={s.get('z_score_20d')} "
            )

        fred_lines = [f"{k}: {v}" for k, v in fred.items() if v is not None] if fred else []
        ecos_lines = [f"{k}: {v}" for k, v in ecos.items() if v is not None] if ecos else []
        
        # kospi_foreign_net 추가 (null이면 제외)
        foreign_net = market.get("kospi_foreign_net")
        if foreign_net is not None:
            fred_lines.append(f"kospi_foreign_net: {foreign_net}")

        news_lines = [f"[{h.get('source','')}] {h.get('title','')}" for h in headlines[:15]]

        summary = f"""
=== 시장 지표 (Z-score) ===
{chr(10).join(stats_lines) if stats_lines else "데이터 없음"}

=== 거시 지표 (FRED/ECOS) ===
{fred_lines}
{ecos_lines}

=== 오늘 뉴스 헤드라인 ===
{chr(10).join(news_lines) if news_lines else "없음"}
"""
        return summary

    def extract_json(self, response_text: str) -> Optional[dict]:
        """Gemini 응답에서 JSON만 추출 (v7.2 강화)"""
        import re
        if not response_text: return None
        
        # 방법 1: 그대로 파싱
        try:
            return json.loads(response_text)
        except: pass
        
        # 방법 2: ```json ... ``` 블록 추출
        match = re.search(r'```(?:json)?\s*([\s\S]*?)```', response_text)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except: pass
            
        # 방법 3: { } 블록 추출
        match = re.search(r'(\{[\s\S]*\})', response_text)
        if match:
            try:
                return json.loads(match.group(1))
            except: pass

        return None

    def discover_autonomous_narratives(self, all_data: dict) -> list:
        """AI 자율 담론 사냥: 시장의 모순(Anomaly)과 기대 충돌을 스스로 포착 (v7.0)"""
        sentiment = all_data.get("sentiment", {}).get("data", {})
        headlines = sentiment.get("news_headlines", [])
        market = all_data.get("market", {}).get("data", {})
        
        if not headlines or not self.gemini: return []

        system_prompt = """
        You are a JSON-only response system.
        NEVER output explanations, comments, or natural language.
        ALWAYS respond with valid JSON only.
        If you cannot generate valid JSON, respond with: {"error": "parse_failed"}
        """

        prompt = f"""{system_prompt}
너는 HOIN Insight의 '경제사냥꾼' 엔진이다. 지표와 뉴스를 분석해 오늘 시장에서 가장 '이상한(Anomaly)' 서사 3가지를 선정해라.
[오늘 지표] {json.dumps(market, ensure_ascii=False)}
[뉴스] {json.dumps([h.get('title') for h in headlines[:15]], ensure_ascii=False)}

결과 데이터는 반드시 JSON 배열로 출력:
[ {{ "topic": "제목", "reason": "이유", "strength": 점수, "related_keywords": [], "anomaly_type": "SPEED|CORRELATION|NEWS_MISMATCH" }} ]
"""
        try:
            # GeminiClient.call_json_controlled 사용 (v1.0 Control Layer)
            results = self.gemini.call_json_controlled(prompt, agent="DETECTOR")
            if not results:
                # 직접 호출 후 로컬 추출 시도 (Fallback)
                raw_text = self.gemini.call(prompt)
                results = self.extract_json(raw_text)
            
            return results if isinstance(results, list) else []
        except: return []

    def detect_anomalies(self, data_summary: str, candidates: list) -> list:
        """AI가 자유롭게 이상징후를 찾는 핵심 함수"""
        if not data_summary or len(data_summary.strip()) < 50:
            return []

        system_prompt = """
        You are a JSON-only response system.
        NEVER output explanations, comments, or natural language.
        ALWAYS respond with valid JSON only.
        If you cannot generate valid JSON, respond with: {"error": "parse_failed"}
        """

        prompt = f"""{system_prompt}
너는 경제사냥꾼의 탐지 엔진이다. 아래 데이터를 보고 가장 이상한 징후 3개를 찾아라.
[데이터 요약]
{data_summary}
[후보]
{candidates}

출력 규칙 (JSON):
[
  {{
    "topic": "제목",
    "anomaly_type": "SPEED|CORRELATION|NEWS_MISMATCH|WHY_NOW",
    "why_anomalous": "데이터 근거",
    "why_now": "오늘인 결정적 이유",
    "key_indicators": ["지표1"],
    "strength": 0.0~10.0
  }}
]
"""
        try:
            results = self.gemini.call_json_controlled(prompt, agent="DETECTOR")
            if not results:
                raw_text = self.gemini.call(prompt, max_tokens=1500)
                results = self.extract_json(raw_text)
            return results if isinstance(results, list) else []
        except: return []

    def detect_correlation_anomalies(self, all_data: dict) -> list:
        """통계적 상관관계 붕괴 및 모순 패턴 탐지 (지시서 #054)"""
        market_stats = all_data.get("market", {}).get("data", {}).get("multi_period_stats", {})
        cot_data = all_data.get("cot", {})
        sentiment_data = all_data.get("sentiment", {})
        anomalies = []

        if not market_stats: return []

        get_z = lambda k: market_stats.get(k, {}).get("z_score_20d", 0.0) or 0.0
        sp500_z = get_z("sp500")
        vix_z = get_z("vix")
        dxy_z = get_z("dxy")
        us10y_z = get_z("us10y")
        wti_z = get_z("wti_oil")

        # 패턴 1: Rally in Fear
        if sp500_z > 1.0 and vix_z > 0.5:
            anomalies.append({
                "topic": "S&P500 신고가 속 VIX 동반 상승 (Rally in Fear)",
                "strength": 8.8,
                "anomaly_type": "CORRELATION",
                "why_anomalous": f"지수 Z-score {sp500_z:.2f} 상승 중 VIX Z-score {vix_z:.2f} 동반 상승",
                "why_now": "가장 낙관적인 시점에 보험(Hedge) 수요가 폭증하는 모순",
                "key_indicators": ["sp500", "vix"]
            })

        # 패턴 2: Price-Position Mismatch
        sp500_cot = next((s for s in cot_data.get("smart_money_signals", []) if s.get("asset") == "S&P500"), None)
        if sp500_z > 1.0 and (sp500_cot and sp500_cot.get("signal_label") in ["FLIP", "STRONG_SHORT"]):
            anomalies.append({
                "topic": "S&P500 독주와 헤지펀드의 하방 베팅",
                "strength": 9.2,
                "anomaly_type": "CORRELATION",
                "why_anomalous": f"지수 신고가 경신 중 헤지펀드 포지션은 {sp500_cot.get('signal_label')} 발생",
                "why_now": "스마트머니가 현재의 가격 상승을 추세 전환의 기회로 이용",
                "key_indicators": ["sp500", "cot"]
            })

        # 패턴 3: Safe Haven Exit
        if us10y_z < -1.0 and dxy_z < -1.0:
            anomalies.append({
                "topic": "안전자산 동반 이탈과 유동성 재배치",
                "strength": 8.5,
                "anomaly_type": "CORRELATION",
                "why_anomalous": f"국채금리 Z-score {us10y_z:.2f} 및 달러 Z-score {dxy_z:.2f} 동시 하락",
                "why_now": "시장 자금이 안전자산을 버리고 위험 자산으로 이동 중",
                "key_indicators": ["us10y", "dxy"]
            })

        # 패턴 4: Deflationary Drop
        if wti_z < -1.5 and dxy_z < -0.5:
             anomalies.append({
                "topic": "달러 약세에도 불구하고 유가 급락 (비상관적 하락)",
                "strength": 8.7,
                "anomaly_type": "CORRELATION",
                "why_anomalous": f"유가 Z-score {wti_z:.2f} 급락 중 달러 Z-score {dxy_z:.2f} 역시 하락",
                "why_now": "통상적인 달러 반비례 관계가 깨짐. 이는 심각한 수요 둔화 시그널",
                "key_indicators": ["wti_oil", "dxy"]
            })

        return anomalies

    def select_best(self, anomalies: list, all_data: dict) -> tuple:
        """가장 강한 이상징후 1개 선정 및 뉴스 트리거 결합 (v7.2)"""
        if not anomalies: anomalies = []
        corr_anomalies = self.detect_correlation_anomalies(all_data)
        
        market_data = all_data.get("market", {}).get("data", {})
        sentiment_data = all_data.get("sentiment", {})
        mismatch = self._detect_news_mismatch(market_data, sentiment_data)
        
        # 1. 모든 후보군 통합
        all_candidates = anomalies + corr_anomalies
        if mismatch:
            all_candidates.append(mismatch)

        # [EXTENSION] 모든 후보군 통합 후 엔리치먼트 레이어 적용 (지시서 #070)
        all_candidates = self.enricher.enrich_candidates(all_candidates, all_data)

        # [EXTENSION] Flow Overlay 적용 (지시서 #070) — 자금 흐름 기반 검증
        overlay = FlowOverlay(self.base_dir)
        all_candidates = [overlay.apply(a, all_data) for a in all_candidates]

        # 2. 전역 뉴스 트리거 결합 (Task 2)
        for a in all_candidates:
            if not a.get("news_trigger"): # 이미 mismatch 등에서 설정된 경우 제외
                trigger = self._find_news_trigger(a, sentiment_data)
                if trigger:
                    a["news_trigger"] = trigger
                    # why_now 보강: 기존 내용 + 뉴스 트리거
                    current_why = a.get("why_now", "")
                    if "뉴스 트리거:" not in current_why:
                        a["why_now"] = f"{current_why}. 뉴스 트리거: {trigger}"
                    
                    # [EXTENSION] extended_strength 로직으로 기존 strength 보강
                    base_str = a.get("strength", 0)
                    a["strength"] = min(10.0, base_str + 0.5)
                    if "extended_strength" in a:
                        a["extended_strength"] = min(10.0, a["extended_strength"] + 0.5)

        selected = None

        # 우선순위 0: NEWS_MISMATCH
        mismatch_found = next((a for a in all_candidates if a.get("anomaly_type") == "NEWS_MISMATCH"), None)
        if mismatch_found:
            print(f"  🔄 [Priority 0] NEWS_MISMATCH 선정: {mismatch_found['topic']}")
            selected = mismatch_found
            selected["source"] = "MISMATCH_ENGINE"
        
        # 우선순위 1: 컨센서스 서프라이즈 (Fallback)
        elif not selected:
            consensus_data = all_data.get("consensus", {})
            major = [s for s in consensus_data.get("major_surprises", []) if abs(s.get("surprise_pct", 0)) > 5.0]
            if major:
                best_c = sorted(major, key=lambda x: abs(x.get("surprise_pct", 0)), reverse=True)[0]
                selected = {
                    "topic": f"{best_c['event']} 서프라이즈 ({best_c['surprise_pct']:+.1f}%)",
                    "strength": 8.5,
                    "anomaly_type": "WHY_NOW",
                    "why_anomalous": f"예측치 대비 괴리율 {best_c['surprise_pct']}% 발생",
                    "why_now": "오늘 발표된 지표가 시장의 기대를 정면으로 위반함",
                    "key_indicators": ["consensus", best_c['event']],
                    "source": "CONSENSUS_FALLBACK"
                }

        # 우선순위 2: Correlation 모순
        if not selected:
            corrs = [a for a in all_candidates if a.get("anomaly_type") == "CORRELATION"]
            if corrs:
                selected = sorted(corrs, key=lambda x: x.get("extended_strength", x.get("strength", 0)), reverse=True)[0]
                selected["source"] = "CORRELATION_ENGINE"

        # 우선순위 3: LLM 탐지 결과
        if not selected:
            llm_anomalies = [a for a in anomalies if not self._is_absolute_value_topic(a.get("topic", ""), a)]
            if llm_anomalies:
                selected = sorted(llm_anomalies, key=lambda x: x.get("extended_strength", x.get("strength", 0)), reverse=True)[0]
                selected["source"] = "LLM"

        # Fallback: Z-score
        if not selected:
            stats = market_data.get("multi_period_stats", {})
            if stats:
                best_key = max(stats, key=lambda k: abs(stats[k].get("z_score_20d", 0) or 0))
                bz = stats[best_key].get("z_score_20d", 0) or 0.0
                selected = {
                    "topic": f"{best_key} 통계적 이탈 (Z-score {bz:.2f})",
                    "strength": 8.0,
                    "anomaly_type": "SPEED",
                    "why_anomalous": f"Z-score {bz:.2f} 기록",
                    "why_now": "최근 변동성이 통계적 임계치를 돌파",
                    "key_indicators": [best_key],
                    "source": "ZSCORE_FALLBACK"
                }

        if selected:
            # 최종 선정 항목에 대해서도 뉴스 트리거 재확인 (Z-score fallback 등 대응)
            if not selected.get("news_trigger"):
                trigger = self._find_news_trigger(selected, sentiment_data)
                if trigger:
                    selected["news_trigger"] = trigger
                    if "뉴스 트리거:" not in selected.get("why_now", ""):
                        selected["why_now"] = f"{selected.get('why_now', '')}. 뉴스 트리거: {trigger}"

            selected["selected"] = True
            selected["content_type"] = "롱폼" if selected.get("strength", 0) >= 8.5 else "쇼츠"
            selected["date"] = self.today
        
        return selected, all_candidates

    def _find_news_trigger(self, signal: dict, sentiment_data: dict) -> str:
        """관련 뉴스 헤드라인 매칭 (지시서 #056)"""
        topic = signal.get("topic", "").lower()
        headlines = sentiment_data.get("data", {}).get("news_headlines", [])
        
        TOPIC_KEYWORDS = {
            "wti": ["호르무즈", "hormuz", "유가", "oil", "wti", "opec", "원유", "석유"],
            "gold": ["금", "gold", "귀금속", "안전자산"],
            "sp500": ["deepseek", "딥시크", "s&p", "나스닥", "nasdaq", "주가", "증시", "기술주", "ai"],
            "dxy": ["달러", "dollar", "dxy", "환율"],
            "kr_": ["코스피", "한국", "kospi", "원화"],
        }
        
        # 1. 토픽과 관련된 키워드 셋 찾기
        matched_keywords = []
        for key, keywords in TOPIC_KEYWORDS.items():
            if any(kw.lower() in topic for kw in keywords):
                matched_keywords.extend(keywords)
        
        if not matched_keywords:
            # 토픽 자체의 단어들로 시도
            matched_keywords = [w for w in topic.split() if len(w) >= 2]

        # 2. 헤드라인 매칭 (우선순위: 호르무즈/DeepSeek 등 강한 키워드 우선)
        priority_keywords = ["호르무즈", "hormuz", "deepseek", "딥시크", "폭락", "급락", "rout", "crash"]
        
        best_match = None
        best_score = -1
        
        for h in headlines:
            title = h.get("title", "").lower()
            summary = h.get("summary", "").lower()
            
            score = 0
            matches = 0
            for kw in matched_keywords:
                kw_lower = kw.lower()
                # 제목에 있으면 3배 가중치, 요약에 있으면 1배
                title_match = kw_lower in title
                summary_match = kw_lower in summary
                
                if title_match or summary_match:
                    matches += 1
                    weight = 10 if kw_lower in priority_keywords else 1
                    if title_match:
                        score += weight * 3
                    if summary_match:
                        score += weight
            
            if matches > 0 and score > best_score:
                best_match = h.get("title")
                best_score = score
                
        return best_match or ""

    def _detect_news_mismatch(self, market_data: dict, sentiment_data: dict) -> dict:
        """뉴스 톤 vs 지표 방향 모순 탐지 (지시서 #056)"""
        headlines = sentiment_data.get("data", {}).get("news_headlines", [])
        headline_text = " ".join([h.get("title", "") + h.get("summary", "") for h in headlines]).lower()
        
        negative_keywords = ["sink", "rout", "crash", "fear", "폭락", "급락", "위기", "봉쇄", "전쟁", "침체", "역성장"]
        positive_keywords = ["rally", "surge", "boom", "strong", "상승", "호황", "강세", "회복"]

        sp500_z = market_data.get("multi_period_stats", {}).get("sp500", {}).get("z_score_20d", 0) or 0
        nasdaq_z = market_data.get("multi_period_stats", {}).get("nasdaq", {}).get("z_score_20d", 0) or 0
        
        # 사례 1: 뉴스 악재 속 지수 상승 (S&P500 기준)
        if any(kw in headline_text for kw in negative_keywords) and sp500_z > 1.0:
            trigger = next((h.get("title") for h in headlines if any(kw in (h.get("title","") + h.get("summary","")).lower() for kw in negative_keywords)), "")
            return {
                "topic": "뉴스 악재 속 지수 상승 (Price-News 모순)",
                "anomaly_type": "NEWS_MISMATCH",
                "strength": 9.2,
                "why_anomalous": f"뉴스 톤은 부정적(DeepSeek 등)이나 SP500 Z-score {sp500_z:.2f}로 강한 상승 중",
                "why_now": "악재를 압도하는 수급 또는 선반영 인식 확산 (뉴스 트리거 확인됨)",
                "news_trigger": trigger,
                "key_indicators": ["sp500", "sentiment"]
            }
        
        # 사례 2: 뉴스 호재 속 지수 급락 (추가 가능)
        if any(kw in headline_text for kw in positive_keywords) and sp500_z < -1.0:
             return {
                "topic": "뉴스 호재 속 지수 급락 (News-Price 모순)",
                "anomaly_type": "NEWS_MISMATCH",
                "strength": 8.8,
                "why_anomalous": f"뉴스는 긍정적이나 지수는 Z-score {sp500_z:.2f}로 하락",
                "why_now": "호재 소멸 또는 Sell-on-news 심리 작동",
                "key_indicators": ["sp500", "sentiment"]
            }

        return {}

    def _is_absolute_value_topic(self, topic: str, anomaly: dict) -> bool:
        """단순 수치 돌파형 토픽 필터링"""
        forbidden = ["돌파", "도달", "최고가", "최저가"]
        return any(f in topic for f in forbidden) and anomaly.get("anomaly_type") == "SPEED"

    def save_results(self, candidates: list, anomalies: list, selected: dict):
        """결과 저장"""
        candidates_data = {"date": self.today, "total_candidates": len(anomalies), "candidates": anomalies}
        (self.signal_dir / "candidates.json").write_text(json.dumps(candidates_data, ensure_ascii=False, indent=2))
        if selected:
            (self.signal_dir / "today_signal.json").write_text(json.dumps(selected, ensure_ascii=False, indent=2))
            (self.signal_dir / "anomaly_log.json").write_text(json.dumps(anomalies, ensure_ascii=False, indent=2))

    def run(self, collector_result=None):
        print(f"\n🔍 AGENT-03 DETECTOR v7.1 시작 [{self.today}]")
        all_data = self.load_all_data()
        if not all_data: return {}
        candidates = self.discover_autonomous_narratives(all_data)
        summary = self.build_data_summary(all_data)
        anomalies = self.detect_anomalies(summary, candidates)
        selected, total_anomalies = self.select_best(anomalies, all_data)
        if selected:
            self.save_results(candidates, total_anomalies, selected)
            print(f"  ✅ 최종 선정: {selected['topic']}")
        return {"selected": selected, "candidates": total_anomalies}

if __name__ == "__main__":
    DetectorAgent().run()
