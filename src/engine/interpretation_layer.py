
import json
from pathlib import Path

class InterpretationLayer:
    """[TASK #087] EVENT INTERPRETATION LAYER
    이벤트를 '정상 시장 반응 (NORMAL FLOW)'으로 변환
    """
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def interpret_events(self, events: list) -> list:
        interpretations = []
        for e in events:
            e_type = e.get("type", "UNKNOWN")
            impact = e.get("impact_score", 0.5)
            event_name = e.get("event", "")
            
            normal_flow = {
                "expected_reactions": [],
                "implications": []
            }
            
            # Rule-based mapping
            if e_type == "SUPPLY_SHOCK":
                normal_flow["expected_reactions"] = [
                    {"asset": "commodity", "direction": "UP"},
                    {"asset": "vix", "direction": "UP"}
                ]
                normal_flow["implications"].append("공급 차질로 인한 가격 상승 압력")
                
            elif e_type == "GEOPOLITICAL":
                # 제목에서 긴장 완화 여부 판단 (단순 로직)
                if any(k in event_name for k in ["휴전", "협상", "해소", "진전", "종료"]):
                    normal_flow["expected_reactions"] = [
                        {"asset": "oil", "direction": "DOWN"},
                        {"asset": "vix", "direction": "DOWN"},
                        {"asset": "gold", "direction": "DOWN"},
                        {"asset": "equity", "direction": "UP"}
                    ]
                    normal_flow["implications"].append("불확실성 해소로 인한 리스크 온(Risk-on)")
                else:
                    normal_flow["expected_reactions"] = [
                        {"asset": "oil", "direction": "UP"},
                        {"asset": "vix", "direction": "UP"},
                        {"asset": "gold", "direction": "UP"},
                        {"asset": "equity", "direction": "DOWN"}
                    ]
                    normal_flow["implications"].append("지정학적 긴장 고조로 인한 안전자산 선호")
                    
            elif e_type == "POLICY":
                if any(k in event_name for k in ["긴축", "인상", "매파", "동결"]):
                    normal_flow["expected_reactions"] = [
                        {"asset": "equity", "direction": "DOWN"},
                        {"asset": "dollar", "direction": "UP"},
                        {"asset": "bond_yield", "direction": "UP"}
                    ]
                    normal_flow["implications"].append("유동성 흡수 및 금리 상승 사이클")
                else:
                    normal_flow["expected_reactions"] = [
                        {"asset": "equity", "direction": "UP"},
                        {"asset": "dollar", "direction": "DOWN"},
                        {"asset": "bond_yield", "direction": "DOWN"}
                    ]
                    normal_flow["implications"].append("완화적 정책 기대로 인한 시장 부양")
                    
            elif e_type == "EARNINGS":
                if impact > 0.7:
                    normal_flow["expected_reactions"] = [{"asset": "sector_equity", "direction": "UP"}]
                    normal_flow["implications"].append("실적 서프라이즈로 인한 펀더멘털 강화")
                else:
                    normal_flow["expected_reactions"] = [{"asset": "sector_equity", "direction": "DOWN"}]
                    normal_flow["implications"].append("실적 부진으로 인한 밸류에이션 하락")

            elif e_type == "LIQUIDITY":
                normal_flow["expected_reactions"] = [
                    {"asset": "equity", "direction": "DOWN"},
                    {"asset": "vix", "direction": "UP"}
                ]
                normal_flow["implications"].append("시장 유동성 충격 및 패닉 셀링")

            interpretations.append({
                "event": event_name,
                "type": e_type,
                "impact_score": impact,
                "normal_flow": normal_flow
            })
            
        # 결과 저장
        save_path = self.output_dir / "event_normal_flow.json"
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(interpretations, f, ensure_ascii=False, indent=2)
            
        return interpretations
