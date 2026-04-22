from typing import List, Dict

class HybridGenerator:
    """[TASK #100.3] Event와 Data Signal을 결합하여 하이브리드 후보 생성"""

    def __init__(self):
        pass

    def generate(self, events: List[Dict], signals: List[Dict]) -> List[Dict]:
        hybrid_candidates = []
        
        for event in events:
            e_type = event.get("event_type")
            e_sectors = event.get("sector_hint", [])
            
            for signal in signals:
                s_type = signal.get("signal_type")
                s_metrics = signal.get("metrics", [])
                
                # Matching logic
                is_match = False
                
                # Case 1: Geopolitical + Oil
                if e_type == "GEOPOLITICAL" and any(m in ["WTI", "Brent"] for m in s_metrics):
                    is_match = True
                
                # Case 2: Supply Shock + Sector move
                if e_type == "SUPPLY_SHOCK" and any(s in ["반도체", "빅테크"] for s in e_sectors) and any(m in ["KOSPI", "SP500"] for m in s_metrics):
                    is_match = True
                
                # Case 3: Policy + Rates/USD
                if e_type == "POLICY" and any(m in ["US10Y", "DXY", "USD_KRW"] for m in s_metrics):
                    is_match = True

                if is_match:
                    hybrid_candidates.append({
                        "candidate_type": "HYBRID",
                        "event": event.get("event"),
                        "signal": signal.get("signal"),
                        "linked_assets": s_metrics,
                        "consistency": "MATCH" if signal.get("z_score", 0) > 0 else "MISMATCH"
                    })
                    
        return hybrid_candidates
