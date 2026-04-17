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
    narrative_pressure_score: int = 0  # 0-100 score
    related_entities: List[str] = field(default_factory=list) # Countries, companies, industries
    rationale: str = ""
    is_valid: bool = False

class PreStructuralSignalLayer:
    """
    STEP 74: Pre-Structural Signal Layer (Economic Hunter Style).
    Detects early narrative-driven market shifts before WHY_NOW confirmation.
    """
    BATCH_SIZE = 15
    ABSOLUTE_VALUE_PATTERNS = [
        r'\d+원',      # 환율 XXX원
        r'\$\d+',      # $XX 돌파 (유가 등)
        r'\d+%.*돌파',  # XX% 돌파
        r'역대\s*최',   # 역대 최고/최저
    ]

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        try:
            self.llm = GeminiClient()
        except Exception as e:
            self.llm = None
            print(f"[PreStructuralSignalLayer] Warning: GeminiClient init failed ({e}).")

    def analyze_topics(self, topics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Scan candidate topics for Pre-Structural Signals using Batch Processing.
        """
        if not topics:
            return []

        # 1. Pre-filter trivial absolute value topics
        eligible_topics, skipped_topics = self._pre_filter_topics(topics)
        
        # 2. Process eligible topics in batches
        all_results = []
        if self.llm and eligible_topics:
            print(f"  🧠 [Step 74] Analyzing {len(eligible_topics)} eligible topics in batches of {self.BATCH_SIZE}...")
            for i in range(0, len(eligible_topics), self.BATCH_SIZE):
                batch = eligible_topics[i : i + self.BATCH_SIZE]
                batch_results = self._analyze_batch(batch)
                all_results.extend(batch_results)
                print(f"  ✅ [Step 74] 배치 {i // self.BATCH_SIZE + 1} 완료 ({len(batch)}개)")
        else:
            # Fallback to heuristics for all eligible if LLM unavailable
            for t in eligible_topics:
                sig = self._heuristic_detect(t)
                all_results.append({"is_valid": sig.is_valid if sig else False, "signal": sig})

        # 3. Re-assemble final list
        final_list = []
        
        # Mapping results back to eligible topics
        for idx, topic in enumerate(eligible_topics):
            res = all_results[idx] if idx < len(all_results) else {"is_valid": False}
            if res.get("is_valid"):
                # Handle both dict (from LLM) and dataclass (from heuristic)
                sig_data = res.get("signal")
                if isinstance(sig_data, PreStructuralSignal):
                    topic["pre_structural_signal"] = asdict(sig_data)
                elif isinstance(res, dict) and "signal_type" in res:
                    topic["pre_structural_signal"] = res
                else: 
                     # Fallback mapping if single res object returned
                     topic["pre_structural_signal"] = res
                
                topic["is_pre_structural"] = True
            else:
                topic["is_pre_structural"] = False
            final_list.append(topic)

        # Mark skipped topics
        for topic in skipped_topics:
            topic["is_pre_structural"] = False
            final_list.append(topic)

        return final_list

    def _pre_filter_topics(self, topics: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Separate topics into LLM-eligible and trivial/skipped cases."""
        eligible = []
        skipped = []
        for t in topics:
            t_str = f"{t.get('title', '')} {t.get('rationale', '')}"
            is_absolute = any(re.search(p, t_str) for p in self.ABSOLUTE_VALUE_PATTERNS)
            if is_absolute:
                skipped.append(t)
            else:
                eligible.append(t)
        
        if skipped:
            print(f"  🚿 [Step 74] Heuristic Filter: {len(skipped)} trivial topics skipped.")
        return eligible, skipped

    def _analyze_batch(self, batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Call Gemini for a batch of topics."""
        prompt = self._build_batch_prompt(batch)
        try:
            # use call_json for reliability
            response_json = self.llm.call_json(prompt, max_tokens=3000)
            if isinstance(response_json, list):
                # Ensure it's sorted by index if LLM returned out of order
                sorted_results = sorted(response_json, key=lambda x: x.get("index", 0))
                return sorted_results
            return [{"is_valid": False}] * len(batch)
        except Exception as e:
            print(f"  ❌ Batch call failed: {e}")
            return [{"is_valid": False}] * len(batch)

    def _build_batch_prompt(self, batch: List[Dict[str, Any]]) -> str:
        batch_items = []
        for idx, t in enumerate(batch):
            item = f"[{idx+1}] Title: {t.get('title')}\nRationale: {t.get('rationale')}\nEvidence: {str(t.get('evidence'))[:500]}"
            batch_items.append(item)

        batch_text = "\n\n---\n\n".join(batch_items)

        return f"""
You are HOIN ENGINE Step 74 (Pre-Structural Signal Detector).
Evaluate the following {len(batch)} topic candidates.

### DEFINITION: PRE-STRUCTURAL SIGNAL
A market-moving event where narrative, expectation, or deadline pressure begins reallocating capital BEFORE legal, policy, or earnings confirmation.
Must have a temporal/structural anchor (Deadline, Verbal Commitment, Capital Rotation, or Dependency Exposure).

### EVALUATION CRITERIA:
- REJECT if general "Growth", "Future potential", or purely price-based without context.
- REJECT if the reason is "Exchange rate broke XXXX level" without describing the structural tension.

### TOPICS TO EVALUATE:
{batch_text}

### OUTPUT FORMAT (JSON ARRAY ONLY):
Output a JSON array of exactly {len(batch)} objects, each matching this structure:
{{
  "index": 1,
  "is_valid": true|false,
  "signal_type": "Deadline" | "Verbal" | "Capital" | "Dependency",
  "trigger_actor": "Who is driving this",
  "temporal_anchor": "Deadline or event window",
  "unresolved_question": "What is undecided?",
  "expected_market_behavior": "risk_off" | "rotation" | "speculation" | "freeze",
  "escalation_path": {{
    "condition_to_upgrade_to_WHY_NOW": "string",
    "condition_to_invalidate": "string"
  }},
  "narrative_pressure_score": 0-100,
  "rationale": "KOREAN short summary"
}}
"""

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
  "narrative_pressure_score": 0-100,
  "related_entities": ["list", "of", "entities"],
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
                narrative_pressure_score=data.get("narrative_pressure_score", 0),
                related_entities=data.get("related_entities", []),
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
