import json
import sys
from pathlib import Path

def verify():
    base_dir = Path(__file__).resolve().parent.parent
    output_path = base_dir / "data/ops/narrative_intelligence_v2.json"
    
    print(f"Checking for Narrative Intelligence v2.0 output at: {output_path}")
    
    if not output_path.exists():
        print("❌ Error: narrative_intelligence_v2.json not found.")
        sys.exit(1)
        
    try:
        data = json.loads(output_path.read_text(encoding='utf-8'))
        topics = data.get("topics", [])
        
        if not topics:
            print("⚠️ Warning: No topics found in the output. This might be normal if today's data is sparse.")
            # We don't fail yet, but check if any topic exists
        
        for i, topic in enumerate(topics):
            print(f"Checking topic {i+1}: {topic.get('title')}")
            
            # v3.0 Fields check
            required_v3 = [
                "narrative_score", "final_narrative_score", "video_ready", 
                "causal_chain", "schema_version", "actor_tier_score", 
                "cross_axis_count", "cross_axis_multiplier", "escalation_flag",
                "conflict_flag", "expectation_gap_score", "expectation_gap_level",
                "tension_multiplier_applied"
            ]
            missing = [f for f in required_v3 if f not in topic]
            
            if missing:
                print(f"❌ Error: Topic {i+1} missing v3.0 fields: {missing}")
                sys.exit(1)
                
            # Type checks
            if not isinstance(topic["final_narrative_score"], (int, float)):
                 print(f"❌ Error: final_narrative_score should be a number (got {type(topic['final_narrative_score'])})")
                 sys.exit(1)
                 
            if not isinstance(topic["conflict_flag"], bool):
                 print(f"❌ Error: conflict_flag should be boolean (got {type(topic['conflict_flag'])})")
                 sys.exit(1)

            if not isinstance(topic["expectation_gap_score"], int):
                 print(f"❌ Error: expectation_gap_score should be an int (got {type(topic['expectation_gap_score'])})")
                 sys.exit(1)

            if topic["expectation_gap_level"] not in ["none", "moderate", "strong"]:
                 print(f"❌ Error: invalid expectation_gap_level: {topic['expectation_gap_level']}")
                 sys.exit(1)
                 
            if not isinstance(topic["causal_chain"], dict):
                 print(f"❌ Error: causal_chain should be a dict (got {type(topic['causal_chain'])})")
                 sys.exit(1)
            
            # Causal chain fields
            required_causal = ["cause", "structural_shift", "market_consequence", "affected_sector", "time_pressure"]
            missing_causal = [f for f in required_causal if f not in topic["causal_chain"]]
            if missing_causal:
                print(f"❌ Error: Topic {i+1} causal_chain missing fields: {missing_causal}")
                sys.exit(1)

        print(f"✅ Narrative Intelligence Verification PASSED! (Checked {len(topics)} topics)")
        sys.exit(0)
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify()
