def build_ui_today(brief):
    """
    Builds the 'ui_today' block for the Operator Dashboard.
    """
    radar = brief.get("market_radar", {})
    decision = brief.get("investment_decision", {})
    narrative = brief.get("narrative", {})
    
    # Extract confidence safely
    conf_obj = decision.get("confidence", {}).get("value", {})
    if isinstance(conf_obj, dict):
        confidence_val = conf_obj.get("final_confidence", 0)
    else:
        confidence_val = conf_obj or 0
        
    return {
        "title": brief.get("display_title") or brief.get("core_theme") or "미확인 테마",
        "why_now": narrative.get("explanation", "내용 없음"),
        "theme_type": brief.get("theme_type", "UNKNOWN"),
        "evolution_stage": radar.get("evolution_stage", "N/A"),
        "intensity_label": radar.get("momentum_state") or radar.get("intensity_label") or "N/A",
        "action": decision.get("action", {}).get("value", "WATCH"),
        "confidence_pct": round(confidence_val * 100),
        "top_stocks": brief.get("ui_top_stocks", [])[:3],
        "market_context": brief.get("market_context") or "AI Power Constraint 테마가 시장의 핵심 동력으로 부상..."
    }


def build_ui_history(validation_tracking):
    """
    Builds the 'ui_history' array for the Operator Dashboard.
    """
    result = []
    # Show latest first
    for d in reversed(validation_tracking):
        result.append({
            "date": d.get("date", "Unknown"),
            "title": d.get("core_theme", "Unknown"),
            "action": d.get("action", "WATCH"),
            "confidence_pct": round(d.get("confidence", 0) * 100),
            "alignment_pct": round(d.get("outcome_alignment", 0) * 100),
            "result_label": "성공" if d.get("failure_type") == "SUCCESS" else "보정 필요",
            "result_status": d.get("failure_type", "UNKNOWN")
        })
    return result


def build_ui_radar(validation_tracking, stats):
    """
    Builds the 'ui_radar' block for the Operator Dashboard.
    """
    # Get last 5 for recent topics
    recent_raw = validation_tracking[-5:]
    recent_processed = []
    for x in reversed(recent_raw):
        recent_processed.append({
            "date": x.get("date"),
            "title": x.get("core_theme"),
            "action": x.get("action"),
            "status": x.get("failure_type")
        })

    after_stats = stats.get("after", {})
    return {
        "avg_alignment_pct": round(after_stats.get("avg_alignment", 0) * 100),
        "avg_hit_ratio_pct": round(after_stats.get("avg_hit_ratio", 0) * 100),
        "sample_size": after_stats.get("count", 0),
        "recent_topics": recent_processed
    }


def build_ui_engine_status(stats):
    """
    Builds the 'ui_engine_status' block for the Operator Dashboard.
    """
    after_stats = stats.get("after", {})
    count = after_stats.get("count", 0)
    alignment_pct = round(after_stats.get("avg_alignment", 0) * 100)
    hit_ratio_pct = round(after_stats.get("avg_hit_ratio", 0) * 100)

    if count < 10:
        status = "EARLY_PRODUCTION"
        warning = "초기 운영 단계 — 표본 수 확대 필요"
    else:
        status = "STABLE_OPERATION"
        warning = ""

    return {
        "status": status,
        "alignment_pct": alignment_pct,
        "hit_ratio_pct": hit_ratio_pct,
        "sample_size": count,
        "warning": warning
    }
