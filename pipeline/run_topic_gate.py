from __future__ import annotations
import argparse
import json
from pathlib import Path
from dataclasses import asdict, is_dataclass

# Adjust imports to absolute
from src.topics.topic_gate import CandidateGenerator, Ranker, Validator, OutputBuilder, HandoffDecider

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

def gate_output_dir(as_of_date: str) -> Path:
    return Path("data") / "topics" / "gate" / as_of_date.replace("-", "/")

def to_plain(obj):
    if is_dataclass(obj):
        return asdict(obj)
    if isinstance(obj, list):
        return [to_plain(x) for x in obj]
    if isinstance(obj, dict):
        return {k: to_plain(v) for k, v in obj.items()}
    return obj

def main(as_of_date: str):
    snapshot = load_daily_snapshot(as_of_date)
    events = load_optional_events(as_of_date)

    gen = CandidateGenerator()
    ranker = Ranker()
    validator = Validator()
    builder = OutputBuilder()
    handoff = HandoffDecider()

    candidates = gen.generate(as_of_date=as_of_date, snapshot=snapshot, events=events)
    ranked = ranker.rank(candidates)
    top1 = ranker.pick_top1(ranked)

    top1 = validator.attach_numbers(top1, snapshot)

    output = builder.build(as_of_date=as_of_date, top1=top1, ranked=ranked)
    output = handoff.decide(output, top1=top1, snapshot=snapshot)

    out_dir = gate_output_dir(as_of_date)
    out_dir.mkdir(parents=True, exist_ok=True)

    candidates_payload = {
        "schema_version": "topic_gate_candidate_v1",
        "as_of_date": as_of_date,
        "candidates": to_plain(ranked),
    }
    output_payload = {
        "schema_version": "topic_gate_output_v1",
        **to_plain(output),
    }

    (out_dir / "topic_gate_candidates.json").write_text(json.dumps(candidates_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "topic_gate_output.json").write_text(json.dumps(output_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[OK] Topic Gate saved: {out_dir}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--as-of-date", required=True, help="YYYY-MM-DD")
    args = ap.parse_args()
    main(args.as_of_date)
