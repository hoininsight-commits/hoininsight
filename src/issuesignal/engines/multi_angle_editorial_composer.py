from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from pathlib import Path

class MultiAngleEditorialComposer:
    """
    (IS-92) Multi-Angle Editorial Composer.
    Composes 3 editorial slots with different 'angles' (Structure, Schedule, Person, Anomaly).
    Ensures diversity in market interpretation.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def compose(self, candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Input: List of Narrative Candidates (IS-86/88/89/90)
        Output: Multi-Angle Editorial Structure (3 slots)
        """
        # 1. Classify Candidates by Angles
        angled_candidates = self._classify(candidates)
        
        # 2. Select Slots
        slots = []
        selected_ids = set()
        
        # Slot 1: ANGLE_STRUCTURE (Required)
        s1 = self._pick_candidate(angled_candidates, "STRUCTURE", selected_ids)
        if s1:
            slots.append(self._to_slot_format(s1, "SLOT-1", "STRUCTURE"))
            selected_ids.add(s1["id"])
            
        # Slot 2: ANGLE_SCHEDULE or ANGLE_PERSON (Required)
        s2 = self._pick_candidate(angled_candidates, ["SCHEDULE", "PERSON"], selected_ids, last_slot=slots[0] if slots else None)
        if s2:
            angle = "SCHEDULE" if "SCHEDULE" in s2["angles"] else "PERSON"
            slots.append(self._to_slot_format(s2, "SLOT-2", angle))
            selected_ids.add(s2["id"])
            
        # Slot 3: ANGLE_ANOMALY or ANGLE_PERSON (Required)
        s3 = self._pick_candidate(angled_candidates, ["ANOMALY", "PERSON"], selected_ids, last_slot=slots[-1] if slots else None)
        if s3:
            angle = "ANOMALY" if "ANOMALY" in s3["angles"] else "PERSON"
            slots.append(self._to_slot_format(s3, "SLOT-3", angle))
            selected_ids.add(s3["id"])
            
        # 3. Final Result
        ymd = datetime.now().strftime("%Y-%m-%d")
        result = {
            "date": ymd,
            "slots": slots,
            "count": len(slots),
            "footer_disclaimer": "본 섹션은 하나의 정답이 아닌, 서로 다른 시점에서 시장을 바라보기 위한 해석 구도입니다."
        }
        
        # Save output
        out_dir = self.base_dir / "data" / "editorial"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"multi_angle_editorial_{ymd}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=4, ensure_ascii=False)
            
        return result

    def _classify(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Adds 'angles' field to each candidate based on metadata.
        """
        for cand in candidates:
            angles = []
            smix = cand.get("source_mix", [])
            dtype = cand.get("dominant_type", "")
            
            if dtype == "STRUCTURE" or "structure" in smix:
                angles.append("STRUCTURE")
            if dtype == "PREVIEW" or "schedule" in smix:
                angles.append("SCHEDULE")
            if "statement" in smix or "person" in smix:
                angles.append("PERSON")
            if "anomaly" in smix:
                angles.append("ANOMALY")
                
            cand["angles"] = angles
        return candidates

    def _pick_candidate(self, candidates: List[Dict[str, Any]], target_angles, excluded_ids, last_slot=None) -> Optional[Dict[str, Any]]:
        """
        Picks the best candidate matching target_angles with diversity constraints.
        """
        if isinstance(target_angles, str):
            target_angles = [target_angles]
            
        # Filter matching
        matches = [c for c in candidates if c["id"] not in excluded_ids and any(a in target_angles for a in c["angles"])]
        
        # Diversity Constraint: No same angle as last_slot, No same asset (simple entity check)
        final_matches = []
        for m in matches:
            if last_slot:
                # Angle check
                m_angles = m["angles"]
                if last_slot["angle"] in m_angles:
                    continue
                # Simple Entity Check (Mock logic: entities should be different)
                # In real scenario, would check m.get('entity')
                
            final_matches.append(m)
            
        if not final_matches:
            # Fallback to matches if constraints too strict
            return matches[0] if matches else None
            
        return final_matches[0]

    def _to_slot_format(self, cand: Dict[str, Any], slot_id: str, angle: str) -> Dict[str, Any]:
        return {
            "slot_id": slot_id,
            "angle": angle,
            "source_id": cand["id"],
            "title": cand.get("theme", "No Title"),
            "why_now": cand.get("why_now", "No Rational"),
            "recommended_format": cand.get("promotion_hint", "DAILY_LONG"),
            "disclaimer": "본 콘텐츠는 자산 추천이 아닌 구조적 관찰입니다."
        }
