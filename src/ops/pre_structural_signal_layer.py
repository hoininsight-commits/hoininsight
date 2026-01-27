from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.llm.gemini_client import GeminiClient

@dataclass
class PreStructuralSignal:
    signal_type: str  # Deadline / Verbal / Capital / Dependency
    trigger_actor: str # Who caused the tension
    temporal_anchor: str # Date, window, or conditional deadline
    unresolved_question: str # What the market does NOT know yet
    expected_market_behavior: str  # risk_off, rotation, speculation, freeze
    escalation_path: Dict[str, str]  # condition_to_upgrade_to_WHY_NOW, condition_to_invalidate
    rationale: str
    is_valid: bool = False

class PreStructuralSignalLayer:
    """
    STEP 74: Pre-Structural Signal Layer (Economic Hunter Style).
    Detects early narrative-driven market shifts before WHY_NOW confirmation.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        try:
            self.llm = GeminiClient()
        except Exception as e:
            self.llm = None
            print(f"[PreStructuralSignalLayer] Warning: GeminiClient init failed ({e}).")

    def analyze_topics(self, topics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Scan candidate topics for Pre-Structural Signals.
        """
        results = []
        for topic in topics:
            signal = self._detect_signal(topic)
            if signal and signal.is_valid:
                topic["pre_structural_signal"] = asdict(signal)
                topic["is_pre_structural"] = True
            else:
                topic["is_pre_structural"] = False
            results.append(topic)
        return results

    def _detect_signal(self, topic: Dict[str, Any]) -> Optional[PreStructuralSignal]:
        if not self.llm:
            return self._heuristic_detect(topic)
        
        prompt = self._build_prompt(topic)
        response = self.llm.generate_content(prompt)
        
        if not response:
            return self._heuristic_detect(topic)
            
        return self._parse_llm_response(response)

    def _build_prompt(self, topic: Dict[str, Any]) -> str:
        title = topic.get("title", "Unknown")
        rationale = topic.get("rationale", "")
        evidence = str(topic.get("evidence", ""))
        
        return f"""
You are HOIN ENGINE Step 74 (Pre-Structural Signal Detector).
Your task is to detect if the following topic is a "Pre-Structural Signal".

### DEFINITION: PRE-STRUCTURAL SIGNAL
A market-moving event where narrative, expectation, or deadline pressure begins reallocating capital BEFORE legal, policy, or earnings confirmation.
These are NOT continuous states. They MUST have a temporal or structural anchor.

### ALLOWED TYPES:
1. Deadline Pressure (Budget/Vote/Cutoff)
2. Verbal Commitment (Official statement/warning/threat)
3. Capital Flow Anticipation (Anticipatory reallocation/rotation)
4. Structural Dependency Exposure (Supply-chain choke points/exposed risks)

### EXCLUSION CRITERIA (REJECT IF):
- "Growing industry", "Undervalued", "Future potential" (General trends)
- NO deadline, NO actor, NO statement, NO specific scenario.
- Same narrative applies after 30 days.

### TOPIC DATA:
- Title: {title}
- Rationale: {rationale}
- Evidence: {evidence}

### OUTPUT FORMAT (JSON ONLY):
{{
  "is_valid": true/false,
  "signal_type": "Deadline" | "Verbal" | "Capital" | "Dependency",
  "trigger_actor": "string",
  "temporal_anchor": "string (date/window/deadline)",
  "unresolved_question": "string",
  "expected_market_behavior": "risk_off" | "rotation" | "speculation" | "freeze",
  "escalation_path": {{
    "condition_to_upgrade_to_WHY_NOW": "string",
    "condition_to_invalidate": "string"
  }},
  "rationale": "KOREAN summary of why this is a pre-structural signal"
}}
"""

    def _parse_llm_response(self, response: str) -> Optional[PreStructuralSignal]:
        try:
            # Clean possible markdown code blocks
            clean_res = re.sub(r'```json|```', '', response).strip()
            data = json.loads(clean_res)
            
            if not data.get("is_valid"):
                return None
                
            return PreStructuralSignal(
                signal_type=data.get("signal_type", "Unknown"),
                trigger_actor=data.get("trigger_actor", "Unknown"),
                temporal_anchor=data.get("temporal_anchor", "Unknown"),
                unresolved_question=data.get("unresolved_question", "Unknown"),
                expected_market_behavior=data.get("expected_market_behavior", "speculation"),
                escalation_path=data.get("escalation_path", {}),
                rationale=data.get("rationale", ""),
                is_valid=True
            )
        except Exception as e:
            print(f"[PreStructuralSignalLayer] Parse error: {e}")
            return None

    def _heuristic_detect(self, topic: Dict[str, Any]) -> Optional[PreStructuralSignal]:
        # Very simple fallback logic
        rationale = topic.get("rationale", "").lower()
        
        # Look for deadline keywords
        deadline_kws = ["deadline", "마감", "투표", "일정", "발표 예정"]
        for kw in deadline_kws:
            if kw in rationale:
                return PreStructuralSignal(
                    signal_type="Deadline",
                    trigger_actor="Market Schedule",
                    temporal_anchor="Approaching Deadline",
                    unresolved_question="Will the event happen as expected?",
                    expected_market_behavior="rotation",
                    escalation_path={
                        "condition_to_upgrade_to_WHY_NOW": "Event occurs/announced",
                        "condition_to_invalidate": "Event delayed/cancelled"
                    },
                    rationale="Heuristic detection based on deadline keywords.",
                    is_valid=True
                )
        return None
