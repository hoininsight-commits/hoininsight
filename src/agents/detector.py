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

        return False

    def detect_correlation_anomalies(self, all_data: dict) -> list:
        """통계적 상관관계 붕괴 및 모순 패턴 탐지 (지시서 #054)"""
        market_stats = all_data.get("market", {}).get("data", {}).get("multi_period_stats", {})
        cot_data = all_data.get("cot", {})
        anomalies = []

        if not market_stats: return []

        # 유틸리티: Z-score 가져오기
        get_z = lambda k: market_stats.get(k, {}).get("z_score_20d", 0.0) or 0.0

        sp500_z = get_z("sp500")
        vix_z = get_z("vix")
        dxy_z = get_z("dxy")
        us10y_z = get_z("us10y")
        wti_z = get_z("wti_oil")

        # 패턴 1: Rally in Fear (지수 상승 + 공포지수 상승)
        if sp500_z > 1.0 and vix_z > 0.5:
            anomalies.append({
                "topic": "S&P500 신고가 속 VIX 동반 상승 (Rally in Fear)",
                "strength": 8.8,
                "anomaly_type": "CORRELATION",
                "why_anomalous": f"지수 Z-score {sp500_z:.2f} 상승 중 VIX Z-score {vix_z:.2f} 동반 상승은 시장의 극심한 경계심을 시사",
                "why_now": "가장 낙관적인 시점에 보험(Hedge) 수요가 폭증하는 모순 발생",
                "key_indicators": ["sp500", "vix"],
                "pattern": "rally_in_fear"
            })

        # 패턴 2: Price-Position Mismatch (지수 상승 + 헤지펀드 숏 급증)
        sp500_cot = next((s for s in cot_data.get("smart_money_signals", []) if s.get("asset") == "S&P500"), None)
        if sp500_z > 1.0 and (sp500_cot and sp500_cot.get("signal_label") in ["FLIP", "STRONG_SHORT"]):
            anomalies.append({
                "topic": "S&P500 독주와 헤지펀드의 하방 베팅 ( 수급 Mismatch)",
                "strength": 9.2,
                "anomaly_type": "CORRELATION",
                "why_anomalous": f"지수 Z-score {sp500_z:.2f} 신고가 경신 중 헤지펀드 포지션은 {sp500_cot.get('signal_label')} 발생",
                "why_now": "스마트머니가 현재의 가격 상승을 추세 전환의 기회로 이용하고 있음",
                "key_indicators": ["sp500", "cot"],
                "pattern": "price_pos_mismatch"
            })

        # 패턴 3: Safe Haven Exit (금리 하락 + 달러 하락 동시 방전)
        if us10y_z < -1.0 and dxy_z < -1.0:
            anomalies.append({
                "topic": "안전자산 동반 이탈과 유동성 재배치 (Safe Haven Exit)",
                "strength": 8.5,
                "anomaly_type": "CORRELATION",
                "why_anomalous": f"국채금리 Z-score {us10y_z:.2f} 및 달러 Z-score {dxy_z:.2f} 동시 하락",
                "why_now": "시장 자금이 안전자산을 버리고 위험 자산 또는 실물 자산으로 급격히 이동 중",
                "key_indicators": ["us10y", "dxy"],
                "pattern": "safe_haven_exit"
            })

        # 패턴 4: Deflationary Drop (유가 급락 + 달러 약세)
        if wti_z < -1.5 and dxy_z < -0.5:
             anomalies.append({
                "topic": "달러 약세에도 불구하고 유가 급락 (비상관적 하락)",
                "strength": 8.7,
                "anomaly_type": "CORRELATION",
                "why_anomalous": f"유가 Z-score {wti_z:.2f} 급락 중 달러 Z-score {dxy_z:.2f} 역시 하락",
                "why_now": "통상적인 달러 반비례 관계가 깨짐. 이는 심각한 수요 둔화 또는 공급 과잉 시그널",
                "key_indicators": ["wti_oil", "dxy"],
                "pattern": "non_correlated_drop"
            })

        # 패턴 5: Bad News Ignore (뉴스 악재 + 지수 견조) - 간략화된 로직
        # (현실적으로는 LLM 분석 결과와 결합 필요하므로 여기서는 생략하거나 단순화)

        return anomalies

    def select_best(self, anomalies: list, all_data: dict) -> dict:
        """가장 강한 이상징후 1개 선정 (Consensus > Correlation > Z-score 우선순위)"""
        if not anomalies: anomalies = []

        # 1. 절대값 토픽 필터링
        filtered = [a for a in anomalies if not self._is_absolute_value_topic(a.get("topic", ""), a)]

        # 1.5. 통계적 모순(Correlation) 패턴 추출
        corr_anomalies = self.detect_correlation_anomalies(all_data)
        
        # 우선순위 1: 컨센서스 서프라이즈
        consensus_data = all_data.get("consensus", {})
        major = [s for s in consensus_data.get("major_surprises", []) if abs(s.get("surprise_pct", 0)) > 5.0]
        
        if major:
            best = sorted(major, key=lambda x: abs(x.get("surprise_pct", 0)), reverse=True)[0]
            print(f"  🔄 [Priority 1] 컨센서스 서프라이즈 선정: {best['event']}")
            selected = {
                "topic": f"{best['event']} 서프라이즈 ({best['surprise_pct']:+.1f}%)",
                "strength": 9.0 if abs(best['surprise_pct']) > 15 else 8.5,
                "anomaly_type": "WHY_NOW",
                "why_anomalous": f"예측치 대비 괴리율 {best['surprise_pct']}% 발생",
                "why_now": "오늘 발표된 지표가 시장의 기대를 정면으로 위반함",
                "key_indicators": ["consensus", best['event']],
                "source": "CONSENSUS_FALLBACK"
            }
        
        # 우선순위 2: 통계적 모순 (Correlation Anomaly)
        elif corr_anomalies:
            best = sorted(corr_anomalies, key=lambda x: x.get("strength", 0), reverse=True)[0]
            print(f"  🔄 [Priority 2] Correlation 모순 패턴 선정: {best['topic']}")
            selected = best
            selected["source"] = "CORRELATION_ENGINE"

        # 우선순위 3: LLM 탐지 결과 (만약 존재한다면)
        elif filtered:
            selected = sorted(filtered, key=lambda x: x.get("strength", 0), reverse=True)[0]
            selected["source"] = "LLM"
            print(f"  🔄 [Priority 3] LLM 탐지 결과 선정: {selected['topic']}")

        else:
            # 4. Fallback (Z-score 등)
            cot_data = all_data.get("cot", {})
            top_cot = cot_data.get("top_signal")
            
            if top_cot and top_cot.get("signal_label") == "FLIP":
                print(f"  🔄 [Fallback] COT FLIP 선정: {top_cot['asset']}")
                selected = {
                    "topic": f"스마트머니 {top_cot['asset']} {top_cot['signal_label']} 포착",
                    "strength": 8.5,
                    "anomaly_type": "WHY_NOW",
                    "why_anomalous": top_cot.get("description"),
                    "why_now": "헤지펀드 포지션의 통계적 유의미한 급변 감지",
                    "key_indicators": ["cot", top_cot['asset']],
                    "source": "COT_FALLBACK"
                }
            else:
                # 마지막 보루: Z-score
                market_data = all_data.get("market", {}).get("data", {})
                stats = market_data.get("multi_period_stats", {})
                best_key, bz = None, 0.0
                if stats:
                    best_key = max(stats, key=lambda k: abs(stats[k].get("z_score_20d", 0) or 0))
                    bz = stats[best_key].get("z_score_20d", 0) or 0.0

                if abs(bz) >= 1.5:
                    print(f"  🔄 [Fallback] Z-score 선정: {best_key} (Z={bz:.2f})")
                    selected = {
                        "topic": f"{best_key} 통계적 이탈 (Z-score {bz:.2f})",
                        "strength": 8.0,
                        "anomaly_type": "SPEED",
                        "why_anomalous": f"{best_key} Z-score={bz:.2f}, 20일 평균 대비 {abs(bz):.1f}σ 이탈",
                        "why_now": f"{best_key}의 최근 변동성이 통계적 임계치를 돌파",
                        "key_indicators": [best_key],
                        "source": "ZSCORE_FALLBACK"
                    }
                else:
                    return None

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
