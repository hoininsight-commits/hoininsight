import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from src.core.filters import SignalFilters
from src.core.claude_client import ClaudeClient


class DetectorAgent:

    def __init__(self):
        self.today = datetime.now().strftime("%Y%m%d")
        self.raw_dir = Path(f"data/raw/{self.today}")
        self.signal_dir = Path(f"data/signals/{self.today}")
        self.signal_dir.mkdir(parents=True, exist_ok=True)
        self.history_path = Path("data/history/signal_log.json")
        self.filters = SignalFilters()
        self.claude = ClaudeClient()

    def load_all_data(self):
        all_data = {}
        for name in ["macro", "market", "sentiment"]:
            p = self.raw_dir / f"{name}.json"
            if p.exists():
                all_data[name] = json.loads(p.read_text())
        
        # 컨센서스 데이터 로드 추가
        p = self.raw_dir / "consensus.json"
        if p.exists():
            all_data["consensus"] = json.loads(p.read_text())
            print(f"  ✅ consensus.json 로드")
        
        return all_data

    def build_data_summary(self, all_data):
        """데이터 요약 생성 (LLM 전달용)"""
        market = all_data.get("market", {}).get("data", {})
        macro = all_data.get("macro", {}).get("data", {})
        sentiment = all_data.get("sentiment", {}).get("data", {})
        consensus = all_data.get("consensus", {})

        # 컨센서스 세션 추가
        surprises = consensus.get("major_surprises", [])
        consensus_lines = []
        if surprises:
            for s in surprises:
                direction = "📈 BEAT" if s.get("surprise_direction") == "BEAT" else "📉 MISS"
                consensus_lines.append(
                    f"{direction} {s.get('event')}: "
                    f"예상={s.get('forecast')} 실제={s.get('actual')} "
                    f"괴리={s.get('surprise')}%"
                )

        summary = f"""
=== 시장 지표 ===
- KOSPI: {market.get('kospi', 'N/A')} ({market.get('kospi_1d_change', '0')}% )
- 환율: {market.get('usd_krw', 'N/A')}원
- VIX: {market.get('vix', 'N/A')}
- WTI: ${market.get('wti_oil', 'N/A')}
- Fear & Greed: {market.get('fear_greed_index', 'N/A')}

=== 오늘 경제지표 서프라이즈 ===
{chr(10).join(consensus_lines) if consensus_lines else "서프라이즈 없음 또는 미발표"}

=== 뉴스 및 권위자 신호 ===
- 주요 헤드라인: {[h.get('title') for h in sentiment.get('news_headlines', [])[:3]]}
- 권위자 행동: {[s.get('action') for s in sentiment.get('authority_signals', [])]}
"""
        return summary

    def detect_anomalies(self, summary, candidates):
        """LLM 기반 신호 감지 (컨센서스 충격 우선)"""
        print("  Claude API 신호 감지 중...")
        
        candidates_text = json.dumps(candidates[:5], ensure_ascii=False)
        
        prompt = f"""
너는 HOIN Insight의 핵심 엔진인 DetectorAgent다. 
아래 수집된 데이터 요약과 후보 신호들을 분석해서 오늘 가장 중요한 'WHY NOW' 토픽을 하나 골라라.

[데이터 요약]
{summary}

[후보 신호 (시스템 계산)]
{candidates_text}

[토픽 선정 우선순위 — 반드시 이 순서를 따를 것]
1순위: 컨센서스 서프라이즈 (SHOCK/SURPRISE 등급)
- 프롬프트에 전달된 consensus 섹션의 major_surprises 확인
- surprise_pct 절대값이 큰 것부터 우선
- 예: "HY 스프레드가 12개월 평균 대비 117% 이상 급변"
- 이 신호가 있으면 반드시 상위 후보로 올릴 것

2순위: 지표 간 모순 (CORRELATION 붕괴)
- 원래 같이/반대로 가야 하는 지표가 반대 방향인 경우
- 예: 지정학 위기 뉴스(전쟁 등) + 유가 하락 = 강한 모순
- 반드시 수치 근거 제시

3순위: Z-score 이상 이탈 (SPEED 신호)
- Z-score > 2.0 또는 5일 변화율 급변
- 수치 근거 없으면 채택 불가

[절대 금지 패턴]
아래 패턴의 토픽은 생성하지 마라. WHY NOW를 데이터로 설명 못하면 토픽이 아니다.
- "환율 XXX원 돌파" 또는 "환율 XXX원 → 위기" (Z-score 2.0 미만 시 금지)
- "유가 $XX → 에너지 압박" (변화율 미미할 때 금지)
- "금리 XX% → 부담 가중" (절대값만 있는 토픽 금지)
- Z-score나 서프라이즈 수치 없이 뉴스 키워드만 있는 토픽

[WHY NOW 필수 조건]
모든 토픽은 "왜 어제가 아니라 오늘인가?"에 대해 데이터(%, z-score)로 답할 수 있어야 한다.

결과는 반드시 아래 JSON 구조의 리스트(배열)로 상위 3개까지 출력해라:
[
  {{
    "topic": "최종 선정된 토픽 명칭 (수치 포함)",
    "strength": 0.0~10.0 점수,
    "content_type": "롱폼" 또는 "쇼츠",
    "filters_hit": ["필터 명칭들"],
    "data_evidence": {{ "관련_지표_명": "현재값(변화율/z-score)" }},
    "why_now": "왜 오늘 처음 나타난 이상 수준인지에 대한 데이터 근거",
    "related_keywords": ["키워드1", "키워드2"],
    "selected": true
  }}
]
"""
        result = self.claude.call_json(prompt)
        return result

    def build_candidates(self, raw_data):
        """기존 휴리스틱 기반 후보 생성 (LLM 참고용 보조 지표)"""
        market = raw_data.get("market", {}).get("data", {})
        candidates = []

        # 환율 이슈
        usd_krw = market.get("usd_krw", 0)
        if usd_krw and usd_krw > 1400:
            candidates.append({
                "topic": f"원달러 환율 {usd_krw:.0f}원 돌파",
                "strength": 7.0,
                "filters_hit": ["필터1_역사적임계값"]
            })

        # VIX 공포
        vix = market.get("vix", 0)
        if vix and vix > 20:
            candidates.append({
                "topic": f"VIX {vix:.1f} 공포 구간",
                "strength": 6.5,
                "filters_hit": ["필터1_역사적임계값"]
            })

        # KOSPI 급락
        kospi_chg = market.get("kospi_1d_change", 0)
        if kospi_chg and kospi_chg < -2.0:
            candidates.append({
                "topic": f"KOSPI {kospi_chg:.1f}% 급락",
                "strength": 8.0,
                "filters_hit": ["필터1_역사적임계값", "필터4_시의성"]
            })

        return candidates

    def _is_absolute_value_topic(self, topic: str, anomaly: dict) -> bool:
        """
        절대값 기반 토픽인지 감지
        Z-score 근거 없이 환율/유가 절대값만 언급하는 토픽 필터링
        """
        import re
        topic_lower = topic.lower()
        why = anomaly.get("why_now", "").lower()

        # 환율 절대값 패턴 (소수점 포함 대응)
        krw_pattern = re.search(r'환율\s*[\d,.]+원', topic)
        if krw_pattern:
            # Z-score(2.0 이상)나 변화율 근거가 명확히 없으면 필터링
            has_zscore = "z-score" in why or "z_score" in why
            has_pct = "%" in why or "변화율" in why
            
            # 지시서 #022: Z-score 2.0 미만 근거면 절대값 토픽으로 간주
            is_weak_z = False
            z_val_match = re.search(r'z[_-]score\s*([0-9.]+)', why)
            if z_val_match:
                try:
                    if float(z_val_match.group(1)) < 2.0:
                        is_weak_z = True
                except: pass

            if (not has_zscore and not has_pct) or is_weak_z:
                return True

        # 유가 절대값 패턴 (단순 수준 언급)
        wti_pattern = re.search(r'유가\s*\$\d+', topic)
        if wti_pattern:
            if "변화율" not in why and "%" not in why and "z-score" not in why:
                return True
            return True

        return False

    def _build_consensus_fallback_topic(self, consensus_data: dict) -> Optional[dict]:
        """
        consensus.json에서 가장 강한 서프라이즈로 토픽 자동 생성
        """
        if not consensus_data:
            return None

        major_surprises = consensus_data.get("major_surprises", [])
        top_surprise = consensus_data.get("top_surprise")

        # top_surprise 또는 major_surprises 중 가장 강한 것 선택
        candidates = []
        if top_surprise:
            candidates.append(top_surprise)
        candidates.extend(major_surprises)

        if not candidates:
            return None

        # surprise_pct 절대값 기준 정렬
        candidates.sort(
            key=lambda x: abs(x.get("surprise_pct", 0) or 0),
            reverse=True
        )
        best = candidates[0]

        surprise_pct = best.get("surprise_pct", 0)
        event_name = best.get("event", "알 수 없는 지표")
        actual = best.get("actual")
        previous = best.get("previous")
        direction = "급등" if (best.get("change", 0) or 0) > 0 else "급락"

        topic = f"{event_name} 12개월 평균 대비 {abs(surprise_pct):.0f}% {direction}"

        return {
            "topic": topic,
            "strength": min(9.5, 6.0 + abs(surprise_pct) / 100),
            "content_type": "롱폼",
            "source": "CONSENSUS_FALLBACK",
            "filters_hit": ["컨센서스 충격"],
            "data_evidence": {
                "event": event_name,
                "actual": actual,
                "previous": previous,
                "surprise_pct": f"{surprise_pct:+.1f}%",
            },
            "why_now": f"{event_name}의 변화량이 12개월 평균 대비 {abs(surprise_pct):.0f}% 이탈 — 오늘 처음 나타난 이상 수준",
            "selected": True
        }

    def _build_zscore_fallback_topic(self, market_data: dict) -> Optional[dict]:
        """
        multi_period_stats에서 Z-score 최대값 지표로 토픽 생성
        """
        if not market_data:
            return None

        multi_stats = market_data.get("multi_period_stats", {})
        if not multi_stats:
            return None

        best_key = None
        best_zscore = 0.0

        for key, stats in multi_stats.items():
            zscore = abs(stats.get("zscore_5d", 0) or 0)
            if zscore > best_zscore:
                best_zscore = zscore
                best_key = key

        if not best_key or best_zscore < 2.0:
            return None

        stats = multi_stats[best_key]
        change_5d = stats.get("change_5d_pct", 0)
        direction = "급등" if change_5d > 0 else "급락"

        topic = f"{best_key} 5일 Z-score {best_zscore:.1f} — 통계적 이상 {direction}"

        return {
            "topic": topic,
            "strength": min(9.0, 5.0 + best_zscore),
            "content_type": "롱폼",
            "source": "ZSCORE_FALLBACK",
            "filters_hit": ["역사적 임계값 돌파"],
            "data_evidence": {
                "indicator": best_key,
                "zscore_5d": best_zscore,
                "change_5d_pct": f"{change_5d:+.1f}%",
            },
            "why_now": f"{best_key} Z-score {best_zscore:.1f} — 통계적으로 오늘 처음 임계값 초과",
            "selected": True
        }

    def select_best(self, anomalies: list, market_data: dict, consensus_data: dict) -> dict:
        if not anomalies:
            # LLM 결과가 없을 경우 곧장 Fallback
            anomalies = []

        # 절대값 토픽 필터링
        filtered = []
        for a in anomalies:
            if self._is_absolute_value_topic(a.get("topic", ""), a):
                print(f"  🚫 절대값 토픽 필터링: {a.get('topic', '')[:50]}")
            else:
                filtered.append(a)

        if not filtered:
            # 1차: consensus.json에서 가장 강한 서프라이즈 토픽으로 교체
            consensus_fallback = self._build_consensus_fallback_topic(consensus_data)
            if consensus_fallback:
                print("  🔄 절대값 필터 후 후보 없음 → 컨센서스 서프라이즈 토픽으로 교체")
                return consensus_fallback
            
            # 2차: 모든 수집 데이터에서 Z-score 최대값 지표로 토픽 생성
            zscore_fallback = self._build_zscore_fallback_topic(market_data)
            if zscore_fallback:
                print("  🔄 컨센서스 없음 → Z-score 최대값 토픽으로 교체")
                return zscore_fallback
            
            # 3차: 그래도 없으면 "오늘 이상징후 없음" 처리
            print("  ⚠️ 유효한 토픽 없음 — 오늘 파이프라인 스킵")
            return None

        sorted_anomalies = sorted(
            filtered,
            key=lambda x: x.get("strength", 0),
            reverse=True
        )

        best = sorted_anomalies[0]
        best["selected"] = True
        best["content_type"] = "롱폼" if best.get("strength", 0) >= 8.0 else "쇼츠"
        best["date"] = self.today
        best["source"] = "LLM"
        return best

    def select_topic(self, candidates):
        """강도 기준 최종 토픽 선정 (하위 호환성 유지)"""
        for c in candidates:
            if c.get("strength", 0) >= 6.0:
                c["selected"] = True
                c["content_type"] = "롱폼" if c["strength"] >= 8.0 else "쇼츠"
                return c
        return None

    def save_results(self, candidates, selected):
        """결과 저장"""
        # candidates.json 저장
        all_candidates = []
        for i, c in enumerate(candidates):
            all_candidates.append({
                "rank": i + 1,
                "topic": c.get("topic"),
                "filters_hit": c.get("filters_hit", []),
                "strength": c.get("strength", 0),
                "selected": selected and c.get("topic") == selected.get("topic")
            })

        (self.signal_dir / "candidates.json").write_text(
            json.dumps({
                "date": self.today,
                "candidates": all_candidates
            }, ensure_ascii=False, indent=2)
        )

        # today_signal.json 저장
        if selected:
            (self.signal_dir / "today_signal.json").write_text(
                json.dumps({
                    "date": self.today,
                    "topic": selected["topic"],
                    "strength": selected["strength"],
                    "content_type": selected["content_type"],
                    "filters_hit": selected["filters_hit"],
                    "data_evidence": selected.get("data_evidence", {}),
                    "related_keywords": selected.get("related_keywords", []),
                    "level2_chain": [],
                    "urgency": "HIGH" if selected["strength"] >= 8.0 else "MEDIUM"
                }, ensure_ascii=False, indent=2)
            )

    def run(self, collector_result=None):
        print(f"\n🔍 AGENT-03 DETECTOR 시작 [{self.today}]")

        # 1. 데이터 로드
        all_data = self.load_all_data()
        if not all_data:
            print("  데이터 로드 실패")
            return {}

        # 2. 후보 생성 (기존 로직 보조용)
        candidates = self.build_candidates(all_data)

        # 3. 데이터 요약 생성
        summary = self.build_data_summary(all_data)

        # 4. LLM 기반 최종 신호 탐지
        anomalies = self.detect_anomalies(summary, candidates)
        
        # 5. 최적 토픽 선정 (필터링 및 fallback 포함)
        market_data = all_data.get("market", {})
        consensus_data = all_data.get("consensus", {})
        selected = self.select_best(anomalies, market_data, consensus_data)

        if selected and selected.get("selected"):
            print(f"  ✅ 선정 완료: {selected['topic']}")
            print(f"  강도: {selected['strength']} / 유형: {selected['content_type']} / 소스: {selected.get('source', 'LLM')}")
        else:
            print("  오늘 선정 기준 충족 신호 없음")

        # 6. 저장
        self.save_results(candidates, selected)
        print("✅ AGENT-03 완료\n")
        return {"selected": selected, "candidates": candidates}


if __name__ == "__main__":
    agent = DetectorAgent()
    agent.run()
