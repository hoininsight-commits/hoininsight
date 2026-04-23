
from typing import List, Dict

class AxisDetector:
    """[TASK #103] Market Axis Detector (v2.0 - Axis-First Selection)"""

    AXIS_MAP = {
        "rates": ["us10y", "us2y", "fed_funds"],
        "liquidity": ["usd_krw", "vix", "hyg"],
        "geopolitics": ["wti_oil", "gold", "vix"],
        "supply_chain": ["wti_oil", "brent", "freight_index"],
        "policy": ["us10y", "fed_funds", "sp500"],
        "flow": ["nasdaq", "sp500", "kospi"]
    }

    # Event Type to Axis mapping
    TYPE_TO_AXIS = {
        "POLICY": "rates",
        "GEOPOLITICAL": "geopolitics",
        "SUPPLY_SHOCK": "supply_chain",
        "LIQUIDITY": "liquidity",
        "EARNINGS": "flow"
    }

    # Directional Consistency Rules (v2.1)
    # (Asset1, Asset2, same_direction: bool)
    CONSISTENCY_RULES = {
        "rates": [("us10y", "us2y", True), ("us10y", "usd_krw", True)],
        "geopolitics": [("wti_oil", "gold", True), ("wti_oil", "vix", True)],
        "liquidity": [("vix", "hyg", False), ("usd_krw", "kospi", False)],
        "supply_chain": [("wti_oil", "brent", True)],
        "policy": [("us10y", "nasdaq", False)],
        "flow": [("nasdaq", "sp500", True), ("kospi", "usd_krw", False)]
    }

    def __init__(self):
        pass

    def validate_axis(self, axis: str, stats: Dict) -> Dict:
        """
        [STEP 0.5] Axis Validation (v3 Simplified)
        """
        assets = self.AXIS_MAP.get(axis, [])
        valid_stats = {a: stats[a] for a in assets if a in stats}
        
        if not valid_stats:
            return {"passed": False, "reason": "no_data", "direction_consistent": True, "reaction": False, "recent": False}
        
        # 2-1. Reaction Check
        reaction = any(abs(s.get("z_score_20d", 0)) > 1.2 or abs(s.get("chg_5d", 0)) > 0.8 for s in valid_stats.values())
        
        # 2-2. Direction Check (v3: Reference only, not a fail condition)
        consistent = True
        rules = self.CONSISTENCY_RULES.get(axis, [])
        for a1, a2, same in rules:
            if a1 in stats and a2 in stats:
                chg1, chg2 = stats[a1].get("chg_5d", 0), stats[a2].get("chg_5d", 0)
                if abs(chg1) > 0.1 and abs(chg2) > 0.1:
                    if same and chg1 * chg2 < 0: consistent = False
                    if not same and chg1 * chg2 > 0: consistent = False
        
        # 2-3. Timing Check
        recent = any(abs(s.get("z_score_20d", 0)) > 1.0 for s in valid_stats.values())
        
        # [v3 RULE] Passed is only reaction AND recent. Direction is bonus/info.
        passed = reaction and recent
        
        return {
            "passed": passed,
            "reaction": reaction,
            "direction_consistent": consistent,
            "recent": recent,
            "score": 1.0 if passed else 0.2
        }

    def detect_market_axis(self, candidates: List[Dict], market_data: Dict) -> Dict:
        """
        [v3] 오늘 시장을 설명하는 핵심 축을 선정합니다.
        - Primary: Validation을 통과한 축 중에서만 선정
        - Secondary: Validation 통과 여부와 상관없이 차순위 선정
        """
        stats = market_data.get("multi_period_stats", {})
        
        # 1. 자산 반응 기반 축별 강도 계산
        axis_intensity = {axis: 0.0 for axis in self.AXIS_MAP}
        for axis, assets in self.AXIS_MAP.items():
            scores = [abs(stats[a].get("z_score_20d", 0)) + abs(stats[a].get("chg_5d", 0)) * 2 
                     for a in assets if a in stats]
            if scores:
                axis_intensity[axis] = max(scores)

        # 2. Axis Validation
        validation_results = {}
        for axis in self.AXIS_MAP:
            validation_results[axis] = self.validate_axis(axis, stats)

        # 3. 후보군 밀도 계산
        axis_density = {axis: 0 for axis in self.AXIS_MAP}
        axis_density["emerging"] = 0 # [v3] 신규 부상 축
        
        for cand in candidates:
            event_type = cand.get("actual_paths", [None])[0]
            axis = self.TYPE_TO_AXIS.get(event_type)
            
            # [NEW] DATA 후보군이나 매핑되지 않은 타입을 위해 자산 기반 역매핑 시도
            if not axis:
                facts = cand.get("core_facts", [])
                if facts:
                    asset_name = facts[0].get("name")
                    for a_name, assets in self.AXIS_MAP.items():
                        if asset_name in assets:
                            axis = a_name
                            break
            
            if not axis:
                axis = "emerging"
                
            if axis in axis_density:
                axis_density[axis] += 1
            else:
                axis_density["emerging"] += 1
                axis = "emerging"
            cand["structure_axis"] = axis

        # 4. 축별 점수 산정
        final_scores = []
        # v3: 'emerging' 축은 validation 생략하고 기본 통과로 처리할 수 있음
        validation_results["emerging"] = {"passed": True, "reaction": True, "direction_consistent": True, "recent": True, "score": 1.0, "reason": "emerging_axis"}
        for axis in list(self.AXIS_MAP.keys()) + ["emerging"]:
            v = validation_results.get(axis, {"passed": False, "direction_consistent": False})
            # [v3] direction_consistent는 점수에만 살짝 반영
            total_score = (axis_intensity.get(axis, 0.0) * 0.5) + (axis_density.get(axis, 0.0) * 0.3)
            if v["direction_consistent"]:
                total_score += 1.0
            
            final_scores.append((axis, total_score, v["passed"]))
            
        final_scores.sort(key=lambda x: x[1], reverse=True)
        
        # 5. [v3 RULE] Primary는 반드시 passed=True 여야 함
        passed_axes = [x for x in final_scores if x[2]]
        
        if passed_axes:
            primary = passed_axes[0][0]
            # Secondary는 Primary를 제외한 전체 중 1위
            remaining = [x for x in final_scores if x[0] != primary]
            secondary = remaining[0][0] if remaining else "geopolitics"
        else:
            # [Fallback] 통과한 축이 없으면 가장 강한 축을 Primary로 하되 LOW confidence
            primary = final_scores[0][0] if final_scores else "rates"
            secondary = final_scores[1][0] if len(final_scores) > 1 else "geopolitics"
            
        # 6. [v3.1] Re-alignment pass: Primary/Secondary 축 소속 자산이면 축 재조정
        for cand in candidates:
            facts = cand.get("core_facts", [])
            if facts:
                asset_name = facts[0].get("name")
                if asset_name in self.AXIS_MAP.get(primary, []):
                    cand["structure_axis"] = primary
                elif asset_name in self.AXIS_MAP.get(secondary, []):
                    cand["structure_axis"] = secondary
        
        confidence = "HIGH" if validation_results[primary]["passed"] else "LOW"
        
        return {
            "primary_axis": primary,
            "secondary_axis": secondary,
            "axis_validation": validation_results,
            "confidence": confidence
        }


