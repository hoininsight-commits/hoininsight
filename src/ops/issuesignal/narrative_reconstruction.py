from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json
import logging

class NarrativeReconstructionEngine:
    """
    IS-50: Narrative Reconstruction Engine
    Retrieves past cases and generates structured narratives based on historical patterns.
    Strictly prohibits speculation and uses only data-driven declarative sentences.
    """

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.decision_dir = base_dir / "data" / "decision"
        self.logger = logging.getLogger("NarrativeReconstruction")

    def reconstruct(self, current_card: Dict) -> Optional[Dict]:
        """
        Main entry point.
        Returns a structured narrative dict if past cases found, else None.
        """
        # 1. Retrieve Past Cases
        past_cases = self._retrieve_past_cases(current_card)
        if not past_cases:
            return None

        # 2. Summarize Outcome (Using the most relevant case)
        best_case = past_cases[0]
        summary = self._summarize_outcome(best_case)

        # 3. Infer Behavior Pattern
        pattern_tag = self._infer_behavior_pattern(current_card, past_cases)

        # 4. Generate Narrative Block
        narrative_text = self._generate_narrative_block(current_card, best_case, summary, pattern_tag)

        return {
            "past_case_id": best_case.get("topic_id", "UNKNOWN"),
            "pattern_tag": pattern_tag,
            "narrative_text": narrative_text,
            "similarity_score": best_case.get("_score", 0),
            "reference_date": best_case.get("_date", "UNKNOWN")
        }

    def _retrieve_past_cases(self, current_card: Dict) -> List[Dict]:
        """
        Searches data/decision for similar cases.
        Simple heuristic matching based on Actor and Asset keywords.
        """
        candidates = []
        if not self.decision_dir.exists():
            return []

        curr_actor = current_card.get("actor", "").upper()
        curr_assets = [t.get("ticker", "").upper() for t in current_card.get("tickers", [])]
        curr_context = current_card.get("trigger_type", "").upper()

        # Recursive search for JSONs
        for f in self.decision_dir.glob("**/*/final_decision_card.json"):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                
                # Exclude self
                if data.get("topic_id") == current_card.get("topic_id"):
                    continue

                score = 0
                # Actor Match (40%)
                if data.get("actor", "").upper() == curr_actor:
                    score += 40
                
                # Asset Match (30%) - Check overlapping tickers
                past_tickers = [t.get("ticker", "").upper() for t in data.get("tickers", [])]
                if set(curr_assets) & set(past_tickers):
                    score += 30
                
                # Context Match (30%)
                if data.get("trigger_type", "").upper() == curr_context:
                    score += 30

                if score >= 60: # Threshold
                    # Extract date from path
                    # Path: .../YYYY/MM/DD/final_decision_card.json
                    parts = f.parts
                    if len(parts) >= 5:
                        data["_date"] = f"{parts[-4]}-{parts[-3]}-{parts[-2]}"
                    data["_score"] = score
                    candidates.append(data)

            except Exception as e:
                continue

        # Sort by score desc, then date desc
        candidates.sort(key=lambda x: (x.get("_score", 0), x.get("_date", "")), reverse=True)
        return candidates[:3]

    def _summarize_outcome(self, past_case: Dict) -> Dict:
        """
        Summarizes action, outcome, verdict from past card.
        If structured outcome data missing, infers from text fields.
        """
        # Simplistic extraction for now - envisioning structured feedback loop in IS-50+
        action = past_case.get("one_liner", "알 수 없는 조치")
        
        # Try to find outcome in raw_data or infer from status
        status = past_case.get("status", "UNKNOWN")
        verdict = "성공" if status == "TRUST_LOCKED" else "실패"
        
        outcome_desc = "시장은 이에 반응했다" # Default
        if status == "REJECT":
            outcome_desc = "시장의 거부 반응이 있었다"
        elif status == "TRUST_LOCKED":
             outcome_desc = "시장은 즉각적으로 반응했다"

        return {
            "action": action,
            "outcome": outcome_desc,
            "verdict": verdict
        }

    def _infer_behavior_pattern(self, current_card: Dict, past_cases: List[Dict]) -> str:
        """
        Infers patterns like TRAUMA_REPEAT based on repetition.
        """
        actor = current_card.get("actor", "UNKNOWN")
        
        if len(past_cases) >= 2:
            # Check if recent outcomes were negative
            fail_count = sum(1 for c in past_cases if c.get("status") != "TRUST_LOCKED")
            if fail_count >= 2:
                return "트라우마_반복 (TRAUMA_REPEAT)"
            else:
                return "구조적_관성 (STRUCTURAL_INERTIA)"
        
        return "단발성_대응 (SINGLE_EVENT)"

    def _generate_narrative_block(self, current: Dict, past: Dict, summary: Dict, pattern: str) -> str:
        """
        Generates the 4-step narrative block.
        """
        actor = current.get("actor", "주체")
        year = past.get("_date", "과거")[:4]
        
        # 4-Step Construction
        lines = []
        
        # 1. Past
        lines.append(f"**[과거]** {year}년에도 {actor}는 동일한 맥락에서 '{summary['action']}' 조치를 취했다.")
        
        # 2. Result
        lines.append(f"**[결과]** 당시 {summary['outcome']}고, 이는 {summary['verdict']}적인 판단으로 판명됐다.")
        
        # 3. Pattern
        lines.append(f"**[패턴]** 데이터상 {actor}는 유사 위기마다 '{pattern}' 경향을 보임이 입증됐다.")
        
        # 4. Current Connection
        lines.append(f"**[현재]** 따라서 현재의 움직임 역시 선택이 아닌, 과거 패턴의 구조적 연장선이다.")
        
        return "\n".join(lines)
