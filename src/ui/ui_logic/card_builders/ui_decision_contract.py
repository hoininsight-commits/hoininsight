import json
import os
from pathlib import Path

def build_ui_decision_contract(input_dir="data/decision", output_dir="data/ui_decision"):
    """
    Adapts engine outputs (lists) into UI-friendly dict contracts.
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    def load_json(name):
        f = input_path / name
        if f.exists():
            try:
                with open(f, 'r', encoding='utf-8') as j:
                    return json.load(j)
            except Exception as e:
                print(f"[UI-CONTRACT] Error loading {name}: {e}")
        return None

    def save_json(name, data):
        with open(output_path / name, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # A. interpretation_units.json (List -> Dict by interpretation_id)
    units = load_json('interpretation_units.json')
    units_dict = {}
    if isinstance(units, list):
        for u in units:
            if 'interpretation_id' in u:
                units_dict[u['interpretation_id']] = u
    elif isinstance(units, dict):
        units_dict = units
    save_json('interpretation_units.json', units_dict)

    # B. mentionables.json (List -> Dict by interpretation_id or topic_id)
    mentions = load_json('mentionables.json')
    mentions_dict = {}
    if isinstance(mentions, list):
        for m in mentions:
            key = m.get('interpretation_id') or m.get('topic_id')
            if key:
                mentions_dict[key] = m
    elif isinstance(mentions, dict):
        mentions_dict = mentions
    save_json('mentionables.json', mentions_dict)

    # C. content_pack.json (List -> Dict by topic_id)
    packs = load_json('content_pack.json')
    packs_dict = {}
    if isinstance(packs, list):
        for p in packs:
            if 'topic_id' in p:
                packs_dict[p['topic_id']] = p
    elif isinstance(packs, dict):
        # The UI expects a dict with a 'packs' key if it follows the old logic, 
        # or we normalize to keyed dict.
        # Let's check docs/ui/render.js: if (packs && packs.packs) -> it expects { "packs": [...] }
        # Let's normalize it to { "packs": list } for now if it's already a list, 
        # or if it's a dict, keep as is.
        packs_dict = packs
    save_json('content_pack.json', packs_dict)

    # D. evidence_citations.json (List -> Dict by topic_id)
    evidence = load_json('evidence_citations.json')
    evidence_dict = {}
    if isinstance(evidence, list):
        for e in evidence:
            if 'topic_id' in e:
                evidence_dict[e['topic_id']] = e
    elif isinstance(evidence, dict):
        evidence_dict = evidence
    save_json('evidence_citations.json', evidence_dict)

    # E. narrative_skeleton.json (Keep as-is dict)
    skeleton = load_json('narrative_skeleton.json') or {}
    save_json('narrative_skeleton.json', skeleton)

    # F. speakability_decision.json (Keep as-is dict)
    decision = load_json('speakability_decision.json') or {}
    save_json('speakability_decision.json', decision)

    print(f"[UI-CONTRACT] Successfully built UI contract assets in {output_dir}")

if __name__ == "__main__":
    build_ui_decision_contract()
