"""
IS-97-6 Narrative Priority Lock Layer
Deterministically selects ONE "Hero Topic" from synthesized candidates.
"""
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

class NarrativePriorityLock:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent.parent
        self.decision_dir = self.base_dir / "data" / "decision"
        self.export_dir = self.base_dir / "exports"
        self.export_dir.mkdir(exist_ok=True)

    def load_data(self):
        candidates = []
        mentionables = []
        speakability = {}
        
        try:
            candidates = json.loads((self.decision_dir / "synthesized_topics.json").read_text())
        except: pass
        try:
            data = json.loads((self.decision_dir / "mentionables_ranked.json").read_text())
            mentionables = data.get("top", [])
        except: pass
        try:
            # Mock speakability for now if not exists or assume generic ready
            # In prod, load actual file
            # speakability = json.loads((self.decision_dir / "speakability_decision.json").read_text())
            pass
        except: pass
        
        return candidates, mentionables, speakability

    def calculate_priority(self, topic: Dict, mentionables: List) -> Dict:
        """Calculates 5-factor priority score."""
        
        # 1. Structural Weight (35%)
        t_type = topic.get("topic_type", "UNKNOWN")
        s_weight = 0.0
        if t_type == "STRUCTURAL_SHIFT": s_weight = 1.0
        elif t_type == "REGIME_ACCELERATION": s_weight = 0.8
        elif t_type == "CAPITAL_REPRICING": s_weight = 0.6
        elif t_type == "BOTTLENECK_REVEAL": s_weight = 0.5
        
        # 2. Bottleneck Weight (20%)
        # Check if topic dominant eye maps to a high-value bottleneck role
        # Simplification: Assume sector maps to role
        # In full version, cross-ref mentionables linked to this sector
        b_weight = 0.5 # Default
        if "SEMICONDUCTORS" in topic["sector"]: b_weight = 0.8
        elif "POWER" in topic["sector"] or "GRID" in topic["sector"]: b_weight = 1.0
        
        # 3. Evidence Weight (15%)
        # Based on eye count (already >= 3) and confidence
        e_weight = topic.get("confidence_score", 0.7)
        
        # 4. Timing (15%)
        # Boost if SCHEDULE or EVENT eye is present
        eyes = topic.get("eyes_used", [])
        tm_weight = 0.5
        if "SCHEDULE" in eyes or "EVENT" in eyes: tm_weight = 1.0
        
        # 5. Cross Theme (10%) - Stub
        c_weight = 0.5
        
        score = (0.35 * s_weight) + (0.20 * b_weight) + (0.15 * e_weight) + (0.15 * tm_weight) + (0.10 * c_weight)
        
        return {
            "total": round(score, 3),
            "breakdown": {
                "structural": s_weight,
                "bottleneck": b_weight,
                "evidence": e_weight,
                "timing": tm_weight
            }
        }

    def process(self):
        candidates, mentionables, speakability = self.load_data()
        
        scored_candidates = []
        
        for cand in candidates:
            # Gating: Check Speakability (Mock Ready for simplified logic if file missing)
            # In real logic: if speakability.get(cand["topic_id"]) != "READY": continue
            
            p_score = self.calculate_priority(cand, mentionables)
            cand["priority_score"] = p_score
            scored_candidates.append(cand)
            
        # Sort Logic: Score Desc -> Structural Desc -> ID
        # Python sort is stable. Do reverse sorts for primary keys last.
        scored_candidates.sort(key=lambda x: x["topic_id"]) # Tie breaker 3
        # Tie breaker 2 (handled by primary score weight implicitly, but explicit sort ok)
        scored_candidates.sort(key=lambda x: x["priority_score"]["total"], reverse=True)
        
        # Select Hero
        hero = None
        hold_queue = []
        
        if scored_candidates:
            hero = scored_candidates[0]
            hold_queue = scored_candidates[1:6] # Top 5 holds
            
            # Save Hero Lock
            hero_out = {
                "status": "LOCKED",
                "lock_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "hero_topic": hero,
                "lock_reason": f"Highest Priority Score ({hero['priority_score']['total']})"
            }
        else:
            hero_out = {"status": "NO_HERO_TODAY", "reason": "No eligible topics"}
            
        # Save JSONs
        with open(self.decision_dir / "hero_topic_lock.json", "w") as f:
            json.dump(hero_out, f, indent=2, ensure_ascii=False)
            
        with open(self.decision_dir / "hold_queue.json", "w") as f:
            json.dump(hold_queue, f, indent=2, ensure_ascii=False)
            
        # Generate Markdown Pack
        if hero:
            self.generate_pack(hero)
            
        print(f"[LOCK] Hero Selected: {hero['sector'] if hero else 'NONE'}")

    def generate_pack(self, hero):
        md = f"""# HOIN INSIGHT HERO TOPIC PACK
**Date**: {datetime.now().strftime('%Y-%m-%d')}
**Sector**: {hero['sector']}
**Type**: {hero['topic_type']}

## 1. Headline
(Generated from Narrative Skeleton)

## 2. Why Now (The 3 Eyes)
- **1. {hero['dominant_eye']}**: {hero['why_now_bundle']['why_now_1']}
- **2. Policy/Other**: {hero['why_now_bundle']['why_now_2']}
- **3. Structure**: {hero['why_now_bundle']['why_now_3']}

## 3. Top Picks (Why-Must)
(Placeholder for mapped mentionables)

## 4. Priority Score
Total: {hero['priority_score']['total']}
(Structure: {hero['priority_score']['breakdown']['structural']}, Timing: {hero['priority_score']['breakdown']['timing']})
"""
        with open(self.export_dir / "hero_upload_pack.md", "w") as f:
            f.write(md)

if __name__ == "__main__":
    lock = NarrativePriorityLock()
    lock.process()
