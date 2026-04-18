import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
from src.core.filters import SignalFilters
from src.core.gemini_client import GeminiClient

class DetectorAgent:
    """이상징후 탐지자 — 숫자와 뉴스 맥락을 결합하여 시장의 신호를 포착함 (v7.0 Intelligent Merge)"""

    def __init__(self):
        self.base_dir = Path(os.getenv("HOIN_BASE_DIR", Path(__file__).resolve().parents[2]))
        self.today = datetime.now().strftime("%Y%m%d")
        self.raw_dir = self.base_dir / f"data/raw/{self.today}"
        self.signal_dir = self.base_dir / f"data/signals/{self.today}"
        self.signal_dir.mkdir(parents=True, exist_ok=True)
        self.filters = SignalFilters()
        self.gemini = GeminiClient()

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
        dart   = all_data.get("dart", {}).get("data", {})

        # 지표별 다중기간 요약 생성
        stats_lines = []
        for key, s in stats.items():
            if not s: continue
            line = (
                f"{key}: 현재={s.get('current')} "
                f"| 5일변화={s.get('chg_5d')}% "
                f"| 20일변화={s.get('chg_20d')}% "
                f"| 20일Z-score={s.get('z_score_20d')} "
                f"| 20일평균={s.get('avg_20d')} "
                f"| 60일평균={s.get('avg_60d')}"
            )
            stats_lines.append(line)

        # FRED 핵심 지표
        fred_lines = []
        if fred:
            fred_lines = [
                f"미국기준금리: {fred.get('fed_rate')}%",
                f"10Y-2Y스프레드: {fred.get('spread_10y2y')}",
                f"하이일드스프레드: {fred.get('hy_spread')}",
                f"금융스트레스지수: {fred.get('financial_stress')}",
                f"MMF잔고: {fred.get('mmf_balance')}억달러",
            ]

        # ECOS 한국 지표
        ecos_lines = []
        if ecos:
            ecos_lines = [
                f"한국기준금리: {ecos.get('kr_base_rate')}%",
                f"한국CPI: {ecos.get('kr_cpi')}",
                f"한국M2: {ecos.get('kr_m2')}",
            ]

        # 뉴스 헤드라인
        news_lines = [f"[{h.get('source','')}] {h.get('title','')}" for h in headlines[:15]]

        # COT 스마트머니 섹션
        cot_data = all_data.get("cot", {})
        cot_signals = cot_data.get("smart_money_signals", [])
        cot_lines = []
        if cot_signals:
            for s in cot_signals:
                cot_lines.append(f"[{s.get('asset')}] {s.get('signal_label')}: {s.get('description')}")

        # 컨센서스 섹션

        consensus_data = all_data.get("consensus", {})
        surprises = consensus_data.get("major_surprises", [])
        consensus_lines = []
        if surprises:
            for s in surprises:
                direction = "📈 BEAT" if s.get("surprise_direction") == "BEAT" else "📉 MISS"
                consensus_lines.append(
                    f"{direction} {s.get('event')}: "
                    f"예산={s.get('previous')} 실제={s.get('actual')} "
                    f"괴리={s.get('surprise_pct')}%"
                )

        summary = f"""
=== 시장 지표 (다중기간 통계) ===
{chr(10).join(stats_lines) if stats_lines else "통계 데이터 없음"}

=== 오늘 경제지표 서프라이즈 ===
{chr(10).join(consensus_lines) if consensus_lines else "서프라이즈 없음"}

=== 거시 지표 (FRED/ECOS) ===
{fred_lines}
{ecos_lines}

=== 오늘 뉴스 헤드라인 ===
{chr(10).join(news_lines) if news_lines else "없음"}

=== 상업용/비상업용 투기 세력 (COT) ===
{chr(10).join(cot_lines) if cot_lines else "특이 신호 없음"}
"""
        return summary

    def discover_autonomous_narratives(self, all_data: dict) -> list:
        """AI 자율 담론 사냥: 시장의 모순(Anomaly)과 기대 충돌을 스스로 포착 (v7.0)"""
        sentiment = all_data.get("sentiment", {}).get("data", {})
        headlines = sentiment.get("news_headlines", [])
        market = all_data.get("market", {}).get("data", {})
        history = all_data.get("history_90d", {})
        
        if not headlines or not self.gemini: return []

        prompt = f"""
너는 HOIN Insight의 '경제사냥꾼' 엔진이다. 지표와 뉴스를 분석해 오늘 시장에서 가장 '이상한(Anomaly)' 서사 3가지를 선정해라.
[오늘 지표] {market}
[90일 평균/최고점] {history}
[뉴스] {json.dumps([h.get('title') for h in headlines[:15]], ensure_ascii=False)}

결과는 반드시 JSON 배열로 출력:
[ {{ "topic": "제목", "reason": "이유", "strength": 점수, "related_keywords": [], "anomaly_type": "SPEED|CORRELATION|NEWS_MISMATCH" }} ]
"""
        try:
            results = self.gemini.call_json(prompt)
            return results if isinstance(results, list) else []
        except: return []

    def detect_anomalies(self, data_summary: str, candidates: list) -> list:
        """AI가 자유롭게 이상징후를 찾는 핵심 함수"""
        if not data_summary or len(data_summary.strip()) < 100:
            print("  ⚠️ 요약 데이터가 너무 부실합니다. 분석을 건너뜁니다.")
            return []

        print("  🧠 AI 이상징후 탐지 중... (Gemini 응답 대기, 최대 30초)")

        prompt = f"""
너는 경제사냥꾼의 탐지 엔진이다. 아래 데이터를 보고 가장 이상한 징후 3개를 찾아라.
이미 추출된 후보들도 참고하여 최종적인 상위 3개를 결정해라.

[데이터 요약]
{data_summary}

[후보 서사]
{candidates}

[탐지 관점]
1순위: 컨센서스 서프라이즈 (SHOCK/SURPRISE)
2순위: 지표 간 모순 (CORRELATION 붕괴)
3순위: Z-score 이상 이탈 (SPEED)

[출력 규칙]
- 순수 JSON 배열만 출력.
[
  {{
    "topic": "제목",
    "anomaly_type": "SPEED|CORRELATION|NEWS_MISMATCH|WHY_NOW",
    "why_anomalous": "데이터 근거",
    "why_now": "오늘인 결정적 이유",
    "key_indicators": ["지표1"],
    "strength": 0.0~10.0,
    "signal_type": "Type1~Type9"
  }}
]
"""
        try:
            results = self.gemini.call_json(prompt, max_tokens=1500)
            if not isinstance(results, list): return []
            print(f"  📡 AI 이상징후 탐지 완료: {len(results)}건")
            return results
        except Exception as e:
            print(f"  ❌ AI 탐지 실패: {e}")
            return []

    def _is_absolute_value_topic(self, topic: str, anomaly: dict) -> bool:
        """절대값 기반 토픽인지 감지 (v4.0 필터링)"""
        import re
        topic_lower = topic.lower()
        # 환율/유가 절대값 언급 패턴
        if re.search(r'환율\s*\d{3,4}원', topic) or re.search(r'유가\s*\$\d+', topic):
            why = anomaly.get("why_anomalous", "").lower() + anomaly.get("why_now", "").lower()
            if "z-score" not in why and "z_score" not in why and "변화율" not in why and "괴리" not in why:
                return True
        return False

    def select_best(self, anomalies: list, all_data: dict) -> dict:
        """가장 강한 이상징후 1개 선정 (3단계 Fallback 로직 적용)"""
        if not anomalies: anomalies = []

        # 1. 절대값 토픽 필터링
        filtered = [a for a in anomalies if not self._is_absolute_value_topic(a.get("topic", ""), a)]

        if filtered:
            selected = sorted(filtered, key=lambda x: x.get("strength", 0), reverse=True)[0]
            selected["source"] = "LLM"
        else:
            # 2. Fallback 단계
            # 1차: 컨센서스 서프라이즈
            consensus_data = all_data.get("consensus", {})
            major = consensus_data.get("major_surprises", [])
            
            # 1.5차: COT 스마트머니 플립 (헤지펀드 포지션 급변)
            cot_data = all_data.get("cot", {})
            top_cot = cot_data.get("top_signal")
            
            if major:

                best = sorted(major, key=lambda x: abs(x.get("surprise_pct", 0)), reverse=True)[0]
                print(f"  🔄 컨센서스 Fallback 적용: {best['event']}")
                selected = {
                    "topic": f"{best['event']} 서프라이즈 ({best['surprise_pct']:+.1f}%)",
                    "strength": 8.5,
                    "anomaly_type": "WHY_NOW",
                    "why_anomalous": f"괴리율 {best['surprise_pct']}%",
                    "why_now": "최근 12개월 평균값에서 크게 이탈",
                    "key_indicators": ["consensus", best['event']],
                    "source": "CONSENSUS_FALLBACK"
                }
            elif top_cot and top_cot.get("signal_label") in ["FLIP", "STRONG"]:
                print(f"  🔄 COT 스마트머니 Fallback 적용: {top_cot['asset']}")
                selected = {
                    "topic": f"스마트머니 {top_cot['asset']} {top_cot['signal_label']} 포착",
                    "strength": 8.5 if top_cot["signal_label"] == "FLIP" else 8.0,
                    "anomaly_type": "WHY_NOW",
                    "why_anomalous": top_cot.get("description"),
                    "why_now": "헤지펀드 포지션의 통계적 유의미한 급변 감지",
                    "key_indicators": ["cot", top_cot['asset']],
                    "source": "COT_FALLBACK"
                }
            else:

                # 2차: Z-score
                market_data = all_data.get("market", {}).get("data", {})
                stats = market_data.get("multi_period_stats", {})
                if stats:
                    best_key = max(stats, key=lambda k: abs(stats[k].get("z_score_20d", 0)) if stats[k].get("z_score_20d") else 0)
                    bz = stats[best_key].get("z_score_20d", 0)
                    if abs(bz) > 2.0:
                        print(f"  🔄 Z-score Fallback 적용: {best_key}")
                        selected = {
                            "topic": f"{best_key} 통계적 이탈 (Z-score {bz:.1f})",
                            "strength": 7.5,
                            "anomaly_type": "SPEED",
                            "key_indicators": [best_key],
                            "source": "ZSCORE_FALLBACK"
                        }
                    else: return None
                else: return None

        selected["selected"] = True
        selected["content_type"] = "롱폼" if selected.get("strength", 0) >= 8.5 else "쇼츠"
        selected["date"] = self.today
        return selected

    def save_results(self, candidates: list, anomalies: list, selected: dict):
        """결과 저장 (candidates.json, today_signal.json)"""
        candidates_data = {
            "date": self.today,
            "total_candidates": len(candidates) + len(anomalies),
            "candidates": anomalies
        }
        (self.signal_dir / "candidates.json").write_text(json.dumps(candidates_data, ensure_ascii=False, indent=2))

        if selected:
            (self.signal_dir / "today_signal.json").write_text(json.dumps(selected, ensure_ascii=False, indent=2))
            # anomaly_log (v5.0 하이브리드 로그)
            (self.signal_dir / "anomaly_log.json").write_text(json.dumps(anomalies, ensure_ascii=False, indent=2))

    def run(self, collector_result=None):
        print(f"\n🔍 AGENT-03 DETECTOR v7.0 시작 [{self.today}]")
        all_data = self.load_all_data()
        if not all_data: return {}

        # 1. 자율 서사 탐색 (v7.0)
        candidates = self.discover_autonomous_narratives(all_data)
        
        # 2. 데이터 요약 및 이상징후 탐지
        summary = self.build_data_summary(all_data)
        anomalies = self.detect_anomalies(summary, candidates)
        
        # 3. 최강 신호 선정 (3단계 Fallback 포함)
        selected = self.select_best(anomalies, all_data)
        
        if selected:
            print(f"\n  ✅ 최종 선정: {selected['topic']}")
            print(f"     강도: {selected['strength']} | 유형: {selected['content_type']}")
            self.save_results(candidates, anomalies, selected)
        
        return {"selected": selected}

if __name__ == "__main__":
    DetectorAgent().run()
