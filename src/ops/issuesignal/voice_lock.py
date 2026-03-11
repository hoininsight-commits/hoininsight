import re
from typing import Dict, Any, List

class VoiceLockEngine:
    """
    IS-39: HUMAN_VOICE_LOCK_ENGINE
    Enforces a single, consistent human speaker identity for all outputs.
    """

    CERTAINTY_MAP = {
        r"가능성이 있다": "이미 결정됐다",
        r"전망된다": "분석 결과는 하나다",
        r"일 수 있다": "해야 한다",
        r"볼 수 있다": "구조적 필연이다",
        r"필요해 보인다": "선택지는 없다",
        r"것으로 보인다": "현상은 명확하다",
        r"유의해야 한다": "즉시 실행해야 한다"
    }

    FORBIDDEN_ENDINGS = [r"\?", r"나요", r"까요", r"가요", r"할지"]

    MANDATED_STEPS = [
        "## 1. 정의",
        "## 2. 표면 해석",
        "## 3. 시장의 오해",
        "## 4. 구조적 강제",
        "## 5. 결론"
    ]

    def apply_lock(self, content: str) -> Dict[str, Any]:
        """
        Locks the voice of the provided content.
        Returns the locked content and a consistency flag.
        """
        if not content:
            return {"locked_content": "", "voice_consistent": False}

        # 1. Enforce Certainty Language
        locked = content
        for pattern, replacement in self.CERTAINTY_MAP.items():
            locked = re.sub(pattern, replacement, locked)

        # 2. Enforce Sentence Rhythm (Short, Declarative)
        locked = self._shorten_sentences(locked)

        # 3. Clean Filler and English (Heuristic)
        locked = self._remove_filler(locked)

        # 4. Validate Structure
        is_consistent = self._validate_structure(locked)

        return {
            "locked_content": locked,
            "voice_consistent": is_consistent
        }

    def _shorten_sentences(self, text: str) -> str:
        """Splits long sentences and ensures no questions."""
        # Split by punctuation but keep it
        text = text.replace("?", ".") # Force all questions to periods first
        
        sentences = re.split(r"([.\n])", text)
        result = []
        for i in range(0, len(sentences)-1, 2):
            s = sentences[i].strip()
            p = sentences[i+1]
            
            if not s: continue
            
            # Remove question endings
            if s.endswith(("까요", "나요", "가요", "한지")):
                s = re.sub(r"(까요|나요|가요|한지)$", "다", s)
            
            # Always replace softening conjunctions
            s = s.replace(" 때문에 ", ". 이유는 ")
            s = s.replace(" 하고 ", ". " )
            
            result.append(s + p)
        
        # If last part remained
        if len(sentences) % 2 == 1 and sentences[-1].strip():
            s_last = sentences[-1].strip()
            s_last = s_last.replace(" 때문에 ", ". 이유는 ")
            result.append(s_last + ".")

        final = " ".join(result).replace("\n ", "\n").replace("  ", " ").replace(" .", ".")
        return final.strip()

    def _remove_filler(self, text: str) -> str:
        """Removes common filler words to increase density."""
        fillers = ["사실 ", "아마도 ", "상당히 ", "매우 ", "혹시 ", "어쩌면 "]
        for f in fillers:
            text = text.replace(f, "")
        return text

    def _validate_structure(self, content: str) -> bool:
        """Checks if all 5 steps are present."""
        missing = [step for step in self.MANDATED_STEPS if step not in content]
        return len(missing) == 0
