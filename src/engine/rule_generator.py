
import json
import re
from typing import Dict, List, Optional

class RuleBasedScriptGenerator:
    """[TASK #092] DETERMINISTIC CONTENT ENGINE
    AI 없이도 완성된 스크립트를 생성하는 규칙 기반 엔진
    """

    NORMAL_TEMPLATE = """[HOOK]
{hook}

[FLOW]
{event_summary} 이 발생했을 때 원래 시장은 이렇게 움직여야 한다.
{normal_flow}

[SCENARIO]
가능한 시나리오는 3가지다.
{scenarios}

[DECISION]
지금 데이터 기준으로 보면 {selected_scenario} 가능성이 가장 높다.

[IMPLICATION]
이 흐름이 이어지면
{theme_impact}

[ACTION]
지금 중요한 건 {action_condition}이다."""

    ANOMALY_TEMPLATE = """[HOOK]
{hook}

[EXPECTED]
원래라면
{expected_flow}

[REALITY]
근데 지금 시장은
{actual_data}

[MISMATCH]
이게 의미하는 건
{mismatch_summary}

[WHY NOW]
지금 이 현상이 중요한 이유는
{why_now}

[IMPLICATION]
이 흐름이 이어지면
{theme_impact}

[ACTION]
지금 시장에서 중요한 건 {action_condition}이다."""

    FALLBACK_TEMPLATE = """(Step 1: Hook)
[I] {hook}

(Step 2: Context)
[F] {fact_summary}

(Step 3: Mechanism)
[I] {mechanism}

(Step 4: WHY NOW)
[F] {why_now_detail}

(Step 5: Implication)
[I] {theme_impact}

(Step 6: Mentionables)
[F] {mentionables}

(Step 7: Risk/Scenario)
[I] {selected_scenario} 가능성이 가장 높다. {risk_warning}

---

### [오늘 이것 하나만 기억해]
{one_thing}"""

    def __init__(self):
        pass

    def generate_fallback(self, candidate: Dict) -> Optional[Dict]:
        """[TASK #093] 정식 결정론적 폴백 스크립트 생성 (Hunter DNA 주입)"""
        if not self._check_fail_safe(candidate):
            return None
            
        vars = self._generate_variables(candidate)
        
        # 1. FACT 요약 정밀화 (None 방지)
        facts = candidate.get("core_facts", [])
        fact_lines = []
        for f in facts[:2]:
            val = f.get('value', '데이터 확인 중')
            chg = f.get('change')
            chg_str = f"{chg:+.2f}%" if (isinstance(chg, (int, float)) and chg != 0) else "변동성 확대"
            fact_lines.append(f"현재 {f.get('name')} 지표는 {val} 수준으로, 전일 대비 {chg_str} 흐름을 보이고 있다.")
        vars["fact_summary"] = " ".join(fact_lines) if fact_lines else "주요 거시 지표의 이례적인 움직임이 포착되었다."
        
        # 2. WHY NOW Detail (Deep Detail & DART 연동)
        # evidence_bundle이 있으면 거기서 뽑고, 없으면 why_now에서 추출
        evidence = candidate.get("evidence_bundle", {})
        deep_events = evidence.get("related_events", [])
        if deep_events:
            # 수치가 포함된 상세 내역을 우선적으로 배치
            vars["why_now_detail"] = " / ".join(deep_events[:2])
        else:
            vars["why_now_detail"] = vars.get("why_now", "현재 시장의 결정적 수급 변화가 임계점을 돌파했다.")

        # 3. 추가 변수 설정
        vars["title"] = candidate.get("topic", "시장 긴급 분석")
        vars["status_label"] = "PARTIAL_SUCCESS (Gemini 실패, Fallback 엔진 가동)"
        vars["gate_status"] = "PASS (Deterministic)"
        vars["mechanism"] = candidate.get("mechanism", "이례적인 수급 쏠림으로 인한 지표 간의 디커플링 현상이 관측된다.")
        if vars["mechanism"] == "Correlative shift observed": # Engine 기본값 교체
            vars["mechanism"] = "주요 자산군 간의 상관관계가 깨지며 새로운 가격 축이 형성되는 과정이다."
            
        vars["mentionables"] = "현재 데이터상 직접적인 브리지가 확인되는 종목은 없다. 관련 섹터 ETF의 흐름을 관찰하라."
        vars["risk_warning"] = "다만, 단기 변동성 확대에 따른 오버슈팅 가능성을 경계해야 한다."
        vars["one_thing"] = f"오늘 관찰된 {vars['title']} 현상이 지속되는지 확인해라. 그게 진짜 신호다."

        try:
            script = self.FALLBACK_TEMPLATE.format(**vars)
        except Exception as e:
            print(f"  ⚠️ 폴백 템플릿 렌더링 실패: {e}")
            return None
            
        from datetime import datetime
        return {
            "topic": vars["title"],
            "script": script,
            "content_type": candidate.get("classification", "NORMAL"),
            "themes": vars.get("themes", []),
            "action": vars.get("action_condition", "WATCH"),
            "date": datetime.now().strftime("%Y%m%d"),
            "strength": candidate.get("strength", 5.0)
        }

    def generate(self, candidate: Dict) -> Optional[Dict]:
        """팩트 데이터를 바탕으로 스크립트 생성 (Fail-Safe 적용)"""
        
        # 1. Fail-Safe Check
        if not self._check_fail_safe(candidate):
            print(f"  🚫 [FAIL-SAFE] {candidate.get('topic')} 생성 조건 미달")
            return None

        classification = candidate.get("classification", "NORMAL")
        
        # 2. Variable Generation
        variables = self._generate_variables(candidate)
        
        # 3. Template Selection & Rendering
        if classification == "ANOMALY":
            template = self.ANOMALY_TEMPLATE
        else:
            template = self.NORMAL_TEMPLATE
            
        try:
            script = template.format(**variables)
        except KeyError as e:
            print(f"  ⚠️ 템플릿 변수 누락: {e}")
            return None

        return {
            "title": candidate.get("topic", "시장 분석"),
            "script": script,
            "type": classification,
            "themes": variables.get("themes", []),
            "action": variables.get("action_condition", "관망")
        }

    def _check_fail_safe(self, cand: Dict) -> bool:
        """필수 데이터 존재 여부 확인 (Resilience를 위해 완화)"""
        if not cand.get("core_facts") and not cand.get("topic"):
            return False
        # scenarios가 없어도 Resilience를 위해 생성 허용
        return True

    def _generate_variables(self, cand: Dict) -> Dict:
        vars = {}
        classification = cand.get("classification", "NORMAL")
        
        # [HOOK]
        if classification == "ANOMALY":
            expected = cand.get("anomaly_overlay", {}).get("expected", "정상적인 흐름")
            actual = cand.get("anomaly_overlay", {}).get("actual", "현재의 움직임")
            vars["hook"] = f"왜 {expected}인데 {actual}일까?"
        else:
            flow_q = cand.get("topic", "현재 시장의 변화")
            vars["hook"] = f"왜 지금 시장은 {flow_q}일까?"

        # [FLOW / EXPECTED]
        vars["event_summary"] = cand.get("topic", "")
        normal_flow_data = cand.get("normal_flow", {})
        if isinstance(normal_flow_data, dict):
            vars["normal_flow"] = ". ".join(normal_flow_data.get("expected_reactions", ["시장 원리에 따른 정방향 움직임"]))
            vars["expected_flow"] = ". ".join(normal_flow_data.get("expected_reactions", ["통상적인 시장 반응"]))
        else:
            vars["normal_flow"] = str(normal_flow_data)
            vars["expected_flow"] = str(normal_flow_data)

        # [REALITY / ACTUAL DATA]
        facts = cand.get("core_facts", [])
        actual_str = []
        for f in facts:
            if isinstance(f, dict):
                actual_str.append(f"{f.get('name')}: {f.get('value')} (변화율: {f.get('change', 'N/A')})")
        vars["actual_data"] = ". ".join(actual_str) if actual_str else "데이터 기반 변동 발생"

        # [MISMATCH]
        mismatch = cand.get("anomaly_overlay", {}).get("mismatch", [])
        vars["mismatch_summary"] = ". ".join(mismatch) if mismatch else "지표 간의 이례적인 불일치 포착"

        # [SCENARIOS]
        scenarios = cand.get("scenarios", [])
        formatted_scenarios = []
        for i, s in enumerate(scenarios[:3]):
            name = s.get("scenario", f"시나리오 {i+1}")
            formatted_scenarios.append(f"{i+1}. {name} 가능성")
        vars["scenarios"] = "\n".join(formatted_scenarios)

        # [DECISION]
        vars["selected_scenario"] = scenarios[0].get("scenario", "기본 시나리오") if scenarios else "중립 시나리오"

        # [WHY NOW] - 숫자 포함 문장 필터링
        why_now_list = cand.get("why_now", [])
        numeric_why_now = [s for s in why_now_list if re.search(r'\d', s)]
        if not numeric_why_now:
            # 숫자가 포함된 facts를 강제로 조합
            numeric_why_now = actual_str[:2]
        vars["why_now"] = "\n".join(numeric_why_now) if numeric_why_now else "현재 시장의 결정적 수급 변화 포착"

        # [IMPLICATION / THEME IMPACT]
        mapping = self._map_themes(cand)
        vars["themes"] = mapping["themes"]
        impact_sentences = []
        for theme in mapping["themes"][:2]:
            impact_sentences.append(f"{theme} 섹터의 변동성이 확대되며 관련 종목군에 영향이 예상된다.")
        vars["theme_impact"] = "\n".join(impact_sentences) if impact_sentences else "주요 섹터 전반의 수급 확산 가능성"

        # [ACTION]
        strength = cand.get("strength", 5.0)
        if classification == "ANOMALY":
            vars["action_condition"] = "OPPORTUNITY" if strength > 7.0 else "RISK"
        else:
            vars["action_condition"] = "WATCH" if strength > 6.0 else "WAIT"

        return vars

    def _map_themes(self, cand: Dict) -> Dict:
        """이벤트 및 데이터에서 테마와 종목 정보를 추출 (동적 추출)"""
        mapping = {"themes": [], "stocks": []}
        
        # TopicSelectionEngine에서 전달된 데이터 우선 사용
        mapping["themes"] = cand.get("themes", [])
        mapping["stocks"] = cand.get("stocks", [])
        
        # 데이터가 없을 경우에만 최소한의 맥락 정보 부여
        if not mapping["themes"]:
            # [HUNTER DNA] 특정 종목을 강제하지 않고 시장 전반의 맥락으로 처리
            mapping["themes"] = ["시장전반", "수급변화"]
            
        return mapping
