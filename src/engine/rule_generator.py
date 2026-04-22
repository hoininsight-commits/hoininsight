
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

    FALLBACK_TEMPLATE = """[HOOK]
{hook}

[FACT]
{fact_summary}

[SCENARIO]
{selected_scenario} 가능성이 가장 높다.

[IMPLICATION]
{theme_impact}

[ACTION]
{action_condition}이다."""

    def __init__(self):
        pass

    def generate_fallback(self, candidate: Dict) -> Optional[Dict]:
        """[TASK #093] 정식 결정론적 폴백 스크립트 생성"""
        if not self._check_fail_safe(candidate):
            return None
            
        vars = self._generate_variables(candidate)
        
        # FACT 요약 (2~3개 핵심 수치)
        facts = candidate.get("core_facts", [])
        fact_lines = []
        for f in facts[:3]:
            fact_lines.append(f"현재 {f.get('name')}는 {f.get('value')}로 전일 대비 {f.get('change', '변동')} 중이다.")
        vars["fact_summary"] = "\n".join(fact_lines) if fact_lines else "주요 지표의 변동성이 관측되고 있다."
        
        try:
            script = self.FALLBACK_TEMPLATE.format(**vars)
        except Exception as e:
            print(f"  ⚠️ 폴백 템플릿 렌더링 실패: {e}")
            return None
            
        return {
            "title": candidate.get("topic", "시장 분석 (폴백)"),
            "script": script,
            "type": candidate.get("classification", "NORMAL"),
            "themes": vars.get("themes", []),
            "action": vars.get("action_condition", "WATCH")
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
        """필수 데이터 존재 여부 확인"""
        if not cand.get("core_facts") and not cand.get("why_now"):
            return False
        if not cand.get("scenarios") or len(cand.get("scenarios", [])) == 0:
            return False
        if not cand.get("classification"):
            return False
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

    def _map_themes(self, candidate: Dict) -> Dict:
        """이벤트 -> 섹터 -> 테마 자동 매핑 (규칙 기반)"""
        topic = candidate.get("topic", "").lower()
        mapping = {"themes": [], "stocks": []}
        
        rules = {
            "유가": {"themes": ["정유", "에너지", "신재생"], "stocks": ["S-Oil", "SK이노베이션"]},
            "휴전": {"themes": ["방산", "에너지", "재건"], "stocks": ["한화에어로스페이스", "현대로템"]},
            "삼성": {"themes": ["반도체", "HBM"], "stocks": ["삼성전자", "SK하이닉스"]},
            "금리": {"themes": ["금융", "기술주", "성장주"], "stocks": ["KB금융", "NAVER"]},
            "달러": {"themes": ["수출주", "여행", "항공"], "stocks": ["현대차", "대한항공"]},
            "ai": {"themes": ["AI", "반도체소부장"], "stocks": ["한미반도체", "리노공업"]},
            "국채": {"themes": ["금융", "채권형"], "stocks": ["KB금융", "신한지주"]}
        }
        
        for key, val in rules.items():
            if key in topic:
                mapping["themes"].extend(val["themes"])
                mapping["stocks"].extend(val["stocks"])
        
        if not mapping["themes"]:
            mapping["themes"] = ["매크로", "시장전반"]
            
        mapping["themes"] = list(set(mapping["themes"]))
        return mapping
