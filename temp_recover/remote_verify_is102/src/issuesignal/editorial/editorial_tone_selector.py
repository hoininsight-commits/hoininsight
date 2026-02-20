import json
from pathlib import Path
from typing import List, Dict, Any

class EditorialToneSelector:
    """
    (IS-83) Editorial Tone & Script Mode Selector.
    Determines 'HOW' to speak about a topic (Tone/Mode) based on its characteristics.
    """
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        
    def process(self, promoted_path: Path):
        """
        Reads candidate list, enriches with Tone/Mode, saves back.
        """
        if not promoted_path or not promoted_path.exists():
            print(f"[ToneSelector] Path not found: {promoted_path}")
            return

        try:
            data = json.loads(promoted_path.read_text(encoding="utf-8"))
            candidates = data.get("candidates", [])
            
            updated_candidates = []
            for c in candidates:
                enriched = self._enrich_candidate(c)
                updated_candidates.append(enriched)
                
            data["candidates"] = updated_candidates
            
            # Save back (Atomic update conceptually)
            with open(promoted_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            print(f"[ToneSelector] Enriched {len(updated_candidates)} candidates with Tone/Mode.")
            
        except Exception as e:
            print(f"[ToneSelector] Failed to process candidates: {e}")

    def _enrich_candidate(self, candidate: Dict) -> Dict:
        """Assign Tone Type and Script Mode based on candidate properties."""
        
        # Default
        tone_type = "STRUCTURAL"
        script_mode = "EXPLANATION"
        hook_style = "지금 시장에서는 조용하지만 중요한 변화가 일어나고 있습니다."
        
        # Extract features
        category = candidate.get("category", "")
        reason = candidate.get("reason", "")
        
        # Rule 1: WARNING (Risk/Trigger based)
        # Mock logic: checking for 'Risk' or 'Warning' in reason
        if "Risk" in reason or "Warning" in reason or "Conflict" in reason:
            tone_type = "WARNING"
            script_mode = "ALERT"
            hook_style = "지금 시장에서 가장 위험한 신호는 …"

        # Rule 2: PREVIEW (Schedule based)
        elif "PREVIEW" in category or "Schedule" in reason:
            tone_type = "PREVIEW"
            script_mode = "HEADS_UP"
            hook_style = "이번 주 시장에서 반드시 체크해야 할 일정은 …"

        # Rule 3: SCENARIO (Conditional)
        elif "SCENARIO" in category or "If" in reason or "Scenario" in reason:
            tone_type = "SCENARIO"
            script_mode = "WHAT_IF"
            hook_style = "만약 이 흐름이 이어진다면, 시장은 전혀 다른 방향으로 움직일 수 있습니다."

        # Rule 4: STRUCTURAL (Default or Explicit)
        elif "STRUCTURE" in category or "Structural" in reason:
            tone_type = "STRUCTURAL"
            script_mode = "EXPLANATION"
            hook_style = "지금 시장에서는 조용하지만 중요한 변화가 일어나고 있습니다."

        # Assign to candidate
        candidate["tone_type"] = tone_type
        candidate["script_mode"] = script_mode
        candidate["opening_hook_style"] = hook_style
        
        return candidate
