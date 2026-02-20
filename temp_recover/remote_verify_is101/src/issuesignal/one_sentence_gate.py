import re
from pathlib import Path
from typing import Dict, Any, Optional

class OneSentenceGate:
    """
    (IS-19) Enforces editorial clarity via a strict one-sentence template and validation.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.vague_verbs = ["영향", "가능성", "기대", "전망", "우려"]
        self.speculative_endings = ["수 있다", "보인다", "예상된다"]
        self.forced_verb_stems = ["해야", "불가피", "강제"]
        self.time_anchors = ["오늘", "이번 주", "이번 분기", "당장"]

    def process(self, trigger: Dict[str, Any]) -> Optional[str]:
        """
        Attempts to generate and validate a sentence for the trigger.
        Returns the sentence if valid, else None (REJECT).
        """
        # 1. Extract components for the template
        # In a real scenario, this would involve NLP or structured field extraction
        event = trigger.get("event_brief", "")
        actor = trigger.get("actor", "")
        action = trigger.get("forced_action", "")
        bottleneck = trigger.get("bottleneck", "")
        time_anchor = trigger.get("time_anchor", "오늘")

        if not all([event, actor, action, bottleneck]):
            return None

        # 2. Construct the sentence
        sentence = f"{time_anchor} {event} 때문에 {actor}는 {action}을 해야 하고, 자본은 {bottleneck}으로 이동한다."

        # 3. Validate the sentence
        if self._validate(sentence):
            return sentence
        
        return None

    def _validate(self, sentence: str) -> bool:
        """
        Runs all IS-19 validation rules on the generated sentence.
        """
        # Rule: Max 30 characters excluding spaces
        length_no_spaces = len(re.sub(r"\s+", "", sentence))
        if length_no_spaces > 30:
            return False

        # Rule: Check for forced verbs (stems)
        if not any(fvs in sentence for fvs in self.forced_verb_stems):
            return False

        # Rule: Check for time anchors
        if not any(ta in sentence for ta in self.time_anchors):
            return False

        # Rule: No vague verbs
        if any(vv in sentence for vv in self.vague_verbs):
            return False

        # Rule: No speculative endings
        if any(se in sentence for se in self.speculative_endings):
            return False

        # Rule: Must be a single sentence (terminated correctly)
        if sentence.count(".") > 1 or not sentence.endswith("."):
            return False

        return True
