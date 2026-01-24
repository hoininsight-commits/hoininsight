import pandas as pd
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

from .definitions import BASELINE_SIGNALS, ANOMALY_LOGIC_MAP, WHY_NOW_TYPES

@dataclass
class AnchorResult:
    data_axis: List[str]
    baseline_match: List[str]
    anomaly_logic: str # Key from ANOMALY_LOGIC_MAP
    why_now_type: str
    level: str # L2, L3, L4
    level_proof: str
    gap_detection: str
    missing_data_request: List[str] = field(default_factory=list)
    
    def to_markdown(self) -> str:
        return f"""
### 1. DATA AXIS
- {', '.join(self.data_axis)}

### 2. BASELINE MATCH
- {', '.join(self.baseline_match)}

### 3. ANOMALY LOGIC
- {self.anomaly_logic}

### 4. WHY_NOW_TRIGGER_TYPE
- **{self.why_now_type}**

### 5. LEVEL JUDGMENT
- **{self.level}**
- Proof: {self.level_proof}

### 6. GAP DETECTION
- Status: **{self.gap_detection}**
- Request: {', '.join(self.missing_data_request) if self.missing_data_request else 'None'}
"""

class AnchorEngine:
    def __init__(self, base_dir):
        self.base_dir = base_dir

    def run_analysis(self, snapshot_data: List[Dict[str, Any]]) -> List[AnchorResult]:
        results = []
        
        # Group by potential clusters (simplified for now: check each item against others)
        # In a real engine, we'd form clusters. Here we iterate items and look for combinatorics.
        
        # For demonstration of the 6-step Logic, we process the 'primary' candidate found by heuristics first,
        # then apply the rigor.
        
        # Actually, Step 1 says "Identify combination". Single axis is ignored.
        # So we need to find pairs/groups.
        
        # 1. Naive Clustering (e.g. Rate + Equity, or Same Sector)
        clusters = self._form_clusters(snapshot_data)
        
        for cluster in clusters:
            res = self._execute_6_steps(cluster)
            if res:
                results.append(res)
                
        return results

    def _get_z(self, item: Dict[str, Any]) -> float:
        z = item.get("z_score")
        if z is None and "evidence" in item:
            z = item["evidence"].get("z_score")
        return float(z) if z is not None else 0.0

    def _form_clusters(self, data: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        # Simple Clustering: All High Z-Score items together?
        # Or conceptually linked items. 
        # Let's take items with Z > 2.0 (Strict Anchor Rule)
        high_z = [d for d in data if abs(self._get_z(d)) > 2.0]
        
        clusters = []
        if len(high_z) >= 2:
            clusters.append(high_z) # All high Z items as one cluster for "Systemic" check
            
            # Also pairs
            for i in range(len(high_z)):
                for j in range(i+1, len(high_z)):
                    clusters.append([high_z[i], high_z[j]])
        
        return clusters

    def _execute_6_steps(self, cluster: List[Dict[str, Any]]) -> Optional[AnchorResult]:
        # STEP 1: DATA AXIS IDENTIFICATION
        axes = [d.get("dataset_id", "unknown") for d in cluster]
        if len(axes) < 2:
            return None # "단일 축이면 이상징후 아님" (Anchor Step 1)
            
        # STEP 2: BASELINE SIGNAL MATCHING
        matches = []
        for item in cluster:
            z = abs(self._get_z(item))
            if z > BASELINE_SIGNALS["volatility_surge"]["threshold_z"]:
                matches.append(f"{item.get('dataset_id')}: Volatility Surge (Z={z:.2f})")
        
        if not matches:
            return None # No baseline violation
            
        # STEP 3: ANOMALY LOGIC TRIGGER
        # Heuristic matching against ANOMALY_LOGIC_MAP definitions
        logic_found = "Unknown"
        
        # Creating a mini-context for logic check
        context = {d.get("dataset_id"): d for d in cluster}
        ids = list(context.keys())
        
        # Example Logic Check (simplified)
        has_rate = any("rates" in x for x in ids)
        has_equity = any("index" in x or "equity" in x for x in ids)
        has_vix = any("vix" in x for x in ids)
        
        if has_rate and (has_equity or has_vix):
            logic_found = "Monetary Tightening"
        elif any("gold" in x for x in ids) and has_equity:
            logic_found = "Risk Off"
        # ... more rules
        
        # STEP 4: WHY_NOW_TRIGGER_TYPE
        # Deduce from logic
        trigger_type = "Hybrid-driven" # Default fallback
        if logic_found == "Monetary Tightening":
            trigger_type = "Capital-driven"
        elif logic_found == "Risk Off":
            trigger_type = "Structural-driven" # Sentiment/Structure
            
        # STEP 5: LEVEL JUDGMENT
        # L2: Data only. L3: News/Event match. L4: Captial Fixation (Volume).
        level = "L2"
        proof = "Statistical Deviation > 2.0 Sigma"
        
        # Check for Volume data to upgrade to L4
        has_volume = any("volume" in d or "amount" in d for d in cluster)
        if has_volume:
            level = "L4"
            proof += " + Capital Fixation Verified (Volume)"
            
        # STEP 6: GAP DETECTION
        gap_status = "Insufficient"
        request = []
        
        if level == "L2":
            gap_status = "Insufficient Evidence for L4"
            request.append("Need Volume/Flow Data to verify Capital Fixation")
        else:
            gap_status = "Sufficient"
            
        return AnchorResult(
            data_axis=axes,
            baseline_match=matches,
            anomaly_logic=logic_found,
            why_now_type=trigger_type,
            level=level,
            level_proof=proof,
            gap_detection=gap_status,
            missing_data_request=request
        )
