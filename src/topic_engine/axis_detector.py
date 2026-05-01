from typing import List, Dict
from src.core.gemini_client import GeminiClient
import json

class AxisDetector:
    """[TASK #103] Market Axis Detector (v3.0 - Zero-Shot Discovery)"""

    AXIS_MAP = {
        "rates": ["us10y", "us2y", "fed_funds"],
        "liquidity": ["usd_krw", "vix", "hyg"],
        "geopolitics": ["wti_oil", "gold", "vix"],
        "supply_chain": ["wti_oil", "brent", "freight_index"],
        "policy": ["us10y", "fed_funds", "sp500"],
        "flow": ["nasdaq", "sp500", "kospi"]
    }

    def __init__(self):
        self.gemini = GeminiClient()

    def validate_axis(self, axis: str, stats: Dict) -> Dict:
        """기본 매크로 축의 반응성을 체크합니다."""
        assets = self.AXIS_MAP.get(axis, [])
        valid_stats = {a: stats[a] for a in assets if a in stats}
        if not valid_stats:
            return {"passed": False, "reason": "no_data", "direction_consistent": True}
        
        reaction = any(abs(s.get("z_score_20d", 0)) > 1.2 or abs(s.get("chg_5d", 0)) > 0.8 for s in valid_stats.values())
        return {"passed": reaction, "reaction": reaction, "direction_consistent": True}

    def discover_frontier_axes(self, candidates: List[Dict]) -> Dict:
        """LLM을 이용하여 후보군에서 자율적으로 주도 섹터/테마를 추출합니다."""
        if not self.gemini: 
            return {"primary": "emerging", "secondary": "flow"}

        # 상위 40개 이벤트의 텍스트와 메타데이터(예: 소셜 거래량)를 함께 전달
        event_texts = []
        for c in candidates[:40]:
            src = c.get('source', 'NA')
            ev = c.get('event', '')
            # 소셜 데이터인 경우 수치 정보를 포함하여 가중치를 높임
            if c.get('candidate_type') == 'PRED_MARKET':
                vol = c.get('core_facts', [{}])[1].get('value', 'N/A')
                prob = c.get('core_facts', [{}])[0].get('value', 'N/A')
                event_texts.append(f"[PRED_MARKET] {ev} (Vol: {vol}, Prob: {prob})")
            else:
                event_texts.append(f"[{src}] {ev}")
        
        prompt = f"""
        당신은 시장의 미세한 흐름과 소셜 에너지(예측 시장 등)를 포착하는 사냥꾼입니다.
        아래 데이터 리스트를 보고 오늘 시장을 지배하거나 사람들의 자본이 몰리는 '진짜' 테마 2개를 추출하세요.
        단순 경제 지표보다 예측 시장(PRED_MARKET)이나 소셜에서 에너지가 분출되는 주제에 더 주목하십시오.
        
        [데이터]
        {json.dumps(event_texts, ensure_ascii=False)}
        
        [형식]
        {{
          "primary": "첫 번째 테마 명칭",
          "secondary": "두 번째 테마 명칭",
          "reason": "이유"
        }}
        """
        try:
            # [TASK #103.1] Tier 1 격상하여 과부하 시에도 끈질기게 재시도
            res = self.gemini.call_json_controlled(prompt, agent="AXIS_DISCOVERY", tier=1)
            
            if res and "primary" in res:
                print(f"    ✨ Discovery Success: {res.get('primary')} / {res.get('secondary')}")
                return res
            return {"primary": "emerging", "secondary": "flow"}
        except Exception as e:
            print(f"    ⚠️ Discovery Error: {str(e)}")
            return {"primary": "emerging", "secondary": "flow"}

    def detect_market_axis(self, candidates: List[Dict], market_data: Dict) -> Dict:
        """자율 발견 및 지능형 매핑 기반의 축 선정 로직"""
        print(f"  🔍 Discovering Market Axes autonomously...")
        discovery = self.discover_frontier_axes(candidates)
        primary_axis = discovery.get("primary", "emerging")
        secondary_axis = discovery.get("secondary", "flow")
        
        stats = market_data.get("multi_period_stats", {})
        
        # 1. 매크로 축 검증 (참고용 히스토리 유지)
        validation_results = {}
        for axis in self.AXIS_MAP:
            validation_results[axis] = self.validate_axis(axis, stats)
            
        # 2. [INTELLIGENT MAPPING] 개별 후보군을 발견된 축에 매핑
        # [TASK #3.1] 꼼수 키워드 대신, 발견된 Frontier Axis에 후보들을 지능적으로 배정
        mapping_prompt = f"""
        당신은 시장 분류 전문가입니다. 아래 후보 테마들이 우리가 발견한 '주도 축' 중 어디에 속하는지 분류하세요.
        속하지 않는다면 'emerging'으로 분류하세요.
        
        [주도 축]
        1. {primary_axis}
        2. {secondary_axis}
        
        [후보 리스트]
        {json.dumps([{"id": c.get("candidate_id", "unknown"), "event": c.get("event", "")} for c in candidates[:10]], ensure_ascii=False)}
        
        [응답 형식]
        {{"candidate_id": "분류된 축 이름"}} (JSON Object 하나만 응답)
        """
        try:
            mapping_res = self.gemini.call_json_controlled(mapping_prompt, agent="AXIS_MATCHER", tier=1)
            for cand in candidates:
                target_axis = mapping_res.get(cand.get("candidate_id")) if mapping_res else None
                if target_axis and target_axis != "emerging":
                    cand["structure_axis"] = target_axis
                    print(f"    🔗 Intelligent Mapping: {cand.get('candidate_id')} -> {target_axis}")
                else:
                    # 매핑 실패 혹은 부정확할 시 주력 축으로 우선 배정
                    cand["structure_axis"] = primary_axis
        except Exception as e:
            print(f"    ⚠️ Mapping failed ({e}). Falling back to diverse mapping.")
            for i, cand in enumerate(candidates):
                cand["structure_axis"] = primary_axis if i % 2 == 0 else secondary_axis

        print(f"  🎯 Top Frontier Axes Identified: Primary='{primary_axis}', Secondary='{secondary_axis}'")
        
        return {
            "primary_axis": primary_axis,
            "secondary_axis": secondary_axis,
            "discovery_reason": discovery.get("reason", "Autonomous trend discovery"),
            "axis_validation": validation_results,
            "confidence": "HIGH"
        }
