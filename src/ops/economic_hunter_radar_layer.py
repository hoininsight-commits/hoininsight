import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class EconomicHunterRadarLayer:
    """
    Step-10: Economic Hunter Radar Layer
    Detects early-stage structural signals that might become future topics.
    """
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.logger = logging.getLogger("EconomicHunterRadarLayer")
        self.ymd = datetime.now().strftime("%Y-%m-%d")
        
    def _load_json(self, path: Path) -> Dict:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except Exception as e:
            self.logger.error(f"Failed to load {path}: {e}")
            return {}

    def _save_json(self, path: Path, data: Any):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')

    def detect_signals(self, topics: List[Dict]) -> List[Dict]:
        candidates = []
        
        # Detection Filters (Keyword based for early stage)
        filters = [
            {
                "theme": "Macro Shock Radar",
                "keywords": ["pce", "cpi", "인플레이션", "금리", "inflation", "fed", "fomc"],
                "early_indicator": "Macro Sentiment Shift"
            },
            {
                "theme": "Policy Radar",
                "keywords": ["정책", "규제", "법안", "policy", "regulation", "bill", "수사", "감사원"],
                "early_indicator": "Regulatory Pressure"
            },
            {
                "theme": "Capital Flow Radar",
                "keywords": ["etf", "수급", "매수", "자금", "inflow", "rotation", "순매수"],
                "early_indicator": "Capital Rotation"
            },
            {
                "theme": "Supply Chain Radar",
                "keywords": ["공급망", "반도체", "에너지", "원자재", "supply", "capacity", "semiconductor"],
                "early_indicator": "Structural Bottleneck"
            }
        ]

        seen_titles = set()

        for topic in topics:
            title = topic.get("title", "").lower()
            if not title or title in seen_titles:
                continue
            
            for f in filters:
                if any(kw in title for kw in f["keywords"]):
                    candidate = {
                        "signal_id": f"RADAR_{datetime.now().strftime('%H%M%S')}_{len(candidates)}",
                        "theme": f["theme"],
                        "signal_strength": "MEDIUM", # Default
                        "early_indicator": f["early_indicator"],
                        "why_now": f"신호 감지: {topic.get('title')[:50]}...",
                        "potential_topic": topic.get("title"),
                        "confidence": "MEDIUM"
                    }
                    
                    # Boost strength if critical keywords present
                    if any(kw in title for kw in ["속보", "쇼크", "급락", "돌파", "폭락"]):
                        candidate["signal_strength"] = "HIGH"
                        candidate["confidence"] = "HIGH"

                    candidates.append(candidate)
                    seen_titles.add(title)
                    break # Matches only one theme

        return candidates

    def run(self):
        self.logger.info(f"Running EconomicHunterRadarLayer for {self.ymd}...")
        
        # 1. Load Inputs
        topic_view_path = self.base_dir / "data/ops/topic_view_today.json"
        topic_data = self._load_json(topic_view_path)
        
        # Primary source: fact_first_shadow
        raw_facts = topic_data.get("sections", {}).get("fact_first_shadow", [])
        
        # 2. Detect Candidates
        candidates = self.detect_signals(raw_facts)
        
        # 3. Filter out existing Top-1 (to avoid redundancy)
        top1_path = self.base_dir / "data/ops/structural_top1_today.json"
        top1_data = self._load_json(top1_path)
        top1_titles = [t.get("title", "").lower() for t in top1_data.get("top1_topics", [])]
        
        final_candidates = [c for c in candidates if c["potential_topic"].lower() not in top1_titles]

        # 4. Save Output (D-4)
        radar_output = {
            "run_date": self.ymd,
            "radar_candidates": final_candidates[:5] # Top 5 for now
        }
        
        # Fallback if no signals found (ensure at least one candidate exists)
        if not final_candidates:
            radar_output["radar_candidates"].append({
                "signal_id": "RADAR_FALLBACK_001",
                "theme": "Macro Shock Radar",
                "signal_strength": "LOW",
                "early_indicator": "Continuous Monitoring",
                "why_now": "시장 매크로 변동성 모니터링 중",
                "potential_topic": "글로벌 금리 방향성 및 인플레이션 추이 관찰",
                "confidence": "LOW"
            })

        self._save_json(self.base_dir / "data/ops/economic_hunter_radar.json", radar_output)
        self.logger.info(f"Detected {len(radar_output['radar_candidates'])} radar candidates.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    EconomicHunterRadarLayer(Path(__file__).resolve().parent.parent.parent).run()
