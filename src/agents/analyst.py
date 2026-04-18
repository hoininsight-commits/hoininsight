import json
from datetime import datetime
from pathlib import Path
from src.core.gemini_client import GeminiClient
from src.core.sector_map import get_related_sectors, get_stocks_by_sector, get_reason_template


class AnalystAgent:

    def __init__(self):
        self.today = datetime.now().strftime("%Y%m%d")
        self.signal_dir = Path(f"data/signals/{self.today}")
        self.raw_dir = Path(f"data/raw/{self.today}")
        self.analysis_dir = Path(f"data/analysis/{self.today}")
        self.analysis_dir.mkdir(parents=True, exist_ok=True)
        self.gemini = GeminiClient()

    def load_signal(self):
        p = self.signal_dir / "today_signal.json"
        if not p.exists():
            return None
        return json.loads(p.read_text())

    def load_raw(self):
        raw = {}
        for name in ["macro", "market", "sentiment", "cot"]:
            p = self.raw_dir / f"{name}.json"
            if p.exists():
                raw[name] = json.loads(p.read_text())
        return raw

    def _filter_text(self, text: str, market_data: dict) -> str:
        """텍스트 필드에서 데이터 근거 없는 서술을 필터링 (Task 5-HOTFIX)"""
        if not text:
            return text

        kospi_foreign_net = market_data.get("kospi_foreign_net", None)
        foreign_condition = (
            kospi_foreign_net is None
            or abs(float(kospi_foreign_net)) == 0.0
        )

        # 금지어 패턴 및 대체어 (Task 1 & 5)
        forbidden_rules = [
            {
                "active": foreign_condition,
                "keywords": ["외국인", "외인", "foreign", "자금 유입 가속"],
                "replacement": "기관 수급 중심의"
            },
            {
                "active": True,
                "keywords": ["개인투자자", "FOMO", "포모", "개미", "모멘텀 자금", "군중"],
                "replacement": "수급"
            },
            {
                "active": True,
                "keywords": ["보험성", "보험용", "보험을", "보험이", "보험 가"],
                "replacement": "리스크 관리 목적의"
            },
            {
                "active": True,
                "keywords": ["완벽한 골디락스", "완벽한 타이밍", "완벽한 상황"],
                "replacement": "우호적인 매크로 환경"
            }
        ]

        import re
        for rule in forbidden_rules:
            if rule["active"]:
                for kw in rule["keywords"]:
                    if kw in text:
                        text = text.replace(kw, rule["replacement"])
        return text

    def _filter_level2_chain(self, level2_chain: list, market_data: dict) -> list:
        """level2_chain 항목 필터링 (Task 1)"""
        if not level2_chain:
            return level2_chain
        
        filtered = []
        for item in level2_chain:
            filtered_item = self._filter_text(item, market_data)
            # 필터링 후 내용이 너무 짧아지거나 변화가 크면 제거 고려 가능하나 일단 유지
            if filtered_item:
                filtered.append(filtered_item)
        return filtered

    def load_existing_analysis(self):
        """기존 today_analysis.json 로드 (Gemini 파싱 실패 시 폴백, Task 5)"""
        p = self.analysis_dir / "today_analysis.json"
        if p.exists():
            try:
                data = json.loads(p.read_text())
                if data and data.get("topic"):
                    return data
            except Exception:
                pass
        return None

    def analyze(self, signal, raw_data):
        """Gemini API로 레벨2 분석 (v7.0: STATE 판단 레이어 추가)"""
        print("  Gemini API 레벨2 분석 중...")

        market = raw_data.get("market", {}).get("data", {})
        macro = raw_data.get("macro", {}).get("data", {})
        cot = raw_data.get("cot", {}).get("positions", {})
        stats = market.get("multi_period_stats", {})

        # 데이터 요약 파싱 (프롬프트 전달용)
        market_summary = "\n".join([f"- {k.upper()}: Z={v.get('z_score_20d')}, 5d_chg={v.get('chg_5d')}%" for k, v in stats.items()])
        cot_summary = "\n".join([f"- {k}: {v.get('direction')} (Net: {v.get('net_change', 0):+,} contracts)" for k, v in cot.items()])

        prompt = f"""
너는 경제사냥꾼 채널 수준의 거시경제 분석 전문가다.
아래 신호와 데이터를 분석해서 시장의 '상태(STATE)'를 정의하고 레벨 2 분석을 수행해라.

[오늘의 신호]
토픽: {signal['topic']}
강도: {signal['strength']}

[수집 데이터 - 핵심 통계]
{market_summary}

[수집 데이터 - COT 수급]
{cot_summary}

---

### [시장 상태 판단 가이드]

STEP 1 — 신호 충돌 확인:
- 가격(S&P500/KOSPI/VIX/Gold) 방향과 COT 수급 방향이 일치하는지 확인.
- 가격은 상승인데 COT가 숏이면 '충돌'로 간주.

STEP 2 — STATE 정의 (3가지 축):
1. Risk Appetite: 상승 / 하락 / 혼조 (주가와 VIX 기준)
2. Hedging Activity: 증가 / 감소 / 중립 (COT 포지션 변화 기준)
3. Directional Conviction: 높음 / 낮음 (가격과 수급의 일치 여부)

STEP 3 — STATE 기반 서사 제약:
- Risk Appetite 상승 + Hedging Activity 증가 조합일 경우:
  * "붕괴", "공포", "대탈출", "폭풍 전야" 서사 절대 금지.
  * 대신 "낙관 속 불안", "헤지 강화", "리스크 관리 가동"으로 해석.
- 하락 베팅(숏)은 반드시 "롱 포지션 헤지(보험)" 가능성을 병기할 것.
- 가격 데이터를 COT보다 우선한다.

STEP 4 — 결과 생성:
아래 JSON 구조에 따라 분석 결과를 리턴해라.

[출력 JSON 구조]
{{
  "date": "{self.today}",
  "topic": "{signal['topic']}",
  "market_state": {{
    "risk_appetite": "상승/하락/혼조",
    "hedging_activity": "증가/감소/중립",
    "conviction": "높음/낮음",
    "summary": "한 줄 요약 (예: Risk ON + Hedge Overlay)"
  }},
  "why_now": "왜 지금 이 이슈가 중요한가 (2~3문장)",
  "expectation_vs_reality": {{
    "expectation": "시장 기대",
    "reality": "실제 현실",
    "conflict": "충돌 이유"
  }},
  "level2_chain": ["원인1", "원인2", "원인3", "한국 임팩트"],
  "key_stocks": ["종목1", "종목2", "종목3"],
  "risk": "무효화 조건 한 문장"
}}

순수 JSON만 출력해라. 마크다운 없이.
"""
        result = self.gemini.call_json(prompt, max_tokens=1500)

        # Gemini 응답 파싱 실패 방어 (Task 5)
        if not result or not result.get("topic"):
            print("  ⚠️ Gemini 응답 파싱 실패 — 기존 today_analysis.json 유지")
            existing = self.load_existing_analysis()
            if existing:
                print(f"  → 기존 분석 파일 사용: topic={existing.get('topic', '')[:40]}")
                return existing
            # 기존 파일도 없으면 빈 결과 반환 (이후 단계에서 실패 처리됨)
            return {}

        # 모든 텍스트 필드 정밀 필터링 (Task 5-HOTFIX)
        market_data = raw_data.get("market", {}).get("data", {})
        result["why_now"] = self._filter_text(result.get("why_now", ""), market_data)
        
        ev_reality = result.get("expectation_vs_reality", {})
        if ev_reality:
            ev_reality["expectation"] = self._filter_text(ev_reality.get("expectation", ""), market_data)
            ev_reality["reality"] = self._filter_text(ev_reality.get("reality", ""), market_data)
            ev_reality["conflict"] = self._filter_text(ev_reality.get("conflict", ""), market_data)

        result["level2_chain"] = self._filter_level2_chain(
            result.get("level2_chain", []), market_data
        )

        # today_signal.json 업데이트
        signal["level2_chain"] = result["level2_chain"]
        signal["market_state"] = result.get("market_state", {})
        signal_path = self.signal_dir / "today_signal.json"
        signal_path.write_text(json.dumps(signal, ensure_ascii=False, indent=2))

        return result

    def map_stocks(self, signal, analysis):
        """관련 종목 매핑 (v6.0: MACRO 토픽은 종목보다 시나리오에 집중)"""
        target_type = signal.get("target_type", "MICRO_SECTOR_FOCUS")
        
        # MACRO_GEOPOLITICAL 등 거대 담론은 억지 매핑 지양
        if "MACRO" in target_type:
            print(f"  📢 거대 담론({target_type}) 감지 — 종목보다 거시 시나리오에 집중합니다.")
            return {
                "date": self.today,
                "topic_signal": signal["topic"],
                "stocks": [],
                "target_segments": signal.get("related_keywords", []),
                "is_macro_narrative": True
            }

        print("  종목 매핑 중...")

        keywords = signal.get("related_keywords", []) or signal.get("key_indicators", [])
        related_sectors = get_related_sectors(keywords)

        # reason 생성용 컨텍스트 추출
        market_state = analysis.get("market_state", {}) or signal.get("market_state", {}) or {}
        direction = "상승" if market_state.get("risk_appetite") == "상승" else "하락" if market_state.get("risk_appetite") == "하락" else "혼조"
        direction_inv = "하락" if direction == "상승" else "상승" if direction == "하락" else "혼조"
        level2_chain = analysis.get("level2_chain") or signal.get("level2_chain") or []

        # 신호 유형 판별 (z_score / cot / consensus / default)
        topic_lower = signal.get("topic", "").lower()
        why_anomalous = signal.get("why_anomalous", "")
        if "cot" in topic_lower or "포지션" in topic_lower:
            signal_type = "cot"
        elif "컨센서스" in topic_lower or "consensus" in topic_lower:
            signal_type = "consensus"
        elif "z-score" in topic_lower or "z_score" in topic_lower or "z-score" in why_anomalous.lower() or "z_score" in why_anomalous.lower():
            signal_type = "z_score"
        else:
            signal_type = "default"

        # z_score 값 추출: signal.why_anomalous 또는 topic에서 파싱
        import re as _re
        z_score_val = "N/A"
        chg_5d_val = "N/A"
        _z_match = _re.search(r"Z-score[=\s]*([\d.]+)", why_anomalous, _re.IGNORECASE) or \
                   _re.search(r"Z-score[=\s]*([\d.]+)", signal.get("topic", ""), _re.IGNORECASE)
        if _z_match:
            z_score_val = _z_match.group(1)

        # 시장 통계에서 chg_5d 추출 (raw market data 활용)
        raw_data = self.load_raw()
        market_stats = raw_data.get("market", {}).get("data", {}).get("multi_period_stats", {})
        topic_key = topic_lower.split(" ")[0]  # "sp500", "gold", "kospi" 등
        for key, stats in market_stats.items():
            if topic_key in key.lower():
                chg_5d_val = stats.get("chg_5d", "N/A")
                break

        cot_direction = "숏" if direction == "하락" else "롱"

        stocks = []
        for sector in related_sectors[:3]:
            sector_stocks = get_stocks_by_sector(sector)
            template = get_reason_template(sector, signal_type)

            # 2단계 연결 사슬 reason 생성
            try:
                reason = template.format(
                    z_score=z_score_val,
                    chg_5d=chg_5d_val,
                    direction=direction,
                    direction_inv=direction_inv,
                    cot_direction=cot_direction,
                    sector=sector
                )
            except KeyError:
                reason = f"{signal['topic']} {direction} → {sector} 섹터 영향 (연결 사슬 구성 불가)"

            # 연결 사슬이 level2_chain에 있으면 첫 2단계 활용
            if level2_chain and len(level2_chain) >= 2:
                reason = f"{level2_chain[0]} → {level2_chain[1]} → {sector} 직접 영향"

            for s in sector_stocks[:2]:
                stocks.append({
                    "ticker": s["ticker"],
                    "name": s["name"],
                    "sector": sector,
                    "impact": "수혜",
                    "reason": reason,
                    "impact_level": "HIGH" if signal["strength"] >= 8.0 else "MEDIUM",
                    "is_primary": True
                })

        # 섹터 맵으로 매핑이 안 된 경우 Claude 활용
        if not stocks:
            print("  섹터 맵 미매칭 — Claude 종목 추론 중...")
            prompt = f"""
토픽: {signal['topic']}
분석: {json.dumps(analysis.get('level2_chain', analysis.get('why_now', '')), ensure_ascii=False)}

위 상황에서 영향받는 한국 코스피/코스닥 상장 종목 3개를 골라라.
실제 존재하는 종목만 사용해라.

JSON 배열만 출력 (마크다운 없이):
[
  {{"ticker":"종목코드6자리","name":"종목명","sector":"섹터명","impact":"수혜 또는 피해","reason":"이유 한 문장","impact_level":"HIGH 또는 MEDIUM","is_primary":true}}
]
"""
            result = self.gemini.call_json(prompt, max_tokens=800)
            if isinstance(result, list):
                stocks = result

        return {
            "date": self.today,
            "topic_signal": signal["topic"],
            "stocks": stocks
        }

    def save_results(self, analysis, stocks_data):
        # 빈 데이터 저장 방지 (topic 없는 경우도 포함, Task 5)
        if not analysis or analysis == {} or not analysis.get("topic"):
            print("  ⚠️ 분석 결과 없음 — 저장 건너뜀")
            return False

        (self.analysis_dir / "today_analysis.json").write_text(
            json.dumps(analysis, ensure_ascii=False, indent=2)
        )
        (self.analysis_dir / "today_stocks.json").write_text(
            json.dumps(stocks_data, ensure_ascii=False, indent=2)
        )
        print(f"  저장 완료: {self.analysis_dir}")
        return True

    def run(self, detector_result=None):
        print(f"\n🧠 AGENT-04 ANALYST 시작 [{self.today}]")

        signal = self.load_signal()
        if not signal:
            print("  선정된 신호 없음 — AGENT-03 먼저 실행 필요")
            return {}

        print(f"  분석 대상: {signal['topic']}")

        raw_data = self.load_raw()
        analysis = self.analyze(signal, raw_data)

        if not analysis or analysis == {}:
            print("  ❌ AGENT-04 분석 실패 — WRITER 실행 불가")
            print("  원인: API 쿼터 초과 또는 응답 오류")
            # 실패 마커 파일 생성
            failure_path = self.analysis_dir / "analysis_failed.txt"
            failure_path.write_text(f"분석 실패: {datetime.now().isoformat()}\n원인: API 응답 없음")
            return {"analysis": None, "stocks": None, "failed": True}

        stocks_data = self.map_stocks(signal, analysis)
        saved = self.save_results(analysis, stocks_data)
        print("✅ AGENT-04 완료\n")
        return {"analysis": analysis, "stocks": stocks_data, "failed": False}


if __name__ == "__main__":
    agent = AnalystAgent()
    agent.run()
