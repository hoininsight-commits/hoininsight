"""
Verify IS-97-4 Labor Shift Mentionables
"""
import sys
import yaml
from pathlib import Path

def test_mentionables_registry():
    path = Path(__file__).parent.parent / "registry" / "mappings" / "mentionables_map_v1.yml"
    assert path.exists()
    
    with open(path) as f:
        data = yaml.safe_load(f)
        
    groups = data.get('groups', [])
    target_group = next((g for g in groups if g['group_id'] == 'LABOR_SHIFT_PHYSICAL_AI'), None)
    
    assert target_group is not None, "LABOR_SHIFT_PHYSICAL_AI group not found"
    assert len(target_group['candidates']) >= 3
    
    # Check why_must
    for cand in target_group['candidates']:
        assert 'why_must' in cand
        assert cand['why_must']

if __name__ == "__main__":
    try:
        test_mentionables_registry()
        print("IS-97-4 Mentionables Verification: PASSED")
    except Exception as e:
        print(f"IS-97-4 Mentionables Verification: FAILED - {e}")
        sys.exit(1)
