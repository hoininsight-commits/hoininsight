from __future__ import annotations

import sys
import time
import os
import json
import traceback
from datetime import datetime
from pathlib import Path

from src.reporting.run_log import RunResult, write_run_log, append_observation_log
from src.utils.target_date import get_target_ymd, get_target_parts
from src.pipeline.run_collect import main as collect_main
from src.pipeline.run_normalize import main as normalize_main
from src.pipeline.run_anomaly import main as anomaly_main
from src.pipeline.run_topic import main as topic_main
from src.pipeline.run_topic_gate import main as gate_pipeline_main
from src.reporters.daily_report import write_daily_brief
from src.reporting.health import write_health
from src.validation.output_check import run_output_checks
from src.validation.schema_check import run_schema_checks

def _utc_now_stamp() -> str:
    # Use standardized YMD but append actual UTC time for high-res logs
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def _date_path_standardized() -> Path:
    y, m, d = get_target_parts()
    return Path("data") / "reports" / y / m / d

def main(target_categories: list[str] = None):
    started = _utc_now_stamp()
    start_time = time.time()
    status = "SUCCESS"
    details_lines = []
    check_lines = []
    checks_ok = False
    per_dataset = []

    try:
        details_lines.append("engine: start")
        print("engine: start", file=sys.stderr)
        
        collect_main(target_categories)
        details_lines.append("collect: ok")
        print("collect: ok", file=sys.stderr)
        
        normalize_main(target_categories)
        details_lines.append("normalize: ok")
        print("normalize: ok", file=sys.stderr)
        
        # --- Logic Layer ---
        from src.pipeline.derived_metrics_engine import run_derived_metrics
        run_derived_metrics(Path("."))
        details_lines.append("derived: ok")
        print("derived: ok", file=sys.stderr)
        # -------------------
        
        anomaly_main()
        details_lines.append("anomaly: ok")
        print("anomaly: ok", file=sys.stderr)

        topic_main()
        details_lines.append("topic: ok")
        print("topic: ok", file=sys.stderr)

        # [Phase 50] Anchor Engine (Economy Hunter Logic) - Strict 6-Step Enforcement
        from src.topics.anchor_engine.logic_core import AnchorEngine
        
        # Load Anomalies for Anchor Input
        anomalies_dir = Path("data/features/anomalies") / datetime.now().strftime("%Y/%m/%d")
        snapshots = []
        if anomalies_dir.exists():
            for f in anomalies_dir.glob("*.json"):
                try: 
                    payload = json.loads(f.read_text(encoding="utf-8"))
                    dataset_id = payload.get("dataset_id", f.stem) if isinstance(payload, dict) else f.stem
                    
                    if isinstance(payload, list):
                        for item in payload:
                            if isinstance(item, dict) and "dataset_id" not in item:
                                item["dataset_id"] = dataset_id
                        snapshots.extend(payload)
                    elif isinstance(payload, dict):
                        if "anomalies" in payload and isinstance(payload["anomalies"], list):
                             for item in payload["anomalies"]:
                                 if isinstance(item, dict) and "dataset_id" not in item:
                                     item["dataset_id"] = dataset_id
                             snapshots.extend(payload["anomalies"])
                        else:
                             if "dataset_id" not in payload:
                                 payload["dataset_id"] = dataset_id
                             snapshots.append(payload)
                except Exception as e:
                    print(f"Error loading {f}: {e}", file=sys.stderr)

        anchor_engine = AnchorEngine(Path("."))
        anchor_results = anchor_engine.run_analysis(snapshots)
        
        # Save Anchor Result
        anchor_out_dir = Path("data/topics/anchor") / datetime.now().strftime("%Y/%m/%d")
        anchor_out_dir.mkdir(parents=True, exist_ok=True)
        
        # Pick Best Anchor (First one for now, or sort by Level)
        # Sorting: L4 > L3 > L2
        anchor_results.sort(key=lambda x: {"L4": 3, "L3": 2, "L2": 1}.get(x.level, 0), reverse=True)
        
        if anchor_results:
            best_anchor = anchor_results[0]
            anchor_file = anchor_out_dir / "anchor_result.json"
            # Serialize
            import dataclasses
            with open(anchor_file, "w", encoding="utf-8") as f:
                json.dump(dataclasses.asdict(best_anchor), f, indent=2, ensure_ascii=False)
            print(f"[Anchor] Selected Best Logic: {best_anchor.anomaly_logic} ({best_anchor.level})", file=sys.stdout)
        else:
            print("[Anchor] No valid topic found matching Anchor Logic steps.", file=sys.stdout)

        details_lines.append("anchor_engine: ok")
        print("anchor_engine: ok", file=sys.stderr)

        # [Phase 50] Strict Topic Decision Gate (Engine 2)
        # 1. Ensure Data Snapshot (JSON) exists
        from src.reporters.data_snapshot import write_data_snapshot
        run_ymd = get_target_ymd()
        try:
            snapshot_path = write_data_snapshot(Path("."))
            details_lines.append(f"snapshot: ok ({snapshot_path})")
            print("snapshot: ok", file=sys.stderr)
        except Exception as e:
             print(f"snapshot: warn ({e})", file=sys.stderr)

        # [NEW] Step 41: Run Pick-Outcome Correlator (Accountability)
        from src.ops.pick_outcome_correlator import PickOutcomeCorrelator
        try:
            correlator = PickOutcomeCorrelator(Path("."))
            correlator.run(run_ymd)
            details_lines.append("pick_correlator: ok")
            print("pick_correlator: ok", file=sys.stderr)
        except Exception as e:
            print(f"pick_correlator: fail ({e})", file=sys.stderr)

        # 2. Run Gate Pipeline (Content Hook Logic)
        try:
            gate_pipeline_main(run_ymd)
            details_lines.append("topic_gate: ok")
            print("topic_gate: ok", file=sys.stderr)
        except Exception as e:
            print(f"topic_gate: fail ({e})", file=sys.stderr)

        # [NEW] Step 43 & 44: Auto Prioritization & Approval
        # These will be executed inside DecisionDashboard.build_dashboard_data
        # to ensure they have access to the fully ranked topics and shadow pool.
        
        # [NEW] Generate Decision Dashboard Markdown
        from src.reporters.decision_dashboard import DecisionDashboard
        try:
            dd = DecisionDashboard(Path("."))
            # Step 43/44 are now deeply integrated into build_dashboard_data
            dd_data = dd.build_dashboard_data(run_ymd)
            
            # Write auto_approved_today.json specifically if not already saved by dd
            # Actually, let's make sure AutoApprovalGate runs and saves.
            from src.ops.auto_approval_gate import AutoApprovalGate
            from src.ops.operator_decision_log import OperatorDecisionLog
            
            # We need the cards from dd_data
            ready_topics = [c for c in dd_data.get("cards", []) if c["status"] == "READY"]
            ap_data = dd_data.get("auto_priority", {})
            op_log = OperatorDecisionLog(Path("."))
            op_decisions = op_log.get_latest_decisions_map(run_ymd)
            
            aa_gate = AutoApprovalGate(Path("."))
            aa_data = aa_gate.run(run_ymd, ready_topics, ap_data, op_decisions)
            
            # [NEW] Step 45: Run Speak Bundle Exporter
            from src.ops.speak_bundle_exporter import SpeakBundleExporter
            try:
                exporter = SpeakBundleExporter(Path("."))
                exporter.run(run_ymd, dd_data.get("cards", []), aa_data)
                details_lines.append("speak_bundle: ok")
                print("speak_bundle: ok", file=sys.stderr)
            except Exception as e:
                print(f"speak_bundle: fail ({e})", file=sys.stderr)

            dd_md = dd.render_markdown(dd_data)
            
            y, m, d = get_target_parts()
            dd_path = Path("data/reports") / y / m / d / "decision_dashboard.md"
            dd_path.parent.mkdir(parents=True, exist_ok=True)
            dd_path.write_text(dd_md, encoding="utf-8")
            
            details_lines.append(f"decision_dashboard: ok | {dd_path.as_posix()}")
            print(f"decision_dashboard: ok", file=sys.stderr)
        except Exception as e:
            print(f"decision_dashboard: fail ({e})", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)

        # [Fixed] Ensure Final Decision Card is generated
        from src.decision.final_decision_card import main as decision_main
        decision_main()
        details_lines.append("decision: ok")
        print("decision: ok", file=sys.stderr)

        report_path = write_daily_brief(Path("."))
        details_lines.append(f"report: ok | {report_path.as_posix()}")
        print(f"report: ok | {report_path.as_posix()}", file=sys.stderr)

        chk = run_output_checks(Path("."), target_categories)
        check_lines = chk.lines
        per_dataset = chk.per_dataset
        checks_ok = chk.ok
        details_lines.extend(["checks:"] + chk.lines)
        if not chk.ok:
            # We print detailed validation errors to stderr
            for line in chk.lines:
                print(f"validation: {line}", file=sys.stderr)
            raise RuntimeError("output checks failed")

        sch = run_schema_checks(Path("."), target_categories)
        details_lines.extend(["schema_checks:"] + sch.lines)
        if not sch.ok:
            for line in sch.lines:
                print(f"schema: {line}", file=sys.stderr)
            raise RuntimeError("schema checks failed")

        details_lines.append("engine: done")
        print("engine: done", file=sys.stderr)
        
    except Exception as e:
        status = "FAIL"
        err_msg = f"error: {repr(e)}"
        details_lines.append(err_msg)
        # CRITICAL: Print error to stderr so it appears in CI logs
        print(err_msg, file=sys.stderr)
        traceback.print_exc(file=sys.stderr)

    health_path = write_health(Path("."), status=status, checks_ok=checks_ok, check_lines=check_lines, per_dataset=per_dataset)
    details_lines.append(f"health: {health_path.as_posix()}")

    # --- Batch Timing Verification (Ops) ---
    try:
        runtime_path = Path("data/ops/workflow_runtime_v1.json")
        if runtime_path.exists():
            ops_data = json.loads(runtime_path.read_text(encoding="utf-8"))
            # Detect workflow from env or assume standard based on category
            current_workflow = os.environ.get("GITHUB_WORKFLOW", "unknown_workflow")
            
            # Check if we can map categories to known workflows for local testing
            if current_workflow == "unknown_workflow":
                if target_categories and "CRYPTO" in target_categories: current_workflow = "pipeline_crypto.yml"
                elif target_categories and "FX_RATES" in target_categories: current_workflow = "pipeline_fx.yml"
                elif target_categories and "US_MARKETS" in target_categories: current_workflow = "pipeline_us_markets.yml"
                elif target_categories and "BACKFILL" in target_categories: current_workflow = "pipeline_backfill.yml"
            
            target_p95 = 300 # Default fallback
            for wf in ops_data["workflows"]:
                if wf["workflow"] == current_workflow or wf["workflow"] in current_workflow:
                    target_p95 = wf["p95_duration_sec"]
                    break
            
            actual_duration = round(time.time() - start_time, 2)
            if actual_duration <= target_p95:
                print(f"[VERIFY][OK] Workflow completed within expected duration ({target_p95}s)", file=sys.stdout)
            else:
                print(f"[VERIFY][WARN] Workflow exceeded expected duration (actual {actual_duration}s > p95 {target_p95}s)", file=sys.stdout)
    except Exception as e:
        print(f"[VERIFY][SKIP] Could not verify runtime: {e}", file=sys.stderr)
    # ----------------------------------------

    finished = _utc_now_stamp()
    report_dir = _date_path_standardized()
    result = RunResult(
        started_utc=started,
        finished_utc=finished,
        status=status,
        details="\n".join(details_lines),
    )
    log_path = write_run_log(report_dir, result)

    obs_line = f"- {finished} | engine_run | status={status} | run_log={log_path.as_posix()}\n"
    append_observation_log(Path("docs") / "OBSERVATION_LOG.md", obs_line)

    if status != "SUCCESS":
        sys.exit(1)

if __name__ == "__main__":
    main()
