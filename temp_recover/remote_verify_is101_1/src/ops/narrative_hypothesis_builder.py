from __future__ import annotations
import json
import uuid
from pathlib import Path
from typing import List, Dict, Any

class NarrativeHypothesisBuilder:
    """
    Transforms STRUCTURAL TOPIC SEEDS into Narrative Hypotheses.
    Neutral, fact-grounded structural explanation.
    """

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.output_path = base_dir / "data" / "ops" / "narrative_hypotheses.json"
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

    def build_hypotheses(self, seeds: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Maps each Topic Seed to exactly ONE Narrative Hypothesis.
        """
        hypotheses = []
        for seed in seeds:
            hypo = self._generate_hypothesis(seed)
            hypotheses.append(hypo)
        
        self._save_hypotheses(hypotheses)
        return hypotheses

    def _generate_hypothesis(self, seed: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates a deterministic narrative hypothesis from a topic seed.
        """
        seed_id = seed.get("seed_id", "unknown")
        frames = seed.get("structural_frames", [])
        fact_count = len(seed.get("supporting_facts", []))
        
        # Hypothesis text construction: 1-2 sentences, neutral, fact-grounded.
        # "What is structurally changing, and why now?"
        # Using frames and seed summary as context.
        summary = seed.get("seed_summary", "").replace("Clustered facts regarding", "").strip()
        
        # Build text
        if frames:
            frames_text = " and ".join(frames)
            hypothesis_text = f"Recent factual anchors regarding {summary} suggest a transition in {frames_text} logic. This represents a structural shift triggered by the convergence of multiple supporting events."
        else:
            hypothesis_text = f"Multiple facts regarding {summary} indicate a changing structural environment currently under observation."

        # Confidence Level
        conf = "MEDIUM" if fact_count >= 3 else "LOW"

        return {
            "hypothesis_id": f"hypo_{uuid.uuid4().hex[:8]}",
            "seed_id": seed_id,
            "hypothesis_text": hypothesis_text,
            "structural_frames": frames,
            "supporting_fact_count": fact_count,
            "confidence_level": conf,
            "status": "PRE-NARRATIVE"
        }

    def _save_hypotheses(self, hypotheses: List[Dict[str, Any]]):
        self.output_path.write_text(json.dumps(hypotheses, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[HypothesisBuilder] Saved {len(hypotheses)} hypotheses to {self.output_path}")

if __name__ == "__main__":
    # Smoke test
    builder = NarrativeHypothesisBuilder(Path("."))
    mock_seeds = [
        {
            "seed_id": "seed_123",
            "structural_frames": ["TECH_INFLECTION"],
            "supporting_facts": ["f1", "f2"],
            "seed_summary": "AI chip delivery updates",
            "first_seen": "2026-01-26"
        }
    ]
    builder.build_hypotheses(mock_seeds)
