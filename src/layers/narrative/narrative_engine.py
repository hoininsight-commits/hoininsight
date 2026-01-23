
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from src.layers.narrative.narrative_schema import NarrativeTopic, ConfidenceLevel

class NarrativeEngine:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.output_dir = base_dir / "data" / "topics" / "narrative" / datetime.now().strftime("%Y/%m/%d")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run(self, anomaly_snapshots: List[Dict[str, Any]]) -> List[NarrativeTopic]:
        """
        Ingests strict anomalies (Signals) and produces Narrative Topics.
        """
        print(f"[NarrativeEngine] Analyzing {len(anomaly_snapshots)} signals...")
        
        narrative_topics = []

        # Logic to group signals and identify drivers.
        # This is where the 'Economic Hunter' logic lives.
        
        # 1. Group by Sector/Theme
        grouped_signals = self._group_signals(anomaly_snapshots)
        
        for group_key, group_items in grouped_signals.items():
            # Criteria: Minimum 2 confirming signals or 1 High-Impulse signal with News
            if self._is_candidate(group_items):
                topic = self._generate_topic(group_key, group_items)
                if topic:
                    narrative_topics.append(topic)

        # Save results
        self._save_results(narrative_topics)
        return narrative_topics

    def _group_signals(self, anomalies):
        # Placeholder for grouping logic
        # Ideally maps specific assets to broader themes (Bio, AI, Energy)
        groups = {}
        for anomaly in anomalies:
            # Simple fallback: Group by 'entity' or 'dataset_id' type
            # Real implementation would need a Mapping Table (Asset -> Sector)
            key = anomaly.get('entity', 'UNKNOWN')
            if key not in groups:
                groups[key] = []
            groups[key].append(anomaly)
        return groups

    def _is_candidate(self, items):
        # Placeholder rule: If anything is flagged as an anomaly, it's a candidate for now.
        return len(items) > 0

    def _generate_topic(self, key, items) -> NarrativeTopic:
        # construct a NarrativeTopic object
        # In a real scenario, this would call an LLM with the context of 'items'
        
        # Mocking logic for "Bio Check" mentioned in spec
        if "BIO" in key.upper() or "HEALTH" in key.upper(): 
             return NarrativeTopic(
                topic_anchor=f"{key} Sector Rotation",
                narrative_driver="Evaluation Criteria Shift (Growth -> Defensive)",
                trigger_event="Recent sustained outflow from Tech -> Inflow to Bio",
                core_narrative="Market is seeking safety with yield, pricing in post-rate-cut environment.",
                intent_signals=["High Volume on ETFs", "Institutional block deals"],
                structural_hint="Still early, no earnings confirmation yet.",
                era_fit="Late Cycle Defense",
                confidence_level=ConfidenceLevel.MEDIUM,
                risk_note="Volatility is high; dependent on single drug approval news."
            )
        
        # Generic fallback
        top_item = items[0]
        return NarrativeTopic(
            topic_anchor=f"{key} Movement",
            narrative_driver="Volatility Spike",
            trigger_event=f"Anomaly detected in {top_item.get('dataset_id')}",
            core_narrative="Sharp short-term deviation observed.",
            intent_signals=[f"Z-Score: {top_item.get('z_score', 'N/A')}"],
            structural_hint="Requires further monitoring.",
            era_fit="Idiosyncratic",
            confidence_level=ConfidenceLevel.LOW,
            risk_note="May be noise."
        )

    def _save_results(self, topics: List[NarrativeTopic]):
        out_file = self.output_dir / "narrative_topics.json"
        data = {"topics": [t.to_dict() for t in topics]}
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"[NarrativeEngine] Saved {len(topics)} topics to {out_file}")

def main():
    # Simple test runner
    base_dir = Path(".")
    engine = NarrativeEngine(base_dir)
    # Mock input
    engine.run([{"entity": "TEST_ASSET", "z_score": 3.5, "dataset_id": "test_ds"}])

if __name__ == "__main__":
    main()
