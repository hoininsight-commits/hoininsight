#!/usr/bin/env python3
import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any
from src.ops.stock_exposure_map import AXIS_EXPOSURE_MAP, DEFAULT_EXPOSURE

class StructuralStockLinkageLayer:
    """
    Phase 22B: Structural Stock Linkage Layer
    Links video candidates to industries and stocks based on Axis.
    No-Behavior-Change: No scoring, just mapping.
    """

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.logger = logging.getLogger("StockLinkage")
        self.ymd_dash = datetime.now().strftime("%Y-%m-%d")

    def _load_json(self, path: Path) -> Any:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except Exception as e:
            self.logger.error(f"Failed to load {path}: {e}")
            return {}

    def _get_axes_from_narrative(self, ds_id: str, narrative_topics: List[Dict]) -> List[str]:
        # Try to find axis from narrative intelligence
        topic = next((t for t in narrative_topics if t.get("dataset_id") == ds_id), {})
        return topic.get("axis", [])

    def _map_stocks(self, ds_id: str, axes: List[str]) -> Dict:
        industries = []
        stocks = []
        
        # 1. Map based on explicit axis
        for axis in axes:
            if axis in AXIS_EXPOSURE_MAP:
                mapping = AXIS_EXPOSURE_MAP[axis]
                industries.append({"industry": mapping["industry"], "logic": mapping["logic"]})
                stocks.extend(mapping["stocks"])
        
        # 2. Fallback based on ds_id keywords
        if not stocks:
            ds_id_lower = ds_id.lower()
            if "inflation" in ds_id_lower or "rates" in ds_id_lower:
                mapping = AXIS_EXPOSURE_MAP.get("Policy:RATE")
            elif "semicon" in ds_id_lower or "nvidia" in ds_id_lower or "hbm" in ds_id_lower:
                mapping = AXIS_EXPOSURE_MAP.get("Liquidity:LIQUIDITY")
            else:
                mapping = DEFAULT_EXPOSURE
            
            if mapping:
                if "industry" in mapping: # Single mapping
                    industries.append({"industry": mapping["industry"], "logic": mapping.get("logic", "")})
                    stocks.extend(mapping.get("stocks", []))
                else: # Already a list?
                    pass

        # De-duplicate
        seen_stocks = set()
        unique_stocks = []
        for s in stocks:
            if s["ticker"] not in seen_stocks:
                unique_stocks.append(s)
                seen_stocks.add(s["ticker"])
        
        return {
            "axis": axes,
            "industry_exposure": industries if industries else [{"industry": "N/A", "logic": "No direct axis mapping"}],
            "stocks": unique_stocks
        }

    def run(self):
        self.logger.info(f"Running Structural Stock Linkage for {self.ymd_dash}...")
        
        # 1. Load Inputs
        pool_path = self.base_dir / "data/ops/video_candidate_pool.json"
        if not pool_path.exists():
            pool_path = self.base_dir / "data_outputs/ops/video_candidate_pool.json"
        pool_data = self._load_json(pool_path)
        candidates = pool_data.get("top_candidates", [])

        narrative_path = self.base_dir / "data/ops/narrative_intelligence_v2.json"
        narrative_data = self._load_json(narrative_path)
        narrative_topics = narrative_data.get("topics", [])

        # 2. Process Topics
        linked_topics = []
        for cand in candidates:
            ds_id = cand.get("dataset_id")
            axes = self._get_axes_from_narrative(ds_id, narrative_topics)
            linkage = self._map_stocks(ds_id, axes)
            
            linked_topics.append({
                "dataset_id": ds_id,
                "title": cand.get("title"),
                "axis": linkage["axis"],
                "industry_exposure": linkage["industry_exposure"],
                "stocks": linkage["stocks"]
            })

        # 3. Output Pack
        pack = {
            "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "date_kst": self.ymd_dash,
            "topics": linked_topics
        }

        out_path = self.base_dir / "data/ops/stock_linkage_pack.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(pack, indent=2, ensure_ascii=False), encoding='utf-8')
        
        self.logger.info(f"Successfully generated stock linkage pack with {len(linked_topics)} topics.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    StructuralStockLinkageLayer(Path(".")).run()
