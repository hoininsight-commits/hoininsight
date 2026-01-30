from __future__ import annotations
import argparse
import json
from pathlib import Path
from dataclasses import asdict, is_dataclass

# Adjust imports to absolute
from src.topics.topic_gate import CandidateGenerator, Ranker, Validator, OutputBuilder, HandoffDecider
from src.ops.quote_failsafe import QuoteFailsafe
from src.ops.source_diversity_auditor import SourceDiversityAuditor
from src.issuesignal.time_decay import TriggerTimeDecayEngine
from src.issuesignal.urgency_engine import UrgencyEngine
from src.issuesignal.output_decider import OutputDecider
from src.issuesignal.content_composer import ContentPackageComposer
from src.issuesignal.audience_gate import AudienceGateEngine
from src.issuesignal.followup_engine import FollowUpEngine
from src.issuesignal.membership_queue import MembershipQueueEngine
from src.issuesignal.voice_lock import VoiceLockEngine

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
    
    # [IS-32] Source Diversity Audit & Enforce
    auditor = SourceDiversityAuditor(Path("."))
    processed_ranked = auditor.audit_topics(processed_ranked, to_plain(events_index))
    
    # [IS-33] Trigger Confidence Decay
    decay_engine = TriggerTimeDecayEngine()
    for t in processed_ranked:
        decay_engine.process_trigger(t)
        # Apply re-arm if topic has diverse sources (example condition)
        if t.get("diversity_verdict") == "PASS":
             # We gather enriched sources if available
             decay_engine.re_arm(t, t.get("enriched_sources", []))

    # [IS-34] Urgency & Output Decision
    urgency_eng = UrgencyEngine()
    output_dec = OutputDecider()
    for t in processed_ranked:
        # 1. Calc Urgency
        u_score = urgency_eng.calculate_urgency(t)
        # 2. Check Too-Late Override
        too_late_reason = urgency_eng.check_too_late(t)
        # 3. Decide Format & Reason
        fmt_ko, reason_ko = output_dec.decide(u_score, too_late_reason)
        
        t["urgency_score"] = u_score
        t["output_format_ko"] = fmt_ko
        t["editorial_reason_ko"] = reason_ko
        
        # 4. If SILENT and was READY, demote or flag
        if "침묵" in fmt_ko and t.get("status") == "READY":
             t["status"] = "SILENT"
             t["demotion_reason"] = reason_ko

    # [IS-35] Content Package Composition
    composer = ContentPackageComposer()
    for t in processed_ranked:
        content_pkg = composer.compose(t)
        if content_pkg:
            t["content_package"] = content_pkg

    # [IS-36] Audience Gate & Distribution Control
    gate = AudienceGateEngine()
    for t in processed_ranked:
        aud_ko, reason_ko = gate.classify(t)
        t["audience_ko"] = aud_ko
        t["distribution_reason_ko"] = reason_ko

    # [IS-37] Narrative Continuity & Follow-up
    followup_eng = FollowUpEngine()
    for t in processed_ranked:
        t["follow_up_plans"] = followup_eng.plan_follow_ups(t)

    # [IS-38] Membership-Only Topic Queue
    mem_queue_eng = MembershipQueueEngine()
    membership_queue = mem_queue_eng.generate_queue(processed_ranked)

    # [IS-39] Human Voice Lock
    voice_eng = VoiceLockEngine()
    for t in processed_ranked:
        pkg = t.get("content_package")
        if pkg:
            # We lock long form content as lead
            if "content" in pkg and isinstance(pkg["content"], str):
                res = voice_eng.apply_lock(pkg["content"])
                pkg["content"] = res["locked_content"]
                t["voice_consistent"] = res["voice_consistent"]
            elif "content" in pkg and isinstance(pkg["content"], dict):
                # Lock short variants
                is_consist = True
                for k, v in pkg["content"].items():
                    res = voice_eng.apply_lock(v)
                    pkg["content"][k] = res["locked_content"]
                    if not res["voice_consistent"]: is_consist = False
                t["voice_consistent"] = is_consist

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
        "membership_only_queue": membership_queue,
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
