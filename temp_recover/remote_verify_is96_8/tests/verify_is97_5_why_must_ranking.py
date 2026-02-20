"""
Verify IS-97-5 Why-Must Ranking Layer
"""
import sys
import json
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.topics.mentionables.why_must_ranking import WhyMustRankingLayer

def test_bottleneck_dominance():
    layer = WhyMustRankingLayer()
    mentionables = [
        {"name": "Bank A", "role": "FINANCIAL", "code": "A"},
        {"name": "Grid Co", "role": "GRID_INFRA", "code": "B"}
    ]
    # Default active unit
    units = [{"interpretation_key": "TEST", "hypothesis_jump": {"status": "READY"}}]
    citations = {}
    
    result = layer.rank(mentionables, units, citations)
    top = result["top"]
    
    # Grid (1.0) should outrank Bank (0.4) significantly
    assert top[0]["name"] == "Grid Co"
    assert top[0]["rank_signals"]["bottleneck_score"] == 1.0
    assert top[1]["name"] == "Bank A"

def test_hypothesis_penalty():
    layer = WhyMustRankingLayer()
    mentionables = [{"name": "Test Co", "role": "SEMIS", "code": "T"}]
    
    # Unit on HOLD
    units = [{"interpretation_key": "TEST", "hypothesis_jump": {"status": "HOLD"}}]
    citations = {}
    
    result = layer.rank(mentionables, units, citations)
    item = result["top"][0]
    
    # Timeline score should be penalized (0.2)
    assert item["rank_signals"]["timeline_proximity"] == 0.2

def test_deduplication():
    layer = WhyMustRankingLayer()
    # 3 entities with same role
    mentionables = [
        {"name": "Grid 1", "role": "GRID_INFRA", "code": "G1"},
        {"name": "Grid 2", "role": "GRID_INFRA", "code": "G2"},
        {"name": "Grid 3", "role": "GRID_INFRA", "code": "G3"}
    ]
    units = [{"interpretation_key": "TEST"}]
    
    # Give Grid 1 citations to boost score
    citations = {"G1": ["OFFICIAL_STAT"]}
    
    result = layer.rank(mentionables, units, citations)
    
    # Should only keep 2
    assert len(result["top"]) == 2
    assert len(result["dropped"]) == 1
    assert result["dropped"][0]["reason"] == "Duplicate Role cap exceeded"
    
    # Grid 1 should be top due to citation boost
    assert result["top"][0]["name"] == "Grid 1"

if __name__ == "__main__":
    try:
        test_bottleneck_dominance()
        test_hypothesis_penalty()
        test_deduplication()
        print("IS-97-5 Verification: PASSED")
    except Exception as e:
        print(f"IS-97-5 Verification: FAILED - {e}")
        sys.exit(1)
