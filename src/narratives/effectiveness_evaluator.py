#!/usr/bin/env python3
"""
Phase 34: Approved Change Effectiveness Evaluator

측정/기록/표시만 수행. 자동 수정/롤백 금지.
"""
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional


def load_applied_events(base_dir: Path, lookback_days: int = 30) -> List[Dict[str, Any]]:
    """Load applied events from the last N days."""
    events = []
    today = datetime.utcnow().date()
    
    for i in range(lookback_days):
        check_date = today - timedelta(days=i)
        ymd_path = check_date.strftime("%Y/%m/%d")
        
        # Check applied_summary.json
        summary_path = base_dir / "data" / "narratives" / "applied" / ymd_path / "applied_summary.json"
        if summary_path.exists():
            try:
                data = json.loads(summary_path.read_text(encoding="utf-8"))
                events.append({
                    "event_id": f"applied_{check_date.strftime('%Y%m%d')}",
                    "applied_at": check_date.strftime("%Y-%m-%d"),
                    "apply_scope": data.get("apply_scope", {}),
                    "source_file": str(summary_path)
                })
            except:
                pass
    
    return events


def calculate_pipeline_reliability(base_dir: Path, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """Calculate pipeline success rate in date range."""
    total_days = 0
    success_days = 0
    fail_count = 0
    
    current = start_date
    while current <= end_date:
        ymd_path = current.strftime("%Y/%m/%d")
        
        # Check daily_brief.md for status
        brief_path = base_dir / "data" / "reports" / ymd_path / "daily_brief.md"
        if brief_path.exists():
            total_days += 1
            try:
                content = brief_path.read_text(encoding="utf-8")
                # Simple heuristic: if brief exists and has content, consider success
                if len(content) > 100:
                    success_days += 1
            except:
                fail_count += 1
        
        current += timedelta(days=1)
    
    success_rate = success_days / total_days if total_days > 0 else None
    return {
        "success_rate": success_rate,
        "fail_count": fail_count,
        "days_used": total_days
    }


def calculate_topics_count(base_dir: Path, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """Calculate average topics count in date range."""
    topics_counts = []
    meta_counts = []
    
    current = start_date
    while current <= end_date:
        ymd_path = current.strftime("%Y/%m/%d")
        
        # Check topics
        topics_dir = base_dir / "data" / "topics" / ymd_path
        if topics_dir.exists():
            topic_files = list(topics_dir.glob("*.json"))
            topics_counts.append(len(topic_files))
        
        # Check meta_topics
        meta_path = base_dir / "data" / "meta_topics" / ymd_path / "meta_topics.json"
        if meta_path.exists():
            try:
                meta_data = json.loads(meta_path.read_text(encoding="utf-8"))
                meta_counts.append(len(meta_data.get("meta_topics", [])))
            except:
                pass
        
        current += timedelta(days=1)
    
    return {
        "topics_avg": sum(topics_counts) / len(topics_counts) if topics_counts else None,
        "meta_topics_avg": sum(meta_counts) / len(meta_counts) if meta_counts else None,
        "days_used": len(topics_counts)
    }


def calculate_confidence_distribution(base_dir: Path, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """Calculate regime confidence distribution in date range."""
    confidence_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    total = 0
    
    current = start_date
    while current <= end_date:
        ymd_path = current.strftime("%Y/%m/%d")
        
        # Check daily_brief.md for confidence
        brief_path = base_dir / "data" / "reports" / ymd_path / "daily_brief.md"
        if brief_path.exists():
            try:
                content = brief_path.read_text(encoding="utf-8")
                if "Confidence: HIGH" in content:
                    confidence_counts["HIGH"] += 1
                    total += 1
                elif "Confidence: MEDIUM" in content:
                    confidence_counts["MEDIUM"] += 1
                    total += 1
                elif "Confidence: LOW" in content:
                    confidence_counts["LOW"] += 1
                    total += 1
            except:
                pass
        
        current += timedelta(days=1)
    
    high_share = confidence_counts["HIGH"] / total if total > 0 else None
    return {
        "high_share": high_share,
        "distribution": confidence_counts,
        "days_used": total
    }


def calculate_regime_flips(base_dir: Path, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """Calculate regime flip count in date range."""
    regimes = []
    
    current = start_date
    while current <= end_date:
        ymd_path = current.strftime("%Y/%m/%d")
        
        # Check daily_brief.md for regime
        brief_path = base_dir / "data" / "reports" / ymd_path / "daily_brief.md"
        if brief_path.exists():
            try:
                content = brief_path.read_text(encoding="utf-8")
                # Extract regime (simple heuristic)
                for line in content.split("\n"):
                    if line.startswith("Regime:"):
                        regime = line.split("Regime:")[1].strip()
                        regimes.append(regime)
                        break
            except:
                pass
        
        current += timedelta(days=1)
    
    # Count flips
    flip_count = 0
    for i in range(1, len(regimes)):
        if regimes[i] != regimes[i-1]:
            flip_count += 1
    
    return {
        "flip_count": flip_count,
        "days_used": len(regimes)
    }


def calculate_drift_changes(base_dir: Path, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """Calculate narrative drift state changes in date range."""
    # Placeholder: would need actual drift tracking
    # For now, return null
    return {
        "change_count": None,
        "days_used": 0
    }


def evaluate_event_effectiveness(base_dir: Path, event: Dict[str, Any], window_days: int = 7) -> Dict[str, Any]:
    """Evaluate effectiveness for a single applied event."""
    applied_date = datetime.strptime(event["applied_at"], "%Y-%m-%d").date()
    
    # Define windows
    pre_start = applied_date - timedelta(days=window_days)
    pre_end = applied_date - timedelta(days=1)
    post_start = applied_date + timedelta(days=1)
    post_end = applied_date + timedelta(days=window_days)
    
    # Calculate metrics
    pre_reliability = calculate_pipeline_reliability(base_dir, pre_start, pre_end)
    post_reliability = calculate_pipeline_reliability(base_dir, post_start, post_end)
    
    pre_topics = calculate_topics_count(base_dir, pre_start, pre_end)
    post_topics = calculate_topics_count(base_dir, post_start, post_end)
    
    pre_confidence = calculate_confidence_distribution(base_dir, pre_start, pre_end)
    post_confidence = calculate_confidence_distribution(base_dir, post_start, post_end)
    
    pre_flips = calculate_regime_flips(base_dir, pre_start, pre_end)
    post_flips = calculate_regime_flips(base_dir, post_start, post_end)
    
    pre_drift = calculate_drift_changes(base_dir, pre_start, pre_end)
    post_drift = calculate_drift_changes(base_dir, post_start, post_end)
    
    # Build metrics
    metrics = {
        "pipeline_reliability": {
            "pre_success_rate": pre_reliability["success_rate"],
            "post_success_rate": post_reliability["success_rate"],
            "delta": (post_reliability["success_rate"] - pre_reliability["success_rate"]) 
                     if pre_reliability["success_rate"] is not None and post_reliability["success_rate"] is not None 
                     else None
        },
        "core_fail_count": {
            "pre": pre_reliability["fail_count"],
            "post": post_reliability["fail_count"],
            "delta": post_reliability["fail_count"] - pre_reliability["fail_count"]
        },
        "topics_count_avg": {
            "pre": pre_topics["topics_avg"],
            "post": post_topics["topics_avg"],
            "delta": (post_topics["topics_avg"] - pre_topics["topics_avg"]) 
                     if pre_topics["topics_avg"] is not None and post_topics["topics_avg"] is not None 
                     else None
        },
        "meta_topics_count_avg": {
            "pre": pre_topics["meta_topics_avg"],
            "post": post_topics["meta_topics_avg"],
            "delta": (post_topics["meta_topics_avg"] - pre_topics["meta_topics_avg"]) 
                     if pre_topics["meta_topics_avg"] is not None and post_topics["meta_topics_avg"] is not None 
                     else None
        },
        "confidence_high_share": {
            "pre": pre_confidence["high_share"],
            "post": post_confidence["high_share"],
            "delta": (post_confidence["high_share"] - pre_confidence["high_share"]) 
                     if pre_confidence["high_share"] is not None and post_confidence["high_share"] is not None 
                     else None
        },
        "regime_flip_count": {
            "pre": pre_flips["flip_count"],
            "post": post_flips["flip_count"],
            "delta": post_flips["flip_count"] - pre_flips["flip_count"]
        },
        "drift_state_changes": {
            "pre": pre_drift["change_count"],
            "post": post_drift["change_count"],
            "delta": None
        }
    }
    
    data_quality = {
        "pre_days_used": min(pre_reliability["days_used"], pre_topics["days_used"], pre_confidence["days_used"]),
        "post_days_used": min(post_reliability["days_used"], post_topics["days_used"], post_confidence["days_used"]),
        "notes": "soft-fail applied" if (pre_reliability["days_used"] < window_days or post_reliability["days_used"] < window_days) else "complete"
    }
    
    return {
        "event_id": event["event_id"],
        "applied_at": event["applied_at"],
        "apply_scope": event["apply_scope"],
        "metrics": metrics,
        "data_quality": data_quality
    }


def main():
    """Main entry point for effectiveness evaluation."""
    base_dir = Path(__file__).parent.parent.parent
    
    # Configuration
    lookback_days = 30
    window_days = 7
    
    # Load applied events
    events = load_applied_events(base_dir, lookback_days)
    
    # Evaluate each event
    evaluated_events = []
    for event in events:
        try:
            result = evaluate_event_effectiveness(base_dir, event, window_days)
            evaluated_events.append(result)
        except Exception as e:
            print(f"[WARN] Failed to evaluate event {event['event_id']}: {e}")
            continue
    
    # Build output
    output = {
        "effectiveness_version": "phase34_v1",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "lookback_days": lookback_days,
        "window_days": window_days,
        "events": evaluated_events
    }
    
    # Save output
    ymd = datetime.utcnow().strftime("%Y/%m/%d")
    output_dir = base_dir / "data" / "narratives" / "effectiveness" / ymd
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / "effectiveness.json"
    output_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    
    print(f"✓ Effectiveness evaluation complete: {output_path}")
    print(f"  - Evaluated {len(evaluated_events)} events")


if __name__ == "__main__":
    main()
