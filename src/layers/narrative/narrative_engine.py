
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
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

    
    def _group_signals(self, anomalies: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Groups anomalies by their mapped Sector or Theme.
        """
        from src.layers.narrative.sector_map import SectorMap

        groups = {}
        for anomaly in anomalies:
            # normalize keys
            raw_id = anomaly.get('entity') or anomaly.get('dataset_id') or 'unknown'
            
            # Get Context from Map
            info = SectorMap.get_info(raw_id)
            sector = info['sector']
            theme = info['theme']

            # Primary Key: Sector (e.g. "Equity", "Commodity")
            # We could also group by Theme if we want more granularity
            # For now, let's try a composite key if Sector is generic, or just Sector.
            # Let's group by THEME if possible, as it's more narrative-driven (e.g. "Tech" vs "Broad Market")
            key = f"{sector} - {theme}"
            
            if key not in groups:
                groups[key] = []
            
            # Enrich anomaly with metadata for later use
            anomaly['_narrative_meta'] = info
            groups[key].append(anomaly)
            
        return groups

    def _is_candidate(self, items: List[Dict[str, Any]]) -> bool:
        # A group is a candidate if it has at least one valid anomaly.
        # Future: require >1 items or specific severity threshold.
        return len(items) > 0

    def _generate_topic(self, key: str, items: List[Dict[str, Any]]) -> Optional[NarrativeTopic]:
        """
        Generates a NarrativeTopic from a group of anomalies.
        """
        if not items:
            return None

        # 1. Identify "Driver" based on signal composition
        # E.g. if Price and Volume both spiked -> "High Conviction Move"
        # If correlation broke -> "Decoupling"
        
        # Check for specific "Mock" scenarios first (Logic Injection)
        if "Biotech" in key:
            return self._generate_bio_mock(key, items)

        # 2. Generic Construction
        primary_item = items[0]
        meta = primary_item.get('_narrative_meta', {})
        sector = meta.get('sector', 'Unknown')
        
        # Determine "Driver" string
        driver = "Structural Volatility"
        if sector == "Rates":
            driver = "Monetary Policy Repricing"
        elif sector == "Commodity":
            driver = "Supply/Demand Shock"
        elif sector == "Equity":
            driver = "Risk Sentiment Shift"
            
        # Determine "Core Narrative"
        # Just listing the anomalies in a readable way
        entities = set(item.get('entity', 'Unknown') for item in items)
        joined_entities = ", ".join(entities)
        core_narrative = f"Anomalous activity detected in {joined_entities}. Markets are repricing {sector} expectations."

        return NarrativeTopic(
            topic_anchor=f"{key} Activity",
            narrative_driver=driver,
            trigger_event=f"Signal Cluster in {joined_entities}",
            core_narrative=core_narrative,
            intent_signals=[f"{item.get('dataset_id')}: z={item.get('z_score', 0):.1f}" for item in items[:3]],
            structural_hint="Watch for flow-through impacts.",
            era_fit="Regime Uncertainty",
            confidence_level=ConfidenceLevel.LOW,
            risk_note="Correlation does not imply causation; monitor for persistence."
        )

    def _generate_bio_mock(self, key: str, items: List[Dict[str, Any]]) -> NarrativeTopic:
        # Mock logic as requested in spec
        return NarrativeTopic(
            topic_anchor=f"{key} Rotation",
            narrative_driver="Evaluation Criteria Shift (Growth -> Defensive)",
            trigger_event="Recent sustained outflow from Tech -> Inflow to Bio",
            core_narrative="Market is seeking safety with yield, pricing in post-rate-cut environment. Biotech showing relative strength.",
            intent_signals=["High Volume on ETFs", "Institutional block deals", "Divergence from SPX"],
            structural_hint="Still early, no earnings confirmation yet.",
            era_fit="Late Cycle Defense",
            confidence_level=ConfidenceLevel.MEDIUM,
            risk_note="Volatility is high; dependent on drug data."
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
    
    # Mock input checking mapping logic
    test_anomalies = [
        {"entity": "sp500", "z_score": 2.5, "dataset_id": "market_sp500_fred"},
        {"entity": "xbi", "z_score": 3.0, "dataset_id": "etf_xbi"}, # Should trigger Bio logic
        {"entity": "us_10y", "z_score": -2.0, "dataset_id": "us_10y_yield"}
    ]
    
    topics = engine.run(test_anomalies)
    for t in topics:
        print(f"Generated: {t.topic_anchor} (Driver: {t.narrative_driver})")

if __name__ == "__main__":
    main()
