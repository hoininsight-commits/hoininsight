from __future__ import annotations
import argparse
import json
from pathlib import Path
from dataclasses import asdict, is_dataclass

# Adjust imports to absolute
from src.topics.topic_gate import CandidateGenerator, Ranker, Validator, OutputBuilder, HandoffDecider
from src.ops.quote_failsafe import QuoteFailsafe

def load_daily_snapshot(as_of_date: str) -> dict:
    # Use standard path
    p = Path("data") / "reports" / as_of_date.replace("-", "/") / "daily_snapshot.json"
    if not p.exists():
        # Fallback to creating generic snapshot if missing (dev mode)
        return {"datasets": []}
    return json.loads(p.read_text(encoding="utf-8"))

def load_optional_events(as_of_date: str) -> list[dict]:
    p = Path("data") / "events" / as_of_date.replace("-", "/") / "events.json"
    if not p.exists():
        return []
    return json.loads(p.read_text(encoding="utf-8"))

def out_dir(as_of_date: str) -> Path:
    return Path("data") / "topics" / "gate" / as_of_date.replace("-", "/")

def to_plain(obj):
    if is_dataclass(obj):
        return asdict(obj)
    if isinstance(obj, list):
        return [to_plain(x) for x in obj]
    if isinstance(obj, dict):
        return {k: to_plain(v) for k, v in obj.items()}
    return obj

def assert_gate_output_clean(payload: dict):
    """Guardrail enforcement (no mixing with Structural Engine)"""
    import re
    forbidden_terms = [
        "L2", "L3", "L4", "level", "anomaly_level",
        "z_score", "zscore", "sigma", "stddev",
        "leaders", "theme_leaders", "related_stocks",
        "Insight Script"
    ]
    
    # Check all values in the payload recursively
    def check_recursive(data):
        if isinstance(data, str):
            for term in forbidden_terms:
                if re.search(r'\b' + re.escape(term) + r'\b', data, re.IGNORECASE):
                    raise ValueError(f"Guardrail Violation: Forbidden term '{term}' found in Gate output.")
        elif isinstance(data, dict):
            for k, v in data.items():
                for term in forbidden_terms:
                    if term.lower() in k.lower():
                        raise ValueError(f"Guardrail Violation: Forbidden key '{k}' (contains '{term}') found in Gate output.")
                check_recursive(v)
        elif isinstance(data, list):
            for item in data:
                check_recursive(item)

    check_recursive(payload)

from src.events.gate_event_loader import load_gate_events

def main(as_of_date: str):
    snapshot = load_daily_snapshot(as_of_date)
    # Use new robust loader
    events = load_gate_events(Path("."), as_of_date)

    gen = CandidateGenerator()
    ranker = Ranker()
    validator = Validator()
    builder = OutputBuilder()
    handoff = HandoffDecider()

    # 1) Generate candidates (using events)
    candidates = gen.generate(as_of_date=as_of_date, snapshot=snapshot, events=events)
    
    # 2) Attach numbers (using events for evidence)
    numbered_candidates = [validator.attach_numbers(c, snapshot, events) for c in candidates]
    
    # 3) Rank (uses hook_score + number_score + trust_score)
    events_index = {e.event_id: e for e in events}
    ranked = ranker.rank(numbered_candidates, events_index=events_index)
    
    # [IS-31] Quote Proof Layer & Failsafe
    failsafe = QuoteFailsafe(Path("."))
    # Convert dataclasses to dicts for failsafe if necessary, but ranked items are usually dicts at this stage
    # If not, to_plain handles it later. Let's ensure they are dictionaries.
    ranked_dicts = to_plain(ranked)
    processed_ranked = failsafe.process_ranked_topics(ranked_dicts, to_plain(events_index))
    
    top1 = ranker.pick_top1(processed_ranked)

    output = builder.build(as_of_date=as_of_date, top1=top1, ranked=processed_ranked, events=events)
    output = handoff.decide(output, top1=top1, snapshot=snapshot)

    candidates_payload = {
        "schema_version": "topic_gate_candidate_v1",
        "as_of_date": as_of_date,
        "candidates": to_plain(ranked),
    }
    output_payload = {
        "schema_version": "topic_gate_output_v1",
        **to_plain(output),
    }

    # Guardrail enforcement (no mixing)
    assert_gate_output_clean(output_payload)

    d = out_dir(as_of_date)
    d.mkdir(parents=True, exist_ok=True)
    (d / "topic_gate_candidates.json").write_text(json.dumps(candidates_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (d / "topic_gate_output.json").write_text(json.dumps(output_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (d / "topic_gate_output.json").write_text(json.dumps(output_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] Topic Gate saved: {d}")

    # 4) Generate Script (v1.0)
    from src.topics.topic_gate.script_generator import ScriptGenerator
    from src.topics.topic_gate.run_script_quality_gate import run as run_quality_gate

    # Initialize generator with project root
    project_root = Path(__file__).parent.parent.parent
    script_gen = ScriptGenerator(project_root)
    
    # Generate script content
    script_content = script_gen.generate_script(as_of_date)
    
    if script_content:
        # Determine Topic ID (safe fallback for dataclass)
        # GateOutput is a dataclass, use attribute access instead of .get()
        topic_id = getattr(output, 'topic_id', f"gate_{as_of_date.replace('-','')}")
        
        # Save Script File
        script_file = d / f"script_v1_{topic_id}.md"
        script_file.write_text(script_content, encoding="utf-8")
        print(f"[OK] Script generated: {script_file}")
        
        # 5) Run Quality Gate
        q_result = run_quality_gate(script_file, topic_id)
        # q_result is a dict, so .get() is correct here
        print(f"[OK] Quality Gate measured: {q_result.get('quality_status')} ({script_file}.quality.json)")
    else:
        print(f"[WARN] Script generation returned empty for {as_of_date}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--as-of-date", required=True, help="YYYY-MM-DD")
    args = ap.parse_args()
    main(args.as_of_date)
