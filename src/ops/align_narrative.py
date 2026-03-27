import json
from pathlib import Path

def align_narrative(project_root, core_theme, narrative_data):
    """
    Ensures the narrative matches the core theme.
    If no match, it 'regenerates' by providing a skeleton based on the core theme.
    """
    if narrative_data.get("theme") == core_theme:
        print(f"[Aligner] Narrative already aligned with {core_theme}")
        return narrative_data
    
    print(f"[Aligner] ⚠️ Narrative mismatch ({narrative_data.get('theme')} vs {core_theme}). Regenerating...")
    
    # Simple 'regeneration' logic: create a basic skeleton for the new core theme
    # In a real system, this would call an LLM or a specialized narrative engine.
    regenerated = {
        "theme": core_theme,
        "explanation": f"{core_theme}에 대한 새로운 구조적 분석이 필요합니다.",
        "situation": "현재 시장은 해당 테마의 초기 신호를 처리 중입니다.",
        "contradiction": "기존 추세와 새로운 동력 사이의 불균형 감지.",
        "sector_impact": ["TBD"],
        "why_it_matters": "SSOT 정렬을 위해 생성된 기본 내러티브입니다."
    }
    return regenerated

if __name__ == "__main__":
    # Test
    sample = {"theme": "Wrong Theme", "explanation": "..."}
    print(json.dumps(align_narrative(".", "AI Power Constraint", sample), indent=2, ensure_ascii=False))
